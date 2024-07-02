
import subprocess

import jwt


def run_command(cmd: list[str]):
    #print("Running command:\n" + ' '.join(cmd))
    p = subprocess.run(cmd, shell=False, check=False, stdout=subprocess.PIPE)
    if p.returncode != 0:
        raise Exception("Failed to run command:\n" + ' '.join(cmd))
    return p.stdout.decode('utf-8').strip()


def get_access_token():
    return run_command(["az", "account", "get-access-token", "--query", "accessToken", "-o", "tsv"])


def get_signed_in_user(access_token=None):
    if not access_token:
        access_token = get_access_token()
    # https://github.com/Azure/azure-cli/issues/22776#issue-1264203875
    return jwt.decode(access_token, algorithms=['RS256'], options={'verify_signature': False})['oid']


def get_resource_group(resource_group_name):
    cmd = ["az", "group", "list", "-o", "tsv", "--query", f"[? name=='{resource_group_name}'].id"]
    return run_command(cmd)


def get_subscription(subscription_name):
    cmd = ["az", "account", "list", "-o", "tsv", "--query", f"[? name=='{subscription_name}'].id"]
    return run_command(cmd)

def get_role(role_name):
    cmd = ["az", "role", "definition", "list", "--name", role_name, "-o", "tsv", "--query", "[0].id"]
    return run_command(cmd)
