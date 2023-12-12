## encap_report

#### Description
Reports all encap-vlans used in the fabric.

### Installation

#### Clone repo and install Python virutal environment
```bash
git clone https://github.com/maercu/codeshare.git
cd codeshare/aci/encap_report

python3 -m venv .venv
source .venv/bin/activate
pip install pip setuptools --upgrade
pip install -r requirements.txt
```

#### Set environment variables
```bash
export APIC_HOST=<APIC IP or hostname>
export APIC_USER=<APIC Username>
export APIC_PASS=<APIC Password>

# Example
# export APIC_HOST=192.168.1.84
# export APIC_USER=admin
# export APIC_PASS=superSecretPassword
```

### Usage

```bash
python encap_report.py
```

Running the script will print the encap report as a table to the shell, in addition the report is stored in JSON format to a file (```encap_report.json```) in the current working directory.




