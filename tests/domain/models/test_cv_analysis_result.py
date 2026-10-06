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
        match_justification="Candidate matches core backend requirements and demonstrated solid API skills.",
    )

    assert result.candidate_name == "Jane Doe"
    assert result.years_of_experience == 5.5
    assert result.key_skills == ["Python", "FastAPI", "Docker"]
    assert result.education == "B.S. in Computer Science"
    assert result.relevant_experience == "5 years of software engineering"
    assert result.strengths == ["Fast learner", "Architecture design"]
    assert result.areas_for_improvement == ["No cloud certification"]
    assert result.match_percentage == 85
    assert (
        result.match_justification
        == "Candidate matches core backend requirements and demonstrated solid API skills."
    )
    assert result.provider == ""
    assert result.model == ""


def test_cv_analysis_result_with_provider_and_model() -> None:
    """Test successful instantiation with explicit provider and model metadata."""
    result = CVAnalysisResult(
        candidate_name="Jane Doe",
        years_of_experience=5.5,
        key_skills=["Python"],
        education="B.S.",
        relevant_experience="Some experience",
        strengths=["Python"],
        areas_for_improvement=["None"],
        match_percentage=85,
        match_justification="Good fit for the required role.",
        provider="gemini",
        model="gemini-3.8-flash",
    )

    assert result.match_justification == "Good fit for the required role."
    assert result.provider == "gemini"
    assert result.model == "gemini-3.8-flash"


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
            match_justification="Partial fit.",
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
            match_justification="Invalid score.",
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
            match_justification="Invalid score.",
        )


def test_cv_analysis_result_rejects_oversized_match_justification() -> None:
    """Test that match_justification exceeding 100 characters raises ValidationError."""
    with pytest.raises(ValidationError):
        CVAnalysisResult(
            candidate_name="Jane Doe",
            years_of_experience=2.0,
            key_skills=["Python"],
            education="B.S.",
            relevant_experience="Some experience",
            strengths=["Python"],
            areas_for_improvement=["None"],
            match_percentage=75,
            match_justification="A" * 101,
        )


def test_cv_analysis_result_accepts_boundary_match_justification() -> None:
    """Test that match_justification of exactly 100 characters succeeds."""
    result = CVAnalysisResult(
        candidate_name="Jane Doe",
        years_of_experience=2.0,
        key_skills=["Python"],
        education="B.S.",
        relevant_experience="Some experience",
        strengths=["Python"],
        areas_for_improvement=["None"],
        match_percentage=75,
        match_justification="A" * 100,
    )
    assert len(result.match_justification) == 100
