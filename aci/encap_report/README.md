## encap_report

#### Description
List all used encap-vlans used in the fabric.

### Installation

#### Install Python virutal environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pip setuptools --upgrade
pip install -r requirements.txt
```

#### Set environment variables
```bash
export APIC_HOST=<API IP or hostname>
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

Running the script will print the encap report as a table to the shell, in addition the report is stored in JSON format to file (```encap_report.json```) in the current working directory.




