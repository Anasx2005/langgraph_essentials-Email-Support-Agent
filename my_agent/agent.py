"""Graph construction for the email agent."""

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from my_agent.utils.state import EmailAgentState
from my_agent.utils.nodes import (
    read_email,
    classify_intent,
    search_documentation,
    bug_tracking,
    write_response,
    human_review,
    send_reply,
)

# Create the graph
builder = StateGraph(EmailAgentState)

# Add nodes
builder.add_node("read_email", read_email)
builder.add_node("classify_intent", classify_intent)
builder.add_node("search_documentation", search_documentation)
builder.add_node("bug_tracking", bug_tracking)
builder.add_node("write_response", write_response)
builder.add_node("human_review", human_review)
builder.add_node("send_reply", send_reply)

# Add edges
builder.add_edge(START, "read_email")
builder.add_edge("read_email", "classify_intent")
builder.add_edge("classify_intent", "search_documentation")
builder.add_edge("classify_intent", "bug_tracking")
builder.add_edge("search_documentation", "write_response")
builder.add_edge("bug_tracking", "write_response")
builder.add_edge("send_reply", END)

# Compile with a checkpointer for persistence (needed for interrupt/resume)
memory = InMemorySaver()
app = builder.compile(checkpointer=memory)