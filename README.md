# azure_pim

Manage roles through PIM app at Azure portal is slow and cannot be automated. This repo tries to implement a CLI version that is based mainly on REST APIs and AZCLI.
This code borrowed insights from other repos: https://github.com/jlester-msft/azure_elevation_script and https://github.com/demoray/azure-pim-cli but is more lightweighted. It focuses on only two functions: activate eligible roles and grant active roles. This code is short and easy to cutomize to meet your specific needs.

You need to have AzCLI installed. You need to `az login` manually as the script cannot run without your access token. I did not include a requirements.txt but it's not hard to figure out by reading exception messages. I remember I had to install these packages:

```
PyJWT
requests
pytz
```

## Activate eligible roles
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

It is possible to change 'start_time' to schedule your PIMs in a future time. For example, to activate msrresrchvc every 8 hours so that your jobs in queue would not lose PIM during waiting. But check with your VC admin for permission.

## Grant active roles
All AML workspaces need keyless access to storage accounts now. Assume you have a AzureML workspace "myworkspace" and a storage account "mystorage". If you have "Owner" or "User Access Administrator" role over mystorage, you can give myworkspace read/write permission over mystorage. To do so, you create a JSON line file task.jsonl as follows and run assign.py with it. You can have more than one task in task.jsonl.

```
task.jsonl:
{"assignee_id": "<guid-identity-of-myworkspace>", "scope_name": "mystorage", "role_name": "Storage Blob Data Contributor", "subscription_name": "subscription name for mystorage"}

python assign.py task.jsonl
```

Note that due to restriction of Microsoft Graph, some devices cannot retrieve identity of "myworkspace" programmingly. The current implementation require you to go to Azure portal -> Microsoft Entra ID, search for "myworkspace" and copy "object ID" to fill in "assignee_id" field.