from typing import Optional

from pydantic import BaseModel


class SimulateStartIn(BaseModel):
    premise: str
    divergence_year: int
    domains: list[str] = []
    initial_conditions: str = ""


class StepOut(BaseModel):
    id: int
    session_id: int
    gen: int
    idx: int
    domain: str
    year_range: str
    event: str
    probability: str
    analogy: str

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    premise: str
    divergence_year: int
    parent_session_id: Optional[int] = None
    branch_from_step_id: Optional[int] = None
    branch_note: str = ""

    class Config:
        from_attributes = True


class BranchIn(BaseModel):
    step_id: int
    premise: str = ""
