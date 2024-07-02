import json
import uuid
from datetime import datetime, timedelta

import requests
from pytz import timezone


def list_eligibility(access_token):
    url = 'https://management.azure.com/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&$filter=asTarget()'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)["value"]
    raise Exception(f"Failed to list eligibility!\nstatus_code={response.status_code}\nresponse={response.text}\n")


def list_activated(access_token):
    url =      'https://management.azure.com/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&$filter=asTarget()'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)["value"]
    raise Exception(f"Failed to list activated assignment!\nstatus_code={response.status_code}\nresponse={response.text}\n")


def activate_scope(scope_name, scope_id, role_id, user_id, headers, comment=None):
    if not comment:
        comment = f"Need access to {scope_name}"

    request_uuid = str(uuid.uuid4())  # a unique GUI for the request
    url = f"https://management.azure.com/{scope_id}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/{request_uuid}?api-version=2020-10-01"

    # TODO: does it matter whether start time is in past after submission?
    start_time = datetime.now(timezone('America/Los_Angeles')) + timedelta(seconds=10)

    payload = {
        "Properties": {
            "RoleDefinitionId": role_id,
            "PrincipalId": user_id,
            "RequestType": "SelfActivate",
            "Justification": comment,
            "ScheduleInfo": {
                "StartDateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "Expiration": {
                    "Type": "AfterDuration",
                    "EndDateTime": None,
                    "Duration": "PT8H"
                }
            },
        }
    }

    response = requests.put(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        return json.loads(response.text)
    
    raise Exception(f"Activation request failed!\nstatus_code={response.status_code}\nresponse={response.text}\n")


def assign_role(user_id, scope_id, role_id, headers):
    '''documenation: https://learn.microsoft.com/en-us/rest/api/authorization/role-assignments/create?view=rest-authorization-2022-04-01&tabs=Python'''
    if not comment:
        comment = f"Add role {role_id}"

    request_uuid = str(uuid.uuid4())  # a unique GUI for the request
    url = f"https://management.azure.com/{scope_id}/providers/Microsoft.Authorization/roleAssignments/{request_uuid}?api-version=2022-04-01"

    payload = {
        "properties": {
            "roleDefinitionId": role_id,
            "principalId": user_id,
            "principalType": "User",
        },
    }

    response = requests.put(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        return json.loads(response.text)
    
    raise Exception(f"Activation request failed!\nstatus_code={response.status_code}\nresponse={response.text}\n")
