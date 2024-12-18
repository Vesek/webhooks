from pydantic import BaseModel, RootModel

# Config model
class EventConfig(BaseModel):
    secret: str
    work_dir: str | None = None
    run: str

class RepositoryEvent(RootModel):
    root: dict[str, EventConfig]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

class ConfigModel(RootModel):
    root: dict[str, RepositoryEvent]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

# Repository model
class RepositoryModel(BaseModel):
    full_name: str
