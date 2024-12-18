from pydantic import BaseModel, FilePath, DirectoryPath, model_validator

# Config model
class Task(BaseModel):
    """
    Represents a task, specifying the script's execution details.

    Attributes:
        run (FilePath): The script or command to be executed.
        work_dir (DirectoryPath | None): The working directory for the task.
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
    events: dict[str, Task]

class Config(BaseModel):
    repos: dict[str, ConfigRepo]
    max_queue_length: int = 0

# Repository model
class Repository(BaseModel):
    full_name: str
