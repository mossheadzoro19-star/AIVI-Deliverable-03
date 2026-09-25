from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class MatchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["success","invalid_input","insufficient_evidence","rate_limited","timeout","evaluation_unavailable"]
    match_score: int = Field(ge=0, le=100)
    top_strengths: list[str] = Field(default_factory=list, max_length=5)
    missing_skills: list[str] = Field(default_factory=list, max_length=10)
    summary: str

    @field_validator("summary")
    @classmethod
    def exactly_two_lines(cls, v: str) -> str:
        lines = [x.strip() for x in v.replace("\r\n","\n").split("\n") if x.strip()]
        if len(lines) != 2:
            raise ValueError("summary must contain exactly two non-empty lines")
        return "\n".join(lines)
