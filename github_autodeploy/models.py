from pydantic import BaseModel, FilePath, DirectoryPath, model_validator
from typing import Annotated
from fastapi import Header

# Config model
class Script(BaseModel):
    """
    Represents a script, specifying it's execution details.

    Attributes:
        run (FilePath): The script or command to be executed.
        work_dir (DirectoryPath | None): The working directory for the script.
    """
    run: FilePath
    work_dir: DirectoryPath | None = None

    @model_validator(mode='after')
    def check_dirname(self):
        if self.work_dir is None:
            self.work_dir = self.run.parent
        return self

class ConfigRepo(BaseModel):
    secret: str
    events: dict[str, Script]

class Config(BaseModel):
    repos: dict[str, ConfigRepo]
    max_queue_length: int = 0

# Payload model
class PayloadRepository(BaseModel):
    full_name: str

# Header model
class Headers(BaseModel):
    X_GitHub_Delivery: Annotated[str, Header(description="Request UUID")]
    X_Hub_Signature_256: Annotated[str, Header(description="HMAC-SHA256 with your secret as the key")]
    X_GitHub_Event: Annotated[str, Header(description="Event type e.g. 'push'")]
