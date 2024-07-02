# azure_pim
PIM through Azure portal is slow and cannot be automated. This repo tries to implement a CLI version that is based on mainly REST API and AZCLI.
This code borrowed insights from other repos: https://github.com/jlester-msft/azure_elevation_script and https://github.com/demoray/azure-pim-cli but it's more lightweighted. It does not have ability to customize but since it is Python and it's short, you can customize it anyway you wanted :).

```
pim.py
List all eligible scope and roles, and wether it's activated

pim.py <scope_name_1> <scope_name_2>
Send requests to elevate these two scopes
```

For example, if I need to use GCR's workspace gcrllama2ws to submit Singularity jobs, I will run
```
pim.py gcrllama2ws msrresrchvc
```

You need to have AzCLI installed. You still need to `az login` manually and the script cannot run without your access token. I did not include a requirements.txt but it's not hard to figure out by reading exception messages.
