from typing import Annotated
from fastapi import FastAPI, Response, Header, Request, Body
from models import ConfigModel, RepositoryModel
from os import path
from pydantic_core._pydantic_core import ValidationError
import json
import hashlib
import hmac
import subprocess

try:
    with open(path.join(path.dirname(__file__), "config.json")) as f:
        config = ConfigModel(json.load(f))
except FileNotFoundError:
    raise SystemExit('ERROR: Config not found')
except ValidationError:
    raise SystemExit('ERROR: Invalid config - refer to config.json.example')


def verify_signature(payload_body, secret_token, signature_header):
    '''
    Webhook signature verification from GitHub docs:
        https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries#python-example
    Modified for use here
    '''
    if not signature_header:
        return False
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        return False
    else:
        return True

app = FastAPI(root_path="/autodeploy") # Root path isn't "/" because of use behind a reverse proxy

@app.get("/")
async def read_root():
    '''
    Get request handler for root, exists just for curious people snooping around
    '''
    message = "This is an autodeploy API webhook endpoint, really nothing interesting.\nA one minute timeout for requests is implemented for basic spam protection, all violations of this timeout will be reported."
    return Response(content=message, media_type="text/plain")

@app.post("/")
async def write_root(
    request: Request, # Raw request so it can be hashed tohether with the "secret"
    X_Hub_Signature_256: Annotated[str, Header(description="HMAC-SHA256 with your secret as the key")],
    X_GitHub_Event: Annotated[str, Header(description="Event type e.g. 'push'")],
    repository: Annotated[RepositoryModel, Body(embed=True)] # Repository info for searching in config
):
    '''
    Post request handler for root, checks if everyhing is valid and
    '''
    if repository.full_name in config:

        if X_GitHub_Event in config[repository.full_name]:
            secret = config[repository.full_name][X_GitHub_Event].secret

            if verify_signature(await request.body(), secret, X_Hub_Signature_256):
                event_config = config[repository.full_name][X_GitHub_Event]
                subprocess.Popen([event_config.run], cwd=event_config.work_dir, shell=True)
                status_code = 200
                message = "OK"

            else:
                status_code = 403
                message="Hash does not match or invalid - violation reported"

        else:
            status_code = 400
            message = f"X-GitHub-Event: {X_GitHub_Event}\nEvent type with undefined behavior"

    else:
        status_code = 400
        message = f"repository: {{full_name}}: {repository.full_name}\nRepository name with undefined behavior"

    return Response(content=message, status_code=status_code, media_type="text/plain")
