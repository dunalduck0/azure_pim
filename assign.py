import argparse

from az_cli import (
    get_access_token,
    get_resource_group,
    get_role,
    get_signed_in_user,
    get_subscription,
)
from rest_api import assign_role


def init():
    parser = argparse.ArgumentParser()
    parser.add_argument("scope_name", type=str)
    parser.add_argument("role_name", type=str)
    parser.add_argument("--user_id", type=str, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = init()

    access_token = get_access_token()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }

    if args.user_id:
        user_id = args.user_id
    else:
        user_id = get_signed_in_user(access_token)


    scope_id = get_subscription(args.scope_name)
    if not scope_id:
        scope_id = get_resource_group(args.scope_name)
    if not scope_id:
        raise ValueError("Unknown scope name " + args.scope_name)
    
    
    role_id = get_role(args.role_name)

    print(assign_role(user_id, scope_id, role_id, headers))
