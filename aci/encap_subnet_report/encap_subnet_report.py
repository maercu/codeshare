import ipaddress
import json
import os
import re
import aciClient
from tabulate import tabulate

# globals
aclient = aciClient.ACI(os.getenv("APIC_HOST"), os.getenv("APIC_USER"), os.getenv("APIC_PASS"))

def get_attrs_from_mo(mo_class, *attrs):
    result = []
    aclient.login()
    mos = aclient.getJson(f"class/{mo_class}.json")

    for mo in mos:
        result.append([mo.get(mo_class).get("attributes").get(attr) for attr in attrs])
    
    aclient.logout()
    return result


def extract_mo_from_path(target, recomp, dn_encap):
    for dn, encap in dn_encap:
        mo = recomp.match(dn).group(1)
        vlan = encap.split("-")[1]
        target.setdefault(vlan, set())
        target[vlan].add(mo)
    
    return target


if __name__ == "__main__":
    encap_to_mo = {}

    stbinds_dn_encap = get_attrs_from_mo("fvRsPathAtt", "dn", "encap")
    recomp_stbinds = re.compile(r"(uni/tn-.*/ap-.*/epg-.*)/rspathAtt-.*")
    encap_to_mo = extract_mo_from_path(encap_to_mo, recomp_stbinds, stbinds_dn_encap)

    vmmports_dn_encap = get_attrs_from_mo("vmmEpPD", "epgPKey", "encap")
    recomp_vmmports = re.compile(r"(.*)")
    encap_to_mo = extract_mo_from_path(encap_to_mo, recomp_vmmports, vmmports_dn_encap)

    l3extpaths_dn_encap = get_attrs_from_mo("l3extRsPathL3OutAtt", "dn", "encap")
    recomp_l3extpaths = re.compile(r"(uni/tn-.*/out-.*)/lnodep-.*")
    encap_to_mo = extract_mo_from_path(encap_to_mo, recomp_l3extpaths, l3extpaths_dn_encap)

    encap_to_mo = dict(sorted({k: list(v) for k, v in encap_to_mo.items()}.items()))

    epg2bd = {}
    for dn, bd in get_attrs_from_mo("fvRsBd", "dn", "tDn"):
        if re.match(r"(uni/tn-.*/ap-.*/epg-.*)/rsbd", dn):
            epg2bd[re.match(r"(uni/tn-.*/ap-.*/epg-.*)/rsbd", dn).group(1)] = bd

    bd2subnets = {}
    for dn, ip in get_attrs_from_mo("fvSubnet", "dn", "ip"):
        bdmatch = re.match(r"(uni/tn-.*/BD-.*)/subnet-\[(.*)\]", dn)
        if bdmatch:
            bd2subnets.setdefault(bdmatch.group(1), [])
            bd2subnets[bdmatch.group(1)].append(str(ipaddress.IPv4Network(ip, strict=False)))

    epg2subnets = {}
    for epg, bd in epg2bd.items():
        if bd2subnets.get(bd):
            epg2subnets[epg] = bd2subnets.get(bd)

 
    encap2l3Subnets = {}
    aclient.login()
    l3paths = aclient.getJson("class/l3extRsPathL3OutAtt.json?rsp-subtree=children&rsp-subtree-class=l3extMember")
    for l3path in l3paths:
        encap = l3path.get("l3extRsPathL3OutAtt").get("attributes").get("encap").split("-")[1]
        encap2l3Subnets.setdefault(encap, set())
        ip = l3path.get("l3extRsPathL3OutAtt").get("attributes").get("addr")
        
        if ip != "0.0.0.0":
            encap2l3Subnets[encap].add(str(ipaddress.IPv4Network(ip, strict=False)))
        
        if l3path.get("l3extRsPathL3OutAtt").get("children"):
            for member in l3path.get("l3extRsPathL3OutAtt").get("children"):
                memberip = member.get("l3extMember").get("attributes").get("addr")
                encap2l3Subnets[encap].add(str(ipaddress.IPv4Network(memberip, strict=False)))

    aclient.logout()

    encap2l3Subnets = dict(sorted({k: list(v) for k, v in encap2l3Subnets.items()}.items()))

    final_report ={}
    for vlan, mos in encap_to_mo.items():
        subnets = encap2l3Subnets.get(vlan, [])
        for mo in mos:
            if epg2subnets.get(mo):
                subnets += epg2subnets.get(mo)
    
        final_report[vlan] = {
            "encap": vlan,
            "objects": sorted(mos),
            "subnets": sorted(subnets)
        }

    
    #print(json.dumps(final_report, indent=1))
    table_data = [[v.get("encap"), "\n".join(v.get("objects")), "\n".join(v.get("subnets"))] for v in final_report.values()]
    print(tabulate(table_data, headers=["ENCAP", "OBJECTS", "SUBNETS"], tablefmt="grid"))
    #print(tabulate(table_data, headers=["ENCAP", "OBJECTS", "SUBNETS"]))