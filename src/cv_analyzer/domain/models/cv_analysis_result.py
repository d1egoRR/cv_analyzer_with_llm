from __future__ import annotations

from pydantic import BaseModel, Field


class CVAnalysisResult(BaseModel):
    """Structured data model for CV job fit evaluation result."""

    candidate_name: str = Field(
        description="Full name of the candidate extracted from the CV. If not present, use 'Not specified'"
    )

    years_of_experience: float = Field(
        description="Demonstrated relevant work experience in years (use 0.0 if none or undetermined)",
        ge=0.0,
    )

    key_skills: list[str] = Field(
        description="List of 5 to 7 key technical and functional skills most relevant to the vacancy"
    )

    education: str = Field(
        description="Highest education level achieved, major/degree, and institution if available"
    )

    relevant_experience: str = Field(
        description="Concise summary (maximum 3-4 lines) of the work trajectory most applicable to this position"
    )

    strengths: list[str] = Field(
        description="3 to 5 key candidate strengths that make them competitive for the vacancy"
    )

    areas_for_improvement: list[str] = Field(
        description="2 to 4 gaps, unproven requirements, or areas to validate in an interview"
    )

    match_percentage: int = Field(
        description=(
            "Estimated overall fit from 0 to 100 weighting: "
            "Experience (40%), Technical Skills (35%), Education/Certifications (15%), and Coherence (10%)"
        ),
        ge=0,
        le=100,
    )

    match_justification: str = Field(
        description="Concise justification (maximum 100 characters) explaining why this match percentage was assigned to the candidate.",
        max_length=100,
    )

    provider: str = Field(
        default="",
        description="LLM provider name that performed the evaluation (e.g. 'gemini', 'openai')",
    )

    model: str = Field(
        default="",
        description="Model identifier that performed the evaluation (e.g. 'gemini-3.8-flash', 'gpt-4o-mini')",
    )
