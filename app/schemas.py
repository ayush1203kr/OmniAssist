"""Pydantic request/response schemas."""
from pydantic import BaseModel, Field, field_validator

class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural-language customer-support query")
    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be empty or whitespace")
        return value.strip()

class AskResponse(BaseModel):
    query: str
    answer: str
    keywords: list[str]
    tool_used: str
    tools_used: list[str]
