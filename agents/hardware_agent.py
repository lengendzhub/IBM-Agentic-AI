"""
agents/hardware_agent.py
Specialized Hardware Agent:
Handles laptop, keyboard, mouse, printer, charger, monitor, and battery problems.
Performs diagnostic lookup, identifies high-value hardware requiring approval,
and initiates support tickets when required.
"""

from typing import Dict, Any
from models.schemas import SupportState
from tools.knowledge_tools import search_troubleshooting


def hardware_agent(state: SupportState) -> SupportState:
    """
    LangGraph Node: hardware_agent
    Processes physical hardware inquiries, provides step-by-step troubleshooting,
    flags expensive replacement requests for human approval, and triggers ticketing.
    """
    query = state.get("user_query", "")
    emp_id = state.get("employee_id", "EMP_UNKNOWN")
    emp_memory = state.get("employee_memory", {})

    # Query knowledge base for SOP
    kb_result = search_troubleshooting(query=query, category="hardware")

    # Evaluate if this action requires human-in-the-loop approval
    # (Expensive equipment replacement: laptop replacement, monitor replacement, battery purchase)
    expensive_keywords = ["replace laptop", "new laptop", "buy laptop", "replace monitor", "damaged monitor", "purchase"]
    is_expensive_request = any(k in query.lower() for k in expensive_keywords) or kb_result.get("is_expensive", False)

    if is_expensive_request:
        state["approval_required"] = True
        state["priority"] = "high"

    # Check for ticket status inquiry within query
    if "status" in query.lower() and "tkt-" in query.lower():
        # Delegated to ticket check
        state["final_answer"] = "Detected ticket status request. Retrieving ticket details..."
        return state

    # Build agent response
    steps_text = "\n".join(kb_result.get("steps", []))
    title = kb_result.get("title", "Hardware Diagnostic Procedure")

    greeting = f"Hello {emp_id},"
    dept = emp_memory.get("department")
    if dept and dept != "General":
        greeting += f" (Department: {dept})"

    response_parts = [
        f"{greeting}\n",
        f"I understand you are experiencing an issue with your hardware equipment: \"{query}\".",
        f"\n### {title}:",
        steps_text,
    ]

    # Contextual guidance based on approval and resolution
    if state.get("approval_required", False):
        response_parts.append(
            "\n⚠️ **Human-in-the-loop Approval Notice**: Equipment replacement or high-value hardware requests "
            "require formal authorization from your reporting manager or IT Asset Administrator."
        )
        state["tool_result"] = "APPROVAL_REQUIRED_HARDWARE"
    elif kb_result.get("requires_ticket_if_unresolved", False):
        response_parts.append(
            "\n💡 If the issue persists after performing the diagnostics above, "
            "a hardware support ticket will be created automatically for IT technician dispatch."
        )
        state["tool_result"] = "CREATE_TICKET_RECOMMENDED"
    else:
        state["tool_result"] = "TROUBLESHOOTING_PROVIDED"

    final_answer = "\n".join(response_parts)
    state["final_answer"] = final_answer

    # Update conversation history
    history = state.get("conversation_history", [])
    history.append(f"Assistant [Hardware Agent]: Provided troubleshooting steps for '{title}'.")
    state["conversation_history"] = history

    return state
