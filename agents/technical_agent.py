"""
agents/technical_agent.py
Specialized Technical Support Agent:
Handles application crashes, software installation, operating system errors,
and network / Wi-Fi connectivity problems.
"""

from typing import Dict, Any
from models.schemas import SupportState
from tools.knowledge_tools import search_troubleshooting


def technical_agent(state: SupportState) -> SupportState:
    """
    LangGraph Node: technical_agent
    Diagnoses software crashes, operating system alerts, and network connectivity,
    providing structured resolution steps and initiating technical support tickets.
    """
    query = state.get("user_query", "")
    emp_id = state.get("employee_id", "EMP_UNKNOWN")
    emp_memory = state.get("employee_memory", {})

    # Retrieve SOP from troubleshooting knowledge base
    kb_result = search_troubleshooting(query=query, category="technical")

    steps_text = "\n".join(kb_result.get("steps", []))
    title = kb_result.get("title", "Technical Support Resolution")

    # Check previous issues in employee memory for recurring software trouble
    prev_issues = emp_memory.get("previous_issues", [])
    recurrence_note = ""
    if any("payroll" in str(p).lower() for p in prev_issues) and "payroll" in query.lower():
        recurrence_note = "⚠️ *Note: I see you experienced payroll software difficulties recently. Escalating priority.*"
        state["priority"] = "high"

    response_parts = [
        f"Hello {emp_id},",
        f"I have received your technical support inquiry: \"{query}\".",
        recurrence_note,
        f"\n### Recommended Actions for {title}:",
        steps_text,
    ]

    # Filter empty lines
    response_parts = [p for p in response_parts if p]

    if kb_result.get("requires_ticket_if_unresolved", True):
        response_parts.append(
            "\n📌 If these steps do not clear the error code or connectivity issue, "
            "a technical support ticket will be created and assigned to desktop support."
        )
        state["tool_result"] = "CREATE_TICKET_RECOMMENDED"
    else:
        state["tool_result"] = "TROUBLESHOOTING_PROVIDED"

    state["final_answer"] = "\n".join(response_parts)

    # Update conversation history
    history = state.get("conversation_history", [])
    history.append(f"Assistant [Technical Agent]: Provided guidance for '{title}'.")
    state["conversation_history"] = history

    return state
