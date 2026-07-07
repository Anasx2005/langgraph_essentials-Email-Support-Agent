"""Node functions for the email agent graph."""

import uuid

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command, interrupt
from typing import Literal

from my_agent.utils.state import EmailAgentState, EmailClassification

# Ensure environment variables are loaded before the LLM client is created
load_dotenv()

# Using Gemini instead of OpenAI
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


def read_email(state: EmailAgentState) -> EmailAgentState:
    """Extract and parse email content."""
    # Placeholder: in a real system this might parse raw email headers/body
    return {}


def classify_intent(state: EmailAgentState) -> EmailAgentState:
    """Use the LLM to classify email intent and urgency."""

    # Create a structured LLM that returns an EmailClassification dict
    structured_llm = llm.with_structured_output(EmailClassification)

    classification_prompt = f"""
    Analyze this customer email and classify it:

    Email: {state['email_content']}
    From: {state['sender_email']}

    Provide classification, including intent, urgency, topic, and summary
    """

    # Get the structured response directly as a dict
    classification = structured_llm.invoke(classification_prompt)

    # Store classification as a single dict in state
    return {"classification": classification}


def search_documentation(state: EmailAgentState) -> EmailAgentState:
    """Search the knowledge base for relevant information."""

    # Build a search query from the classification
    classification = state.get("classification", {})
    query = f"{classification.get('intent', '')} {classification.get('topic', '')}"

    try:
        # TODO: implement real search logic here (vector store, API, etc.)
        search_results = [
            "--Search_result_1--",
            "--Search_result_2--",
            "--Search_result_3--",
        ]
    except Exception as e:
        # For recoverable search errors, store the error and continue
        search_results = [f"Search temporarily unavailable: {str(e)}"]

    return {"search_results": search_results}


def bug_tracking(state: EmailAgentState) -> EmailAgentState:
    """Create or update a bug tracking ticket."""

    # TODO: integrate with a real bug tracking system (Jira, Linear, etc.)
    ticket_id = f"BUG_{uuid.uuid4()}"

    return {"ticket_id": ticket_id}


def write_response(state: EmailAgentState) -> Command[Literal["human_review", "send_reply"]]:
    """Generate a response using the available context and route based on quality."""

    classification = state.get("classification", {})

    # Format context from raw state data on demand
    context_sections = []

    if state.get("search_results"):
        # Format search results for the prompt
        formatted_docs = "\n".join([f"- {doc}" for doc in state["search_results"]])
        context_sections.append(f"Relevant documentation:\n{formatted_docs}")

    if state.get("customer_history"):
        # Format customer data for the prompt
        context_sections.append(
            f"Customer tier: {state['customer_history'].get('tier', 'standard')}"
        )

    # Build the prompt with formatted context
    draft_prompt = f"""
    Draft a response to this customer email:
    {state['email_content']}

    Email intent: {classification.get('intent', 'unknown')}
    Urgency level: {classification.get('urgency', 'medium')}

    {chr(10).join(context_sections)}

    Guidelines:
    - Be professional and helpful
    - Address their specific concern
    - Use the provided documentation when relevant
    - Be brief
    """

    response = llm.invoke(draft_prompt)

    # Determine if human review is needed based on urgency and intent
    needs_review = (
        classification.get("urgency") in ["high", "critical"]
        or classification.get("intent") == "complex"
    )

    # Route to the appropriate next node
    if needs_review:
        goto = "human_review"
        print("Needs approval")
    else:
        goto = "send_reply"

    return Command(
        update={"draft_response": response.content},
        goto=goto,
    )


def human_review(state: EmailAgentState) -> Command[Literal["send_reply", "__end__"]]:
    """Pause for human review using interrupt() and route based on the decision."""

    classification = state.get("classification", {})

    # interrupt() must come first - any code before it will re-run on resume
    human_decision = interrupt(
        {
            "email_id": state["email_id"],
            "original_email": state["email_content"],
            "draft_response": state.get("draft_response", ""),
            "urgency": classification.get("urgency"),
            "intent": classification.get("intent"),
            "action": "Please review and approve/edit this response",
        }
    )

    # Now process the human's decision
    if human_decision.get("approved"):
        return Command(
            update={
                "draft_response": human_decision.get(
                    "edited_response", state["draft_response"]
                )
            },
            goto="send_reply",
        )
    else:
        # Rejection means a human will handle it directly
        return Command(update={}, goto="__end__")


def send_reply(state: EmailAgentState) -> EmailAgentState:
    """Send the email response."""
    # TODO: integrate with a real email service
    print(f"Sending reply: {state['draft_response'][:60]}...")
    return {}