import json
import pytest
from client import sanitize_json
from models import MatchResult

def test_sanitize_markdown_json():
    raw='```json\n{"status":"success","match_score":72,"top_strengths":["Python"],"missing_skills":["Docker"],"summary":"Strong Python foundation.\\nDocker is not evidenced."}\n```'
    obj=MatchResult.model_validate(json.loads(sanitize_json(raw)))
    assert obj.match_score==72

def test_reject_extra_fields():
    with pytest.raises(Exception):
        MatchResult.model_validate({"status":"success","match_score":50,"top_strengths":[],"missing_skills":[],"summary":"one\\ntwo","unexpected":"x"})

def test_score_bounds():
    with pytest.raises(Exception):
        MatchResult.model_validate({"status":"success","match_score":101,"top_strengths":[],"missing_skills":[],"summary":"one\\ntwo"})

def test_summary_requires_two_lines():
    with pytest.raises(Exception):
        MatchResult.model_validate({"status":"success","match_score":50,"top_strengths":[],"missing_skills":[],"summary":"only one line"})
