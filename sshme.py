import getpass
import json
import pathlib
import socket
import subprocess
import urllib.request

GITLAB_BASE_URL = "https://gitlab.YOURCOMPANY.com"

user_name = getpass.getuser()
user_password = getpass.getpass()
ssh_key_path = pathlib.Path.home().joinpath(".ssh", "id_ed25519")
if ssh_key_path.is_file():
    print("Using existing SSH key:", ssh_key_path)
else:
    print("Creating new SSH key...", ssh_key_path)
    ssh_key_path.parent.mkdir(exist_ok=True)
    subprocess.check_call(["ssh-keygen", "-q", "-t", "ed25519", "-f", str(ssh_key_path), "-N", ""])
pub_key_file = ssh_key_path.with_suffix(".pub")
with pub_key_file.open("r") as file:
    ssh_key = file.read()
print("Creating temporary Gitlab access token...")
request = urllib.request.Request(
    url=GITLAB_BASE_URL + "/oauth/token",
    headers={"Content-Type": "application/json; charset=utf-8"},
    data=json.dumps({"grant_type": "password", "username": user_name, "password": user_password}).encode()
)
with urllib.request.urlopen(request) as response:
    access_token = json.loads(response.read())["access_token"]
print("Publishing SSH key to Gitlab....")
urllib.request.urlopen(urllib.request.Request(
    url=GITLAB_BASE_URL + "/api/v4/user/keys",
    headers={
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {access_token}",
    },
    data=json.dumps({"title": socket.gethostname(), "key": ssh_key}).encode()
))
