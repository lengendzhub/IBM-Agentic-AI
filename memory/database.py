"""
memory/database.py
SQLite database implementation for long-term employee memory,
ticket persistence, conversation logging, and approval workflows.
"""

import sqlite3
import json
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List


# Default database path inside project data folder
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "support.db"
)


class SupportDatabase:
    """
    Manages SQLite database operations for:
    - Long-term employee memory (department, preferences, past issues)
    - Support tickets (creation, status updates, history lookup)
    - Conversation logs (short-term turn history stored persistently)
    - Human approval requests (sensitive actions workflow)
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.initialize_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_tables(self) -> None:
        """Creates all required database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Support Tickets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    ticket_id TEXT PRIMARY KEY,
                    employee_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    status TEXT NOT NULL DEFAULT 'Open',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # 2. Employee Long-term Memory Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_memory (
                    employee_id TEXT PRIMARY KEY,
                    department TEXT DEFAULT 'General',
                    preferred_language TEXT DEFAULT 'English',
                    previous_issues TEXT DEFAULT '[]',
                    interaction_count INTEGER DEFAULT 0,
                    last_interaction TEXT
                )
            """)

            # 3. Conversation Logs Table (Short-term persistence)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

            # 4. Human Approval Requests Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS approval_requests (
                    request_id TEXT PRIMARY KEY,
                    employee_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending Approval',
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                )
            """)

            conn.commit()

        # Seed sample data if database is fresh
        self.seed_sample_data()

    def seed_sample_data(self) -> None:
        """Seeds initial employee profiles and a sample ticket for demonstration."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check if employees already exist
            cursor.execute("SELECT COUNT(*) FROM employee_memory")
            if cursor.fetchone()[0] == 0:
                sample_employees = [
                    (
                        "EMP1024",
                        "Finance",
                        "English",
                        json.dumps(["Payroll application login problem", "Monitor flickering"]),
                        2,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    (
                        "EMP1025",
                        "Engineering",
                        "English",
                        json.dumps(["Git SSH key setup", "Docker memory limit"]),
                        4,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    (
                        "EMP1026",
                        "Human Resources",
                        "English",
                        json.dumps(["Leave portal synchronization"]),
                        1,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    (
                        "EMP5501",
                        "Marketing",
                        "English",
                        json.dumps([]),
                        0,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                ]
                cursor.executemany("""
                    INSERT INTO employee_memory
                    (employee_id, department, preferred_language, previous_issues, interaction_count, last_interaction)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, sample_employees)

            # Check if sample tickets exist
            cursor.execute("SELECT COUNT(*) FROM support_tickets")
            if cursor.fetchone()[0] == 0:
                sample_tickets = [
                    (
                        "TKT-12345678",
                        "EMP1024",
                        "technical",
                        "Payroll application crashed on launch error code 0x8004",
                        "high",
                        "In Progress",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    (
                        "TKT-87654321",
                        "EMP1025",
                        "hardware",
                        "External Dell 27-inch monitor flickering and losing HDMI signal",
                        "medium",
                        "Open",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                ]
                cursor.executemany("""
                    INSERT INTO support_tickets
                    (ticket_id, employee_id, category, description, priority, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, sample_tickets)

            conn.commit()

    # --------------------------------------------------------------------------
    # Ticket Operations
    # --------------------------------------------------------------------------

    def create_ticket(
        self,
        employee_id: str,
        category: str,
        description: str,
        priority: str = "medium",
        status: str = "Open"
    ) -> Dict[str, Any]:
        """Creates a new support ticket with a unique TKT-XXXXXXXX identifier."""
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO support_tickets
                (ticket_id, employee_id, category, description, priority, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticket_id, employee_id, category, description, priority, status, now, now))
            conn.commit()

        # Update long-term employee memory with this issue
        self.append_previous_issue(employee_id, f"[{category.upper()}] {description[:60]}")

        return {
            "ticket_id": ticket_id,
            "employee_id": employee_id,
            "category": category,
            "description": description,
            "priority": priority,
            "status": status,
            "created_at": now
        }

    def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a ticket record by its unique ticket_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ticket_id, employee_id, category, description, priority, status, created_at, updated_at
                FROM support_tickets
                WHERE ticket_id = ?
            """, (ticket_id.strip().upper(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """Updates the status of a specific support ticket."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE support_tickets
                SET status = ?, updated_at = ?
                WHERE ticket_id = ?
            """, (status, now, ticket_id.strip().upper()))
            conn.commit()
            return cursor.rowcount > 0

    def list_employee_tickets(self, employee_id: str) -> List[Dict[str, Any]]:
        """Lists all tickets associated with a given employee ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ticket_id, employee_id, category, description, priority, status, created_at, updated_at
                FROM support_tickets
                WHERE employee_id = ?
                ORDER BY created_at DESC
            """, (employee_id.strip().upper(),))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    # --------------------------------------------------------------------------
    # Long-term Memory Operations
    # --------------------------------------------------------------------------

    def get_employee_memory(self, employee_id: str) -> Dict[str, Any]:
        """Retrieves the long-term memory record for an employee."""
        emp_id = employee_id.strip().upper()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT employee_id, department, preferred_language, previous_issues, interaction_count, last_interaction
                FROM employee_memory
                WHERE employee_id = ?
            """, (emp_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                try:
                    data["previous_issues"] = json.loads(data["previous_issues"])
                except Exception:
                    data["previous_issues"] = []
                return data

            # If employee does not exist, create a default profile
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO employee_memory
                (employee_id, department, preferred_language, previous_issues, interaction_count, last_interaction)
                VALUES (?, 'General', 'English', '[]', 0, ?)
            """, (emp_id, now))
            conn.commit()
            return {
                "employee_id": emp_id,
                "department": "General",
                "preferred_language": "English",
                "previous_issues": [],
                "interaction_count": 0,
                "last_interaction": now
            }

    def append_previous_issue(self, employee_id: str, issue_summary: str) -> bool:
        """Appends a new issue record to the employee's long-term memory."""
        emp = self.get_employee_memory(employee_id)
        issues = emp.get("previous_issues", [])
        if issue_summary not in issues:
            issues.append(issue_summary)
            # Keep at most 10 past issues
            if len(issues) > 10:
                issues = issues[-10:]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE employee_memory
                SET previous_issues = ?, interaction_count = interaction_count + 1, last_interaction = ?
                WHERE employee_id = ?
            """, (json.dumps(issues), now, employee_id.strip().upper()))
            conn.commit()
            return cursor.rowcount > 0

    # --------------------------------------------------------------------------
    # Conversation Logging (Short-term context persistence)
    # --------------------------------------------------------------------------

    def save_conversation(self, employee_id: str, role: str, message: str) -> None:
        """Logs a single turn in the conversation."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_logs (employee_id, role, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (employee_id.strip().upper(), role, message, now))
            conn.commit()

    def get_recent_conversations(self, employee_id: str, limit: int = 6) -> List[str]:
        """Fetches recent conversation turns formatted as 'Role: Message'."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, message FROM conversation_logs
                WHERE employee_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (employee_id.strip().upper(), limit))
            rows = cursor.fetchall()
            # Reverse so they appear in chronological order
            history = []
            for r in reversed(rows):
                prefix = "User" if r["role"].lower() == "user" else "Assistant"
                history.append(f"{prefix}: {r['message']}")
            return history

    # --------------------------------------------------------------------------
    # Human-in-the-Loop Approval Operations
    # --------------------------------------------------------------------------

    def create_approval_request(self, employee_id: str, action_type: str, details: str) -> str:
        """Records a pending human approval request."""
        req_id = f"APP-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO approval_requests (request_id, employee_id, action_type, details, status, created_at)
                VALUES (?, ?, ?, ?, 'Pending Approval', ?)
            """, (req_id, employee_id.strip().upper(), action_type, details, now))
            conn.commit()
        return req_id

    def update_approval_status(self, request_id: str, status: str) -> bool:
        """Updates status of a pending approval (e.g., 'Approved', 'Rejected')."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE approval_requests
                SET status = ?, resolved_at = ?
                WHERE request_id = ?
            """, (status, now, request_id.strip().upper()))
            conn.commit()
            return cursor.rowcount > 0


# Global singleton instance provider
_db_instance: Optional[SupportDatabase] = None

def get_db(db_path: str = DEFAULT_DB_PATH) -> SupportDatabase:
    """Returns the singleton instance of the SupportDatabase."""
    global _db_instance
    if _db_instance is None or _db_instance.db_path != db_path:
        _db_instance = SupportDatabase(db_path)
    return _db_instance
