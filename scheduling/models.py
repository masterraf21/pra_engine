from pydantic import BaseModel
from typing import Optional


class GlobalState(BaseModel):
    BaselineAvailable: bool = False
    DurationsBaselineKey: Optional[str]
    CriticalPathBaselineKey: Optional[str]
