from path import Path
from pydantic import BaseModel


class CriticalPathData(BaseModel):
    root: str
    operation: str
    duration: float
