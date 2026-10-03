import pytest
from pydantic import ValidationError

from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


def test_cv_analysis_result_valid_instantiation() -> None:
    """Test successful instantiation with valid data."""
    result = CVAnalysisResult(
        candidate_name="Jane Doe",
        years_of_experience=5.5,
        key_skills=["Python", "FastAPI", "Docker"],
        education="B.S. in Computer Science",
        relevant_experience="5 years of software engineering",
        strengths=["Fast learner", "Architecture design"],
        areas_for_improvement=["No cloud certification"],
        match_percentage=85,
    )

    assert result.candidate_name == "Jane Doe"
    assert result.years_of_experience == 5.5
    assert result.key_skills == ["Python", "FastAPI", "Docker"]
    assert result.education == "B.S. in Computer Science"
    assert result.relevant_experience == "5 years of software engineering"
    assert result.strengths == ["Fast learner", "Architecture design"]
    assert result.areas_for_improvement == ["No cloud certification"]
    assert result.match_percentage == 85


def test_cv_analysis_result_rejects_negative_experience() -> None:
    """Test that negative years_of_experience raises ValidationError."""
    with pytest.raises(ValidationError):
        CVAnalysisResult(
            candidate_name="Jane Doe",
            years_of_experience=-1.0,
            key_skills=["Python"],
            education="B.S.",
            relevant_experience="Some experience",
            strengths=["Python"],
            areas_for_improvement=["None"],
            match_percentage=50,
        )


def test_cv_analysis_result_rejects_out_of_bounds_match_percentage() -> None:
    """Test that match_percentage < 0 or > 100 raises ValidationError."""
    with pytest.raises(ValidationError):
        CVAnalysisResult(
            candidate_name="Jane Doe",
            years_of_experience=2.0,
            key_skills=["Python"],
            education="B.S.",
            relevant_experience="Some experience",
            strengths=["Python"],
            areas_for_improvement=["None"],
            match_percentage=105,
        )

    with pytest.raises(ValidationError):
        CVAnalysisResult(
            candidate_name="Jane Doe",
            years_of_experience=2.0,
            key_skills=["Python"],
            education="B.S.",
            relevant_experience="Some experience",
            strengths=["Python"],
            areas_for_improvement=["None"],
            match_percentage=-5,
        )
