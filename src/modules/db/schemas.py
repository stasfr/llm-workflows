from pydantic import BaseModel


class SProject(BaseModel):
    project_name: str
    project_snapshot: str
