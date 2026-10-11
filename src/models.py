from pydantic import BaseModel, Field


class Analysis(BaseModel):
    match_score: int = Field(ge=0, le=100, description="Overall fit, 0-100")
    summary: str = Field(description="2-3 sentence overall verdict")
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


if __name__ == "__main__":
    a = Analysis(
        match_score=72,
        summary="Good fit overall.",
        matching_skills=["Python", "SQL"],
        missing_skills=["Docker"],
    )
    print(a)
    print(a.model_dump_json(indent=2))