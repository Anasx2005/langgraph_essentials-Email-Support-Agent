"""State definitions for the email agent graph."""

from typing import Literal, TypedDict


class EmailClassification(TypedDict):
    """Structured classification result produced by the LLM."""
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


class EmailAgentState(TypedDict):
    """Full state shared across all nodes in the graph."""

    # Raw email data
    email_content: str
    sender_email: str
    email_id: str

    # Classification result
    classification: EmailClassification | None

    # Bug tracking
    ticket_id: str | None

    # Raw search results
    search_results: list[str] | None
    customer_history: dict | None

    # Generated content
    draft_response: str | None