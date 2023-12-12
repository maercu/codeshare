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
    
    l3extpaths_dn_encap = get_attrs_from_mo("l3extRsPathL3OutAtt", "dn", "encap")
    recomp_l3extpaths = re.compile(r"(uni/tn-.*/out-.*)/lnodep-.*")
    encap_to_mo = extract_mo_from_path(encap_to_mo, recomp_l3extpaths, l3extpaths_dn_encap)

    encap_to_mo = dict(sorted({k: list(v) for k, v in encap_to_mo.items()}.items()))
    print(json.dumps(encap_to_mo, indent=1))

    table_data = [[k, "\n".join(v)] for k, v in encap_to_mo.items()]
    print(tabulate(table_data, headers=["ENCAP", "OBJECTS"], tablefmt="grid"))

    with open("encap_report.json", "w") as fo:
        json.dump(encap_to_mo, fo, indent=1)

