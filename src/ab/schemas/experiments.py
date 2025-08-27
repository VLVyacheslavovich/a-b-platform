from pydantic import BaseModel
from typing import List, Optional, Dict

class GroupRatio(BaseModel):
    group: int
    ratio: int
    params: Optional[Dict] = {}


class ExperimentIn(BaseModel):
    experiment_name : str
    source: str
    groups: List[GroupRatio]


class ExperimentOut(BaseModel):
    experiment_id: int
    experiment_name: str
    source: str
    groups_count: int
