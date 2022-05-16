from pydantic import BaseModel
from typing import Optional


class Key(BaseModel):
    duration: Optional[str]
    criticalPath: Optional[str]
    correlation: Optional[str]


class GlobalState(BaseModel):
    baselineReady: bool = False
    isRegression: bool = False
    lastRegressionCheck: Optional[str]
    baselineKey: Key = Key()
    resultKey: Key = Key()


class TraceRangeParam(BaseModel):
    endDatetime: str
    startDatetime: str
    limit: int = 5000
