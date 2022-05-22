from pydantic import BaseModel
from typing import Optional
from src.critical_path.models import Result
from src.critical_path.constants import LATENCY_THRESHOLD


class AnalysisResult(BaseModel):
    regression: bool = False
    critical_path_result: Result = Result()


class Key(BaseModel):
    duration: Optional[str]
    criticalPath: Optional[str]


class GlobalState(BaseModel):
    baselineReady: bool = False
    isRegression: bool = False
    lastRegressionCheck: Optional[str]
    currentAnalysis: AnalysisResult = AnalysisResult()
    baselineKey: Key = Key()


class TraceRangeParam(BaseModel):
    endDatetime: str
    startDatetime: str
    limit: int = 5000


class AnalysisParam(BaseModel):
    endDatetime: str
    startDatetime: str
    limit: int = 5000
    latencyThreshold: int = LATENCY_THRESHOLD
