from __future__ import annotations

from pydantic import BaseModel, Field

from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


class CVAnalysisResponse(BaseModel):
    """Transport schema representing the CV evaluation result."""

    candidate_name: str = Field(
        description="Full name of the candidate extracted from the CV."
    )
    years_of_experience: float = Field(
        description="Demonstrated relevant work experience in years.",
        ge=0.0,
    )
    key_skills: list[str] = Field(
        description="Key technical and functional skills relevant to the vacancy."
    )
    education: str = Field(
        description="Highest education level, degree, and institution."
    )
    relevant_experience: str = Field(
        description="Concise summary of work trajectory most applicable to this position."
    )
    strengths: list[str] = Field(
        description="Key candidate strengths that make them competitive for the role."
    )
    areas_for_improvement: list[str] = Field(
        description="Gaps, unproven requirements, or topics to validate during interview."
    )
    match_percentage: int = Field(
        description="Estimated overall fit percentage (0 to 100).",
        ge=0,
        le=100,
    )
    match_justification: str = Field(
        description="Brief justification (maximum 100 characters) for the assigned match percentage.",
        max_length=100,
    )
    provider: str = Field(
        description="LLM provider used to generate the analysis (e.g. 'gemini', 'openai')."
    )
    model: str = Field(
        description="Model identifier used to generate the analysis (e.g. 'gemini-3.8-flash', 'gpt-4o-mini')."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "candidate_name": "Jane Doe",
                "years_of_experience": 5.0,
                "key_skills": [
                    "Python",
                    "FastAPI",
                    "Docker",
                    "LangChain",
                    "PostgreSQL",
                ],
                "education": "B.S. in Computer Science - Tech University",
                "relevant_experience": "5 years designing scalable backend APIs and integrating LLM pipelines.",
                "strengths": [
                    "Deep FastAPI expertise",
                    "Clean hexagonal architecture design",
                    "Hands-on LCEL experience",
                ],
                "areas_for_improvement": [
                    "No explicit cloud certifications listed",
                    "Needs validation on Kubernetes cluster management",
                ],
                "match_percentage": 88,
                "match_justification": "Matches core FastAPI & Python requirements; lacks explicit Kubernetes experience.",
                "provider": "gemini",
                "model": "gemini-3.8-flash",
            }
        }
    }

    @classmethod
    def from_domain(cls, domain: CVAnalysisResult) -> CVAnalysisResponse:
        """Create a response schema instance from a domain model.

        Args:
            domain: Domain CVAnalysisResult instance.

        Returns:
            Mapped CVAnalysisResponse instance.
        """
        return cls(
            candidate_name=domain.candidate_name,
            years_of_experience=domain.years_of_experience,
            key_skills=domain.key_skills,
            education=domain.education,
            relevant_experience=domain.relevant_experience,
            strengths=domain.strengths,
            areas_for_improvement=domain.areas_for_improvement,
            match_percentage=domain.match_percentage,
            match_justification=domain.match_justification,
            provider=domain.provider or "unknown",
            model=domain.model or "unknown",
        )


class ErrorResponse(BaseModel):
    """Transport schema representing an API error response."""

    detail: str = Field(description="Description of the error that occurred.")
