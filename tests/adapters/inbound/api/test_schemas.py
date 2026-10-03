from cv_analyzer.adapters.inbound.api.schemas import (
    CVAnalysisResponse,
    ErrorResponse,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


def test_cv_analysis_response_from_domain_mapping() -> None:
    """Test that CVAnalysisResponse.from_domain accurately maps domain fields."""
    domain_result = CVAnalysisResult(
        candidate_name="Alice Smith",
        years_of_experience=4.0,
        key_skills=["Python", "FastAPI"],
        education="M.S. in Computer Science",
        relevant_experience="4 years developing APIs",
        strengths=["Backend architecture"],
        areas_for_improvement=["Frontend frameworks"],
        match_percentage=90,
    )

    response = CVAnalysisResponse.from_domain(domain_result)

    assert response.candidate_name == domain_result.candidate_name
    assert response.years_of_experience == domain_result.years_of_experience
    assert response.key_skills == domain_result.key_skills
    assert response.education == domain_result.education
    assert response.relevant_experience == domain_result.relevant_experience
    assert response.strengths == domain_result.strengths
    assert response.areas_for_improvement == domain_result.areas_for_improvement
    assert response.match_percentage == domain_result.match_percentage


def test_error_response_instantiation() -> None:
    """Test ErrorResponse schema with detail message."""
    error = ErrorResponse(detail="Invalid file format")
    assert error.detail == "Invalid file format"
