"""
tools/ticket_tools.py
Support ticket management tools integrated with SQLite database.
Allows agents to create, query, and track support tickets.
"""

from typing import Dict, Any, List
from memory.database import get_db

try:
    from langchain_core.tools import tool
except ImportError:
    # Fallback decorator if langchain_core is being loaded
    def tool(func):
        return func


def create_support_ticket(
    employee_id: str,
    category: str,
    description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Creates a new HR or IT equipment support ticket in the database.

    Args:
        employee_id: The ID of the employee reporting the issue (e.g. EMP1024).
        category: The issue category ('hardware', 'technical', 'access', 'general').
        description: A clear explanation of the problem or request.
        priority: The priority level ('low', 'medium', 'high', 'critical'). Defaults to 'medium'.

    Returns:
        A dictionary containing ticket_id, employee_id, category, description, priority, status, and created_at.
    """
    db = get_db()
    # Normalize category and priority
    category_clean = category.strip().lower()
    priority_clean = priority.strip().lower() if priority else "medium"

    ticket = db.create_ticket(
        employee_id=employee_id.strip().upper(),
        category=category_clean,
        description=description.strip(),
        priority=priority_clean,
        status="Open"
    )
    return ticket


def check_ticket_status(ticket_id: str) -> Dict[str, Any]:
    """
    Checks the current status of an existing support ticket using its ticket ID.

    Args:
        ticket_id: The unique identifier of the ticket (e.g. TKT-12345678).

    Returns:
        A dictionary with ticket_id, status, category, priority, and description,
        or an informative message if the ticket is not found.
    """
    db = get_db()
    ticket = db.get_ticket(ticket_id.strip().upper())

    if not ticket:
        return {
            "ticket_id": ticket_id,
            "status": "Ticket not found",
            "message": f"No ticket found matching ID '{ticket_id}'. Please verify the ticket number."
        }

    return {
        "ticket_id": ticket["ticket_id"],
        "employee_id": ticket["employee_id"],
        "category": ticket["category"],
        "priority": ticket["priority"],
        "status": ticket["status"],
        "description": ticket["description"],
        "created_at": ticket["created_at"],
        "updated_at": ticket["updated_at"]
    }


def list_employee_tickets(employee_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all past and active support tickets raised by a specific employee.

    Args:
        employee_id: The ID of the employee (e.g. EMP1024).

    Returns:
        A list of ticket dictionaries belonging to the employee.
    """
    db = get_db()
    tickets = db.list_employee_tickets(employee_id.strip().upper())
    return tickets


# Export LangChain Tool instances
create_support_ticket_tool = tool(create_support_ticket)
check_ticket_status_tool = tool(check_ticket_status)
list_employee_tickets_tool = tool(list_employee_tickets)
