"""Simple script to test the email agent graph end-to-end."""

from datetime import datetime

from dotenv import load_dotenv
from langgraph.types import Command

from my_agent.agent import app

# Load environment variables (GOOGLE_API_KEY) from .env
load_dotenv()

OUTPUT_FILE = "run_output.md"


def log(lines: list[str], text: str):
    """Print to terminal AND collect the line for the markdown file."""
    print(text)
    lines.append(text)


def run_single_test():
    """Send one urgent email through the graph and resume after human review."""

    lines = []
    log(lines, f"# Test Run — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Save the graph diagram as a PNG file
    graph_png = app.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(graph_png)
    log(lines, "Graph image saved as graph.png\n")

    initial_state = {
        "email_content": "I was charged twice for my subscription! This is urgent!",
        "sender_email": "customer@example.com",
        "email_id": "email_123",
    }

    log(lines, "## Input Email\n")
    log(lines, f"```\n{initial_state['email_content']}\n```\n")

    # Run with a thread_id for persistence
    config = {"configurable": {"thread_id": "customer_123"}}
    result = app.invoke(initial_state, config)

    # The graph will pause at human_review if urgency/intent requires it
    if "__interrupt__" in result:
        log(lines, "## Status: Waiting for human review\n")
        log(lines, "### Draft Response\n")
        log(lines, f"```\n{result['draft_response']}\n```\n")

        # Provide human input to resume
        human_response = Command(resume={"approved": True})
        final_result = app.invoke(human_response, config)

        log(lines, "## Status: Email sent successfully\n")
    else:
        log(lines, "## Status: No review needed, response sent directly\n")
        log(lines, f"```\n{result}\n```\n")

    # Write everything collected to the markdown file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nFull output saved to {OUTPUT_FILE}")

# Save the graph diagram as a PNG file
graph_png = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(graph_png)

print("Graph image saved as graph.png")

if __name__ == "__main__":
    run_single_test()