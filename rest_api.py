import json
import uuid
from datetime import datetime, timedelta
from enum import Enum

import requests
from pytz import timezone


class RoleAssignmentScheduleRequestType(Enum):
    SelfActivate = "SelfActivate"
    SelfDeactivate = "SelfDeactivate"
    AdminAssign  = "AdminAssign"
    AdminRemove = "AdminRemove"
    # more at https://learn.microsoft.com/en-us/rest/api/authorization/role-assignment-schedule-requests/create?view=rest-authorization-2020-10-01&tabs=HTTP#requesttype

def list_eligibility(access_token):
    """documenation: https://learn.microsoft.com/en-us/rest/api/authorization/privileged-role-eligibility-rest-sample?view=rest-authorization-2022-08-01-preview#list-eligible-assignments"""
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
    """documenation: https://learn.microsoft.com/en-us/rest/api/authorization/privileged-role-assignment-rest-sample?view=rest-authorization-2022-08-01-preview#list-active-assignments"""
    url = 'https://management.azure.com/providers/Microsoft.Authorization/roleAssignmentScheduleInstances?api-version=2020-10-01&$filter=asTarget()'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)["value"]
    raise Exception(f"Failed to list activated assignment!\nstatus_code={response.status_code}\nresponse={response.text}\n")


def activate_role(scope_id, role_id, user_id, headers):
    return create_role_assignment_schedule_request(
        RoleAssignmentScheduleRequestType.SelfActivate,
        scope_id, role_id, user_id, headers)


def deactivate_role(scope_id, role_id, user_id, headers):
    return create_role_assignment_schedule_request(
        RoleAssignmentScheduleRequestType.SelfDeactivate,
        scope_id, role_id, user_id, headers)


def assign_active_role(scope_id, role_id, user_id, headers):
    return create_role_assignment_schedule_request(
        RoleAssignmentScheduleRequestType.AdminAssign,
        scope_id, role_id, user_id, headers
    )


def remove_active_role(scope_id, role_id, user_id, headers):
    return create_role_assignment_schedule_request(
        RoleAssignmentScheduleRequestType.AdminRemove,
        scope_id, role_id, user_id, headers
    )

"""
Create role assignment through PIM
https://learn.microsoft.com/en-us/rest/api/authorization/role-assignment-schedule-requests?view=rest-authorization-2020-10-01
"""

def create_role_assignment_schedule_request(
        request_type :RoleAssignmentScheduleRequestType,
        scope_id, role_id, user_id, headers):
    request_uuid = str(uuid.uuid4())  # a unique GUI for the request
    url = f"https://management.azure.com/{scope_id}/providers/Microsoft.Authorization/roleAssignmentScheduleRequests/{request_uuid}?api-version=2020-10-01"

    # TODO: does it matter whether start time is in past after submission?
    start_time = datetime.now(timezone('America/Los_Angeles')) + timedelta(seconds=10)
    offset_six_months = start_time + timedelta(days=179)

    if request_type == RoleAssignmentScheduleRequestType.AdminAssign:
        schedule_info = {
            "StartDateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "Expiration": {
                "Type": "AfterDateTime",
                "EndDateTime": offset_six_months.strftime("%Y-%m-%dT%H:%M:%S"),
                "Duration": None
            }
        }
    elif request_type == RoleAssignmentScheduleRequestType.SelfActivate:
        schedule_info = {
            "StartDateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "Expiration": {
                "Type": "AfterDuration",
                "EndDateTime": None,
                "Duration": "PT8H"
            }
        }
    elif request_type in [RoleAssignmentScheduleRequestType.SelfDeactivate, RoleAssignmentScheduleRequestType.AdminRemove]:
        schedule_info = None
    else:
        raise NotImplementedError(f"request_type={request_type} is not implemented yet.")

    payload = {
        "Properties": {
            "PrincipalId": user_id,
            "RoleDefinitionId": role_id,
            "RequestType": request_type.value,
            "Justification": "auto generated",
        }        
    }

    if schedule_info:
        payload["Properties"]["ScheduleInfo"] = schedule_info

    response = requests.put(url, json=payload, headers=headers)
    if response.status_code in [201]:
        return json.loads(response.text)
    
    raise Exception(f"Request failed!\nstatus_code={response.status_code}\nresponse={response.text}\n"
                    f"\nPUT {url}\npayload={json.dumps(payload, indent=2)}\n")
