
import json
import subprocess

import jwt


class CommandFailedException(Exception):
    def __init__(self, command, returncode, error=None):
        self.command = command
        self.returncode = returncode
        self.error = error
        super().__init__(self._format_message())

    def _format_message(self):
        base_message = f"Command '{' '.join(self.command)}' failed with return code {self.returncode}."
        if self.error:
            return f"{base_message} error:\n{self.error}"
        return base_message


def run_command(cmd: list[str]):
    #print("Running command:\n" + ' '.join(cmd))
    p = subprocess.run(cmd, shell=False, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise CommandFailedException(cmd, p.returncode, p.stderr.decode('utf-8').strip())
    return p.stdout.decode('utf-8').strip()


def return_single_item_from_multiple_choices(choices):
    if not choices:
        return None
    
    if len(choices) == 1:
        return choices[0]

    print(f"Multiple choices found. Please select one by entering the number:")
    for i, choice in enumerate(choices):
        print(f"{i+1}: {choice}")
    while True:
        try:
            choice = int(input())
            if choice < 1 or choice > len(choices):
                print(f"Invalid choice. Please enter a number between 1 and {len(choices)}")
            else:
                return choices[choice-1]
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_access_token():
    return run_command(["az", "account", "get-access-token", "--query", "accessToken", "-o", "tsv"])


def get_signed_in_user(access_token=None):
    if not access_token:
        access_token = get_access_token()
    # https://github.com/Azure/azure-cli/issues/22776#issue-1264203875
    return jwt.decode(access_token, algorithms=['RS256'], options={'verify_signature': False})['oid']


def get_subcription(subscription_name=None):
    """Get the current subscription. It is too slow to process all subscriptions."""
    cmd = ["az", "account", "show", "--query", "{name: name, id: id}"]
    if subscription_name:
        cmd += ["--name", subscription_name]
    rst = json.loads(run_command(cmd))
    return rst


def get_resource_group(resource_group_name, subscription):
    """Get everything that matches the resource group name."""
    cmd = ["az", "group", "list", "--subscription", subscription,
            "--query", f"[? name=='{resource_group_name}'].id"]
    return json.loads(run_command(cmd))


def get_resource(resource_name, subscription):
    """Get everything that matches the resource name."""
    cmd = ["az", "resource", "list", "--subscription", subscription,
           "--name", resource_name, "--query", "[].id"]
    return json.loads(run_command(cmd))


def get_role(role_name, subscription):
    """Role name is case sensitive!"""
    cmd = ["az", "role", "definition", "list", "--subscription", subscription,
           "--name", role_name, "--query", "[].id"]
    return json.loads(run_command(cmd))


def get_service_principal(sp_name, subscription):
    try:
        # TODO: unable to run due to AADSTS530003
        cmd = ["az", "ad", "sp", "list", "--filter", f"displayName eq '{sp_name}'",
            "--query", "[].{id: id, alternativeNames: alternativeNames[1]}"]
        return json.loads(run_command(cmd))
    except CommandFailedException:
        # fallback to using resource list
        cmd = ["az", "resource", "list", "--subscription", subscription,
               "--name", sp_name, "--query", "[].{id: identity.principalId, alternativeNames: id}"]
        return json.loads(run_command(cmd))