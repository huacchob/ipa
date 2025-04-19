import json
from copy import deepcopy

import requests

base_url: str = "http://localhost:9080/nitro/v1"

login_url: str = f"{base_url}/config/login"

auth_payload: str = json.dumps(
    obj={
        "login": {"username": "nsroot", "password": "nsroot"},
    }
)
post_headers: dict[str, str] = {"Content-Type": "application/json"}

login_response: requests.Response = requests.request(
    method="POST",
    url=login_url,
    headers=post_headers,
    data=auth_payload,
    timeout=1000,
)

ses_id: str = login_response.json().get("sessionid", "")


# interface_url: str = f"{base_url}/config/interface"
interface_url: str = f"{base_url}/config/dnsnameserver"

get_headers: dict[str, str] = deepcopy(post_headers)
get_headers.update({"Cookie": f"NITRO_AUTH_TOKEN={ses_id}"})

interface_response: requests.Response = requests.request(
    method="GET",
    url=interface_url,
    headers=get_headers,
    timeout=1000,
)

print(interface_response.json())
