# azure_pim
PIM through Azure portal is slow and cannot be automated. This repo tries to implement a CLI version that is based on mainly REST API and AZCLI.
This code borrowed insights from other repos: https://github.com/jlester-msft/azure_elevation_script and https://github.com/demoray/azure-pim-cli

```
pim.py
List all eligible scope and roles, and wether it's activated

pim.py <scope_name_1> <scope_name_2>
Send requests to elevate these two scopes
```
