"""
workflow/graph.py
LangGraph StateGraph implementation for the Intelligent HR Equipment Support Assistant.
Connects query classification, conditional routing, specialized agents,
tool calling (ticket creation), human-in-the-loop approval, and memory updates.
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END

from models.schemas import SupportState, IssueCategory
from memory.database import get_db
from agents.classifier import classify_query, route_query
from agents.hardware_agent import hardware_agent
from agents.technical_agent import technical_agent
from agents.access_agent import access_agent
from agents.general_agent import general_agent
from tools.ticket_tools import create_support_ticket


# ==============================================================================
# Node 6: create_ticket
# ==============================================================================

def create_ticket_node(state: SupportState) -> SupportState:
    """
    LangGraph Node: create_ticket
    Generates a unique support ticket in SQLite and appends details to final_answer.
    """
    emp_id = state.get("employee_id", "EMP_UNKNOWN")
    category = state.get("category", "general")
    query = state.get("user_query", "Support issue")
    priority = state.get("priority", "medium")

    # Call the support ticket tool
    ticket = create_support_ticket(
        employee_id=emp_id,
        category=category,
        description=query,
        priority=priority
    )

    state["tool_result"] = f"CREATED_TICKET_{ticket['ticket_id']}"

    ticket_banner = (
        f"\n\n---\n"
        f"### 🎫 Support Ticket Generated Successfully\n"
        f"- **Ticket ID**: `{ticket['ticket_id']}`\n"
        f"- **Employee ID**: {ticket['employee_id']}\n"
        f"- **Category**: {ticket['category'].capitalize()}\n"
        f"- **Priority**: {ticket['priority'].capitalize()}\n"
        f"- **Status**: **{ticket['status']}**\n"
        f"- **Created At**: {ticket['created_at']}\n"
        f"- **Description**: {ticket['description']}\n"
        f"You can track this ticket anytime using: *\"Status of ticket {ticket['ticket_id']}\"*"
    )

    current_answer = state.get("final_answer", "")
    state["final_answer"] = current_answer + ticket_banner

    # Update conversation history
    history = state.get("conversation_history", [])
    history.append(f"System: Created support ticket {ticket['ticket_id']}.")
    state["conversation_history"] = history

    return state


# ==============================================================================
# Node 7: human_approval
# ==============================================================================

def human_approval_node(state: SupportState) -> SupportState:
    """
    LangGraph Node: human_approval
    Handles security or high-cost sensitive actions:
    - Records an approval request in the SQLite database
    - Appends an escalation notice to final_answer
    """
    emp_id = state.get("employee_id", "EMP_UNKNOWN")
    category = state.get("category", "general")
    query = state.get("user_query", "")

    db = get_db()
    action_type = f"{category.upper()}_SENSITIVE_ACTION"
    req_id = db.create_approval_request(
        employee_id=emp_id,
        action_type=action_type,
        details=query
    )

    approval_banner = (
        f"\n\n---\n"
        f"### 🛡️ Human-in-the-Loop Security Escalation\n"
        f"- **Approval Request ID**: `{req_id}`\n"
        f"- **Action Type**: `{action_type}`\n"
        f"- **Current Status**: **Pending Human Verification**\n"
        f"Because this action involves access credentials, account security, or high-value asset replacement, "
        f"it cannot be completed autonomously. An authorized IT Administrator or reporting manager "
        f"must approve request `{req_id}` before changes take effect."
    )

    current_answer = state.get("final_answer", "")
    state["final_answer"] = current_answer + approval_banner

    # Update conversation history
    history = state.get("conversation_history", [])
    history.append(f"System: Escalated to Human-in-the-Loop approval (Request ID: {req_id}).")
    state["conversation_history"] = history

    return state


# ==============================================================================
# Node 8: final_response
# ==============================================================================

def final_response_node(state: SupportState) -> SupportState:
    """
    LangGraph Node: final_response
    Finalizes response, writes turn to SQLite short-term conversation logs,
    and returns completed state.
    """
    emp_id = state.get("employee_id", "EMP_UNKNOWN")
    query = state.get("user_query", "")
    answer = state.get("final_answer", "Your request has been processed.")

    # Save to SQLite conversation history
    db = get_db()
    db.save_conversation(employee_id=emp_id, role="user", message=query)
    db.save_conversation(employee_id=emp_id, role="assistant", message=answer)

    return state


# ==============================================================================
# Conditional Edges Logic
# ==============================================================================

def route_after_agent(state: SupportState) -> str:
    """
    Decides the next step after a specialized agent executes:
    - 'human_approval' if state['approval_required'] is True
    - 'create_ticket' if tool_result recommends ticket creation
    - 'final_response' otherwise
    """
    if state.get("approval_required", False):
        return "human_approval"

    tool_result = state.get("tool_result", "")
    query = state.get("user_query", "").lower()

    # Create ticket automatically if agent recommended it or user explicitly reported failure
    ticket_indicators = [
        "CREATE_TICKET_RECOMMENDED",
        "printer is not printing",
        "crashes whenever",
        "crashes on startup",
        "broken"
    ]
    should_ticket = any(ind in tool_result for ind in ["CREATE_TICKET_RECOMMENDED"]) or \
                   any(ind in query for ind in ["printer is not printing", "crashes whenever", "crashes on startup"])

    # Do not create ticket if this is just a ticket-status lookup or simple general question
    if "status of ticket" in query or "check ticket" in query:
        should_ticket = False

    if should_ticket:
        return "create_ticket"

    return "final_response"


# ==============================================================================
# Graph Construction & Compilation
# ==============================================================================

def build_graph():
    """
    Assembles and compiles the LangGraph StateGraph.

    Nodes:
    1. classify_query
    2. hardware_agent
    3. technical_agent
    4. access_agent
    5. general_agent
    6. create_ticket
    7. human_approval
    8. final_response
    """
    workflow = StateGraph(SupportState)

    # 1. Add all 8 nodes
    workflow.add_node("classify_query", classify_query)
    workflow.add_node("hardware_agent", hardware_agent)
    workflow.add_node("technical_agent", technical_agent)
    workflow.add_node("access_agent", access_agent)
    workflow.add_node("general_agent", general_agent)
    workflow.add_node("create_ticket", create_ticket_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("final_response", final_response_node)

    # 2. Add entry edge: START -> classify_query
    workflow.add_edge(START, "classify_query")

    # 3. Add conditional router edges from classify_query
    workflow.add_conditional_edges(
        "classify_query",
        route_query,
        {
            "hardware_agent": "hardware_agent",
            "technical_agent": "technical_agent",
            "access_agent": "access_agent",
            "general_agent": "general_agent"
        }
    )

    # 4. Add conditional edges from each specialized agent
    for agent_name in ["hardware_agent", "technical_agent", "access_agent", "general_agent"]:
        workflow.add_conditional_edges(
            agent_name,
            route_after_agent,
            {
                "human_approval": "human_approval",
                "create_ticket": "create_ticket",
                "final_response": "final_response"
            }
        )

    # 5. Connect downstream nodes
    workflow.add_edge("human_approval", "final_response")
    workflow.add_edge("create_ticket", "final_response")
    workflow.add_edge("final_response", END)

    # 6. Compile graph
    app = workflow.compile()
    return app


def run_support_agent(
    employee_id: str,
    query: str,
    db_path: str = None
) -> SupportState:
    """
    Convenience wrapper to run a full cycle of the support agent graph.
    Initializes employee memory, invokes compiled LangGraph, and returns final state.
    """
    db = get_db(db_path) if db_path else get_db()
    emp_memory = db.get_employee_memory(employee_id)
    history = db.get_recent_conversations(employee_id, limit=6)

    initial_state: SupportState = {
        "user_query": query,
        "employee_id": employee_id,
        "category": "",
        "priority": "medium",
        "conversation_history": history,
        "employee_memory": emp_memory,
        "tool_result": "",
        "approval_required": False,
        "final_answer": ""
    }

    graph = build_graph()
    final_state = graph.invoke(initial_state)
    return final_state
