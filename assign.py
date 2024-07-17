import argparse
import json

from az_cli import (
    CommandFailedException,
    get_access_token,
    get_resource_group_ids_by_name,
    get_resource_ids_by_name,
    get_role_ids_by_name,
    get_subcription_id_by_name,
    return_single_item_from_multiple_choices,
)
from rest_api import assign_active_role, remove_active_role


def init():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="""
Complete a list of role assignment tasks via REST API. Each line of the input file is a task
in JSON format. For example:
{
    "assignee_id": "000000-967f-48d6-8180-1e674161278e",
    "scope_name": "Project Echelon",
    "role_name": "Storage Blob Data Contributor",
    "subscription_name": "Project Echelon"
}

assignee_id:
    it is a required field for now, because only managed devices can retrieve assignee ID
    by assignee name (e.g. "Mei Yang") via Microsoft Graph.
scope_name or scope_id:
    one of them has to be provided. If both are provided, scope_id will be used.
role_name or role_id:
    one of them has to be provided. If both are provided, role_id will be used.
    If role_name is provided, it must be case SENSITIVE.
subscription_name or subscription_id:
    this is the subscription of scope and role. If neither is provided, the selected subscription
    via `az account show` is used. If both are provided, subscription_id will be used.

""")
    parser.add_argument("tasks", type=str, help="A JSON line file containing a list of tasks to complete.", default=None)
    return parser.parse_args()


def load_tasks(filename):
    with open(filename, 'r') as f:
        for line in f:
            task = json.loads(line)
            # we need assignee
            if 'assignee_name' not in task and 'assignee_id' not in task:
                print(f"Skip task without 'assignee_name' or 'assignee_id' field:\n", task)
            elif 'scope_name' not in task and 'scope_id' not in task:
                print(f"Skip task without 'scope_name' or 'scopoe_id' field:\n", task)
            elif 'role_name' not in task and 'role_id' not in task:
                print(f"Skip task without 'role_name' or 'role_id' field:\n", task)
            else:
                yield task


def update_subscription_id(task):
    if 'subscription_id' in task:
        return
    elif 'subscription_name' in task:
        sid = get_subcription_id_by_name(task['subscription_name'])
        if sid:
            task['subscription_id'] = sid
            return
        else:
            raise ValueError(f"Cannot find subscription with name: {task['subscription_name']}")
    else:
        default_sid = get_subcription_id_by_name()
        task['subscription_id'] = default_sid
        return


def update_assignee_id(task):
    if 'assignee_id' in task:
        return
    
    if 'assignee_name' in task:
        raise NotImplementedError("Assignee name is not supported at the moment.")
    
    raise ValueError("No assignee name or ID provided.")


def update_scope_id(task):
    if 'scope_id' in task:
        return
    
    candidates = []
    if 'scope_name' in task:
        try:
            sid = get_subcription_id_by_name(task['scope_name'])
            candidates.append(f"subscriptions/{sid}")
        except CommandFailedException:
            pass

        candidates += get_resource_group_ids_by_name(task['scope_name'], task['subscription_id'])
        candidates += get_resource_ids_by_name(task['scope_name'], task['subscription_id'])
        if len(candidates) == 0:
            raise ValueError("Cannot find subcription/resource group/resource with name (case insensitive): " + task['scope_name'])
        task['scope_id'] = return_single_item_from_multiple_choices(candidates)
        return
    
    raise ValueError("No scope name or ID provided.")


def update_role_id(task):
    if 'role_id' in task:
        return
    
    if 'role_name' in task:        
        candidates = get_role_ids_by_name(task['role_name'], task['subscription_id'])
        if len(candidates) == 0:
            raise ValueError("Cannot find role with name (case sensitive): " + task['role_name'])
        task['role_id'] = return_single_item_from_multiple_choices(candidates)


if __name__ == "__main__":
    args = init()

    # get access token
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }

    for task in load_tasks(args.tasks):            
        update_subscription_id(task)  # TODO: too slow to process all subscriptions            
        update_assignee_id(task)  # TODO: does not support assignee name
        update_scope_id(task)
        update_role_id(task)

        rst = assign_active_role(task['scope_id'], task['role_id'], task['assignee_id'], headers)
        #rst = remove_active_role(task['scope_id'], task['role_id'], task['assignee_id'], headers)

        scope_name = rst['properties']['expandedProperties']['scope']['displayName']
        role_name = rst['properties']['expandedProperties']['roleDefinition']['displayName']
        user_name = rst['properties']['expandedProperties']['principal']['displayName']
        status = rst['properties']['status']
        print(f"{scope_name} --- {role_name} --- {user_name} --- {status}")
