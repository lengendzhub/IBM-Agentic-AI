"""
agents/general_agent.py
Specialized General HR Support Agent:
Handles leave policies, attendance regularization, working hours,
general employee questions, and utility tool requests (ticket status, datetime, calculations).
"""

import re
from typing import Dict, Any
from models.schemas import SupportState
from tools.knowledge_tools import search_troubleshooting
from tools.ticket_tools import check_ticket_status
from tools.utility_tools import get_current_datetime, safe_calculator


def general_agent(state: SupportState) -> SupportState:
    """
    LangGraph Node: general_agent
    Processes human resources inquiries, policy lookups, ticket status tracking,
    and general corporate guidance.
    """
    query = state.get("user_query", "")
    emp_id = state.get("employee_id", "EMP_UNKNOWN")
    q_lower = query.lower()

    # 1. Check if user is asking for Ticket Status (e.g. TKT-XXXXXXXX)
    ticket_match = re.search(r"TKT-[A-Za-z0-9]{8}", query, re.IGNORECASE)
    if "status" in q_lower or "ticket" in q_lower or ticket_match:
        if ticket_match:
            tkt_id = ticket_match.group(0).upper()
            status_info = check_ticket_status(tkt_id)
            if status_info.get("status") == "Ticket not found":
                response = f"Ticket Lookup Result:\nNo record found for ID **{tkt_id}**. Please check the ticket number."
            else:
                response = (
                    f"### 📋 Support Ticket Details:\n"
                    f"- **Ticket ID**: {status_info['ticket_id']}\n"
                    f"- **Employee ID**: {status_info['employee_id']}\n"
                    f"- **Category**: {status_info['category'].upper()}\n"
                    f"- **Priority**: {status_info['priority'].capitalize()}\n"
                    f"- **Status**: **{status_info['status']}**\n"
                    f"- **Description**: {status_info['description']}\n"
                    f"- **Created At**: {status_info['created_at']}\n"
                    f"- **Last Updated**: {status_info['updated_at']}"
                )
            state["tool_result"] = f"CHECKED_TICKET_{tkt_id}"
            state["final_answer"] = response
            return state

    # 2. Check if user is asking for current date/time
    if any(k in q_lower for k in ["what time", "current time", "today's date", "current date"]):
        now_str = get_current_datetime()
        state["tool_result"] = f"DATETIME_{now_str}"
        state["final_answer"] = f"The current system date and time is: **{now_str}**."
        return state

    # 3. Check if user asks a math calculation query (e.g., calculate, 120 + 80)
    math_match = re.search(r"calc(?:ulate)?\s+([0-9\+\-\*\/\s\(\)\.]+)", q_lower)
    if math_match:
        expr = math_match.group(1)
        calc_result = safe_calculator(expr)
        if calc_result.get("success"):
            state["tool_result"] = f"CALCULATED_{calc_result['result']}"
            state["final_answer"] = f"Calculation Result: `{expr}` = **{calc_result['result']}**"
            return state

    # 4. Standard HR Knowledge Base Lookup (Leave, Attendance, Working Hours)
    kb_result = search_troubleshooting(query=query, category="general")
    steps_text = "\n".join(kb_result.get("steps", []))
    title = kb_result.get("title", "HR Policy Information")

    response_parts = [
        f"Hello {emp_id},",
        f"Here is the guidance for: \"{query}\".\n",
        f"### ℹ️ {title}:",
        steps_text,
        "\nIf you need further personal assistance, please contact your HR Business Partner or email hr-support@company.com."
    ]

    state["tool_result"] = "HR_GUIDANCE_PROVIDED"
    state["final_answer"] = "\n".join(response_parts)

    # Update conversation history
    history = state.get("conversation_history", [])
    history.append(f"Assistant [General HR Agent]: Provided HR guidance for '{title}'.")
    state["conversation_history"] = history

    return state
