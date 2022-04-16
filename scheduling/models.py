from pydantic import BaseModel
from typing import Optional


class Key(BaseModel):
    duration: str = ""
    criticalPath: str = ""
    correlation: str = ""


class GlobalState(BaseModel):
    baselineReady: bool = False
    baselineKey: Key = Key()
    resultKey: Key = Key()
