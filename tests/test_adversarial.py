from models import MatchResult

def test_injection_output_still_requires_declared_schema():
    result = MatchResult.model_validate({
        "status":"success",
        "match_score":60,
        "top_strengths":["Python"],
        "missing_skills":["Docker"],
        "summary":"Python is explicitly evidenced.\nDocker is not evidenced."
    })
    assert result.match_score == 60
    assert "Docker" in result.missing_skills

def test_invalid_input_contract():
    result = MatchResult.model_validate({
        "status":"invalid_input",
        "match_score":0,
        "top_strengths":[],
        "missing_skills":[],
        "summary":"The supplied content is not a usable resume.\nNo candidate score was produced."
    })
    assert result.match_score == 0
