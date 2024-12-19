from pydantic import BaseModel, FilePath, DirectoryPath, model_validator
from typing import Annotated
from fastapi import Header

# Config model
class Script(BaseModel):
    """
    Model for individual scripts, specifying their execution details.

    Attributes:
        run (FilePath): The script or command to be executed.
        refs (list[str] | None): Which refs should trigger the script. Can be None (null) because some events may not have 'refs'
        work_dir (DirectoryPath | None): The working directory for the script.
    """
    run: FilePath
    refs: list[str] | None = ["refs/heads/main"]
    work_dir: DirectoryPath | None = None

    @model_validator(mode='after')
    def check_dirname(self):
        """
        Set the work directory to the parent of the script if it's not specified.
        """
        if self.work_dir is None:
            self.work_dir = self.run.parent
        return self

class ConfigRepo(BaseModel):
    """
    Model for the configuration of specific Github repos.

    Attributes:
        secret (str): The secret key used for signing the payload.
        events (dict[str, Script]): A mapping of event types to scripts that should be executed.
    """
    secret: str
    events: dict[str, Script]

class Config(BaseModel):
    """
    Model for the configuration file.

    Attributes:
        repos (dict[str, ConfigRepo]): A mapping of repository names to configurations.
        max_queue_length (int): The maximum number of tasks that can be in the queue at any time. Default is 0 (unlimited).
    """
    repos: dict[str, ConfigRepo]
    max_queue_length: int = 0

# Payload model
class PayloadRepository(BaseModel):
    """
    Model of a repository in the payload.

    Attributes:
        full_name (str): The full name of the repository, usually in the format 'owner/repository'.
    """
    full_name: str

class Payload(BaseModel):
    """
    Model of an webhook payload.

    Attributes:
        ref (str | None): The reference (branch or tag) associated with the event. Can be None because some events don't have refs associated.
        repository (PayloadRepository): The repository model.
    """
    ref: str | None = None
    repository: PayloadRepository

# Header model
class Headers(BaseModel):
    """
    Represents the headers of an Webhook HTTP request from GitHub.

    Attributes:
        X_GitHub_Delivery (str): Request UUID.
        X_Hub_Signature_256 (str): HMAC-SHA256 with your secret as the key.
        X_GitHub_Event (str): Event type, e.g. 'push'.

    """
    X_GitHub_Delivery: Annotated[str, Header(description="Request UUID")]
    X_Hub_Signature_256: Annotated[str, Header(description="HMAC-SHA256 with your secret as the key")]
    X_GitHub_Event: Annotated[str, Header(description="Event type e.g. 'push'")]
