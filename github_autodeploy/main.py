from typing import Annotated
from fastapi import FastAPI, Response, Header, Request, Body
from models import Config, PayloadRepository, Headers
from pydantic_core._pydantic_core import ValidationError
from task_handler import TaskHandler, Task
from asyncio import QueueFull
from logging.handlers import RotatingFileHandler
from os import path
from util import verify_signature
import logging


# Check if config exists, load it, and check validity
try:
    with open(path.join(path.dirname(__file__), "config.json")) as f:
        config = Config.model_validate_json(f.read())
except FileNotFoundError:
    raise SystemExit('ERROR: Config not found')
except ValidationError:
    raise SystemExit('ERROR: Invalid config - refer to config.json.example')


# Setup logging
log_level = logging.INFO
max_log_file_size = 5 * 1024 * 1024  # 5 MB
backup_count = 1

# Log file will probably never be too big, but just to be sure
rotating_handler = RotatingFileHandler(
    "autodeploy.log", maxBytes=max_log_file_size, backupCount=backup_count
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

logger = logging.getLogger("autodeploy")
logger.setLevel(log_level)
logger.addHandler(rotating_handler)

taskhandler = TaskHandler(logger.getChild("taskhandler"), config.max_queue_length)

app = FastAPI(root_path="/autodeploy") # Root path isn't "/" because of use behind a reverse proxy

logger.info("Server started!")

@app.get("/")
async def read_root():
    '''
    Get request handler for root, exists just for curious people snooping around
    '''
    message = "This is an autodeploy API webhook endpoint, really nothing interesting."
    return Response(content=message, media_type="text/plain")

@app.post("/")
async def write_root(
    request: Request, # Raw request so it can be hashed tohether with the "secret",
    headers: Annotated[Headers, Header()], # Required headers sent by github
    repository: Annotated[PayloadRepository, Body(embed=True)] # Repository info for searching in config
):
    '''
    Post request handler for root, checks if everyhing is valid and
    '''

    # Check if repository has a defined configuration
    if repository.full_name not in config.repos:
        status_code = 400
        message = f"repository: {{full_name}}: {repository.full_name}\nRepository name with undefined behavior"

        logger.debug(f"Response: {status_code} - {message}")
        return Response(content=message, status_code=status_code, media_type="text/plain")

    repo_config = config.repos[repository.full_name]

    # Check if event has a defined configuration for repo
    if headers.X_GitHub_Event not in repo_config.events:
        status_code = 400
        message = f"X-GitHub-Event: {headers.X_GitHub_Event}\nEvent type with undefined behavior"

        logger.debug(f"Response: {status_code} - {message}")
        return Response(content=message, status_code=status_code, media_type="text/plain")

    # Check if request signature matches config
    if not verify_signature(await request.body(), repo_config.secret, headers.X_Hub_Signature_256):
        status_code = 403
        message="Hash does not match or invalid - violation reported"

        logger.warn(f"Response: {status_code} - {message}")
        return Response(content=message, status_code=status_code, media_type="text/plain")

    task = repo_config.events[headers.X_GitHub_Event]
    uuid = headers.X_GitHub_Delivery

    # Try to add the task to the queue
    try:
        taskhandler.queue.put_nowait(Task(task, uuid))
        log_level = logging.INFO
        status_code = 200
        message = f"Task '{uuid}' added to queue"
    except QueueFull:
        log_level = logging.ERROR
        status_code = 400
        message = "Task queue is full"

    logger.log(log_level, f"Response: {status_code} - {message}")
    return Response(content=message, status_code=status_code, media_type="text/plain")
