from lib2to3.pytree import Base
from statistics import correlation
from pydantic import BaseModel


class FeatureCorrelation(BaseModel):
    feature: str
    correlation: int
