from pydantic import BaseModel


class CriticalPathData(BaseModel):
    root: str
    operations: str
    duration: int
