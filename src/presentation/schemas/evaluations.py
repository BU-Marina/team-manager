from pydantic import BaseModel, Field


class EvaluationCreateRequest(BaseModel):
    task_id: int
    score: int = Field(ge=1, le=5)
    comment: str | None = None


class EvaluationResponse(BaseModel):
    id: int
    task_id: int
    evaluator_id: int
    score: int
    comment: str | None = None
