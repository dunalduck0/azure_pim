import argparse

from az_cli import get_access_token, get_signed_in_user
from rest_api import activate_role, list_activated, list_eligibility


def init():
    parser = argparse.ArgumentParser(usage="pim.py without arguments will list all scopes, their roles and whether it's activated.\npim.py gcrllama2ws msrresrchvc will activate these two roles for submitting Sing jobs from gcrllama2ws.")
    parser.add_argument("scope_list", type=str, nargs='*', help="List of scopes")
    return parser.parse_args()


if __name__ == "__main__":
    args = init()

    access_token = get_access_token()
    user_id = get_signed_in_user(access_token)    

    dct_activated = list_activated(access_token)
    activated_scope_roles = [(x['properties']['expandedProperties']['scope']['id'], x['properties']['expandedProperties']['roleDefinition']['id']) for x in dct_activated]

    dct_eligibility = list_eligibility(access_token)
    scope_name_lookup = {}
    for item in dct_eligibility:
        data = item['properties']['expandedProperties']
        scope_name = data['scope']['displayName']
        if scope_name in scope_name_lookup:
            scope_name_lookup[data['scope']['displayName']].append(data)
        else:
            scope_name_lookup[data['scope']['displayName']] = [data]
    
        activated = (data['scope']['id'], data['roleDefinition']['id']) in activated_scope_roles
        print(scope_name, '---', data['roleDefinition']['displayName'], '---', 'activated' if activated else 'not activated')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-type': 'application/json'
    }

    print('')
    for scope_name in args.scope_list:
        if not scope_name in scope_name_lookup:
            raise ValueError("Unknown scope name " + scope_name)
        
        if len(scope_name_lookup[scope_name]) > 1:
            raise NotImplementedError("Multiple roles for the same scope is not supported yet")

        s = scope_name_lookup[scope_name][0]
        scope_id = s['scope']['id'].strip('/')
        role_id = s['roleDefinition']['id']
        rst = activate_role(scope_id, role_id, user_id, headers)

        scope_name = rst['properties']['expandedProperties']['scope']['displayName']
        role_name = rst['properties']['expandedProperties']['roleDefinition']['displayName']
        user_name = rst['properties']['expandedProperties']['principal']['displayName']
        status = rst['properties']['status']
        print(f"{scope_name} --- {role_name} --- {user_name} --- {status}")
