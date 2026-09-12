"""
agents/access_agent.py
Specialized Access & Account Agent:
Handles password-reset requests, login problems, account lockouts, and system permissions.
Implements strict security boundaries: never collects passwords, triggers mandatory
human-in-the-loop approvals for privileged actions.
"""

from typing import Dict, Any
from models.schemas import SupportState
from tools.knowledge_tools import search_troubleshooting


def access_agent(state: SupportState) -> SupportState:
    """
    LangGraph Node: access_agent
    Processes security access and identity requests.
    Enforces Human-in-the-Loop (HITL) approval for password resets,
    privilege escalations, and system provisioning.
    """
    query = state.get("user_query", "")
    emp_id = state.get("employee_id", "EMP_UNKNOWN")

    # Search access troubleshooting SOP
    kb_result = search_troubleshooting(query=query, category="access")

    # Security check: identify sensitive operations requiring human approval
    sensitive_operations = [
        "password", "reset password", "forgot password", "unlock", "locked",
        "permission", "access", "grant", "privilege", "role"
    ]
    is_sensitive = any(term in query.lower() for term in sensitive_operations)

    if is_sensitive:
        state["approval_required"] = True
        state["tool_result"] = "APPROVAL_REQUIRED_ACCESS"

    steps_text = "\n".join(kb_result.get("steps", []))
    title = kb_result.get("title", "Access & Identity Management SOP")

    response_parts = [
        f"Hello {emp_id},",
        f"Regarding your access and account request: \"{query}\".",
        "\n🔒 **Security Notice**: For your protection and organizational compliance, "
        "passwords and sensitive authentication tokens must NEVER be shared in chat.\n",
        f"### {title}:",
        steps_text,
    ]

    if state.get("approval_required", False):
        response_parts.append(
            "\n⚠️ **Human-in-the-Loop Approval Required**: "
            "Because this involves credential reset or access provisioning, "
            "an authorization request has been routed to your departmental IT Administrator / Manager."
        )

    state["final_answer"] = "\n".join(response_parts)

    # Update conversation history
    history = state.get("conversation_history", [])
    history.append(f"Assistant [Access Agent]: Provided security procedure for '{title}' (Approval: {state.get('approval_required')}).")
    state["conversation_history"] = history

    return state
