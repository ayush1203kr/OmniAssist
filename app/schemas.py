"""Pydantic schemas: request and response validation for the /ask endpoint."""

from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    """Body of POST /ask."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,  # keep queries reasonable
        description="Natural-language customer-support query",
    )

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        # Reject whitespace-only queries; otherwise trim the surrounding spaces.
        if not value.strip():
            raise ValueError("query must not be empty or whitespace")
        return value.strip()


class AskResponse(BaseModel):
    """Structured JSON returned by POST /ask."""

    query: str
    answer: str
    keywords: list[str]
    # Primary tool the agent used: "policy_search" | "order_status" | "calculator" | "none"
    tool_used: str
    # Every tool the agent called, in order (demonstrates multi-step behaviour).
    tools_used: list[str]
