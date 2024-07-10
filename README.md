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

You need to have AzCLI installed. You still need to `az login` manually and the script cannot run without your access token. I did not include a requirements.txt but it's not hard to figure out by reading exception messages. I remember I had to install these packages:

```
PyJWT
requests
pytz
```

You may update 'start_time' in request to schedule your PIMs in future times. For example, every 7.5 hours for msrresrchvc so that your jobs in queue would not lose PIM during waiting. But check with your VC admin for permission.

Similarly, assigning roles through PIM is also slow. You can do the job with assign.py. For example, you have a AzureML workspace "myworkspace" and a storage account "mystorage" and you want myworkspace to read/write mystorage.
You need to assign the role "Storage Blob Data Contributor" (case sensitive) as follows:
```
python assign.py mystorage "Storage Blob Data Contributor" myworkspace
```

Note that the script assumes mystorage and myworkspace are in the same subscription "mysubscription" and you have chosen mysubscription as the default one. If not, you can use the optional parameter --subscription_name
```
python assign.py mystorage "Storage Blob Data Contributor" myworkspace --subscription_name mysubscription
```
