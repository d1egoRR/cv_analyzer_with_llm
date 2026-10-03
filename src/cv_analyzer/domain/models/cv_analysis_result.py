from __future__ import annotations

from pydantic import BaseModel, Field


class CVAnalysisResult(BaseModel):
    """Structured data model for CV job fit evaluation result."""

    candidate_name: str = Field(
        description="Nombre completo del candidato extraído del CV. Si no figura, usar 'No especificado'"
    )

    years_of_experience: float = Field(
        description="Años de experiencia laboral relevante demostrada (usar 0.0 si no cuenta o no se puede determinar)",
        ge=0.0,
    )

    key_skills: list[str] = Field(
        description="Lista de 5 a 7 habilidades técnicas y funcionales más relevantes para la vacante"
    )

    education: str = Field(
        description="Máximo nivel alcanzado, título o especialización principal e institución si figura"
    )

    relevant_experience: str = Field(
        description="Resumen conciso (máximo 3-4 líneas) del recorrido laboral más aplicable a este puesto"
    )

    strengths: list[str] = Field(
        description="3 a 5 fortalezas principales que lo hacen competitivo para la vacante"
    )

    areas_for_improvement: list[str] = Field(
        description="2 a 4 brechas, requisitos no demostrados o aspectos a validar en entrevista"
    )

    match_percentage: int = Field(
        description=(
            "Ajuste global estimado de 0 a 100 aplicando mentalmente: "
            "Experiencia (40%), Habilidades técnicas (35%), Formación/Certificaciones (15%) y Coherencia (10%)"
        ),
        ge=0,
        le=100,
    )
