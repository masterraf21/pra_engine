from path import Path
from pydantic import BaseModel


class PathDuration(BaseModel):
    operation: str
    duration: float


class CriticalPathData(BaseModel):
    root: str
    durations: list[PathDuration]
