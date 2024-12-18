from typing import Annotated
from fastapi import FastAPI, Response, Header, Request, Body
from models import Config, Repository
from pydantic_core._pydantic_core import ValidationError
from task_handler import TaskHandler, Task
from asyncio import QueueFull
from os import path
from util import verify_signature

# Check if config exists, load it, and check validity
try:
    with open(path.join(path.dirname(__file__), "config.json")) as f:
        config = Config.model_validate_json(f.read())
except FileNotFoundError:
    raise SystemExit('ERROR: Config not found')
except ValidationError:
    raise SystemExit('ERROR: Invalid config - refer to config.json.example')

taskhandler = TaskHandler(config.max_queue_length)

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
    repository: Annotated[Repository, Body(embed=True)] # Repository info for searching in config
):
    '''
    Post request handler for root, checks if everyhing is valid and
    '''
    if repository.full_name in config.repos:

        if X_GitHub_Event in config.repos[repository.full_name].events:
            secret = config.repos[repository.full_name].secret

            if verify_signature(await request.body(), secret, X_Hub_Signature_256):
                task = config.repos[repository.full_name].events[X_GitHub_Event]
                status_code = 200
                message = "Task added to queue"
                try:
                    taskhandler.queue.put_nowait(task)
                except QueueFull:
                    status_code = 400
                    message = "Task queue is full"
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
