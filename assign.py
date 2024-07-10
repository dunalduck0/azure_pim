import argparse

from az_cli import (
    get_access_token,
    get_resource,
    get_resource_group,
    get_role,
    get_service_principal,
    get_signed_in_user,
    get_subcription,
    return_single_item_from_multiple_choices,
)
from rest_api import assign_role


def init():
    parser = argparse.ArgumentParser(description="Assign a <role> to a <target> identity over a <scope>.\nIf --target_name is not specified, the signed-in user is assumed to be the target.")
    parser.add_argument("scope_name", type=str, help="The display name of the scope, e.g. 'gcrllama2ws'")
    parser.add_argument("role_name", type=str, help="The display name of the role, e.g. 'Storage Blob Data Contributor'")
    parser.add_argument("target_name", type=str, default=None)
    parser.add_argument("--subscription_name", type=str, default=None, help="The display name of the subscription, e.g. 'deep learning group'")
    return parser.parse_args()


if __name__ == "__main__":
    args = init()

    # get access token
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }
    
    # TODO: too slow to process all subscriptions
    subscription = get_subcription(args.subscription_name)
    print(f"Will use the below subscription below. Change subscription using --subscription_name.\n{subscription}")

    # find scope by name matching
    candidates = []
    if args.scope_name == subscription['name']:
        candidates.append('/subscriptions/' + subscription['id'])
    candidates += get_resource_group(args.scope_name, subscription['id'])
    candidates += get_resource(args.scope_name, subscription['id'])
    if len(candidates) == 0:
        raise ValueError("Cannot find subcription/resource group/resource with name (case insensitive): " + args.scope_name)
    scope_id = return_single_item_from_multiple_choices(candidates)
    
    # find role by name matching
    candidates = get_role(args.role_name, subscription['id'])
    if len(candidates) == 0:
        raise ValueError("Cannot find role with name (case sensitive): " + args.role_name)
    role_id = return_single_item_from_multiple_choices(candidates)

    # get assignee's ID
    if args.target_name:
        candidates = get_service_principal(args.target_name, subscription['id'])        
        if len(candidates) == 0:
            raise ValueError("Cannot find target with name (case insensitive): " + args.target_name)
        target_id = return_single_item_from_multiple_choices(candidates)['id']
    else:
        target_id = get_signed_in_user(access_token)

    print(assign_role(target_id, scope_id, role_id, headers))
