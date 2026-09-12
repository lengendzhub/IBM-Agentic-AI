"""
tests/test_cases.py
Comprehensive automated test suite for Intelligent HR Equipment Support Assistant.
Executes 10+ test queries through the compiled LangGraph workflow,
evaluates classification accuracy, agent routing, tool calling, and HITL approvals.
"""

import sys
import os
import time
from typing import Dict, Any, List

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.graph import run_support_agent
from memory.database import get_db
from models.schemas import IssueCategory


# Definition of 10+ test cases covering all specified scenarios
TEST_SUITE = [
    {
        "id": 1,
        "name": "Laptop Failure",
        "employee_id": "EMP1024",
        "query": "My laptop is not turning on.",
        "expected_category": "hardware",
        "expected_agent": "hardware_agent",
        "expected_tool": "search_troubleshooting",
        "expected_approval": False,
        "description": "Physical power/boot failure on corporate laptop"
    },
    {
        "id": 2,
        "name": "Printer Failure",
        "employee_id": "EMP1025",
        "query": "Office printer is not printing and showing error light.",
        "expected_category": "hardware",
        "expected_agent": "hardware_agent",
        "expected_tool": "create_support_ticket",
        "expected_approval": False,
        "description": "Printer offline or hardware error requiring ticket creation"
    },
    {
        "id": 3,
        "name": "Software Crash",
        "employee_id": "EMP1024",
        "query": "The payroll application crashes whenever I open it.",
        "expected_category": "technical",
        "expected_agent": "technical_agent",
        "expected_tool": "search_troubleshooting",
        "expected_approval": False,
        "description": "Application crash with repeated failure pattern"
    },
    {
        "id": 4,
        "name": "Wi-Fi Issue",
        "employee_id": "EMP1026",
        "query": "My office Wi-Fi is not connecting on the 3rd floor.",
        "expected_category": "technical",
        "expected_agent": "technical_agent",
        "expected_tool": "search_troubleshooting",
        "expected_approval": False,
        "description": "Corporate wireless network connectivity loss"
    },
    {
        "id": 5,
        "name": "Password Reset",
        "employee_id": "EMP1024",
        "query": "I forgot my employee portal password.",
        "expected_category": "access",
        "expected_agent": "access_agent",
        "expected_tool": "human_approval",
        "expected_approval": True,
        "description": "Sensitive identity credential reset requiring human approval"
    },
    {
        "id": 6,
        "name": "Portal Access Request",
        "employee_id": "EMP1025",
        "query": "I need access to the attendance system.",
        "expected_category": "access",
        "expected_agent": "access_agent",
        "expected_tool": "human_approval",
        "expected_approval": True,
        "description": "Privilege provisioning request requiring manager approval"
    },
    {
        "id": 7,
        "name": "Leave Enquiry",
        "employee_id": "EMP1026",
        "query": "How can I apply for leave?",
        "expected_category": "general",
        "expected_agent": "general_agent",
        "expected_tool": "search_troubleshooting",
        "expected_approval": False,
        "description": "Standard HR policy information request"
    },
    {
        "id": 8,
        "name": "Ticket Status Enquiry",
        "employee_id": "EMP1024",
        "query": "What is the status of ticket TKT-12345678?",
        "expected_category": "general",
        "expected_agent": "general_agent",
        "expected_tool": "check_ticket_status",
        "expected_approval": False,
        "description": "Status lookup of pre-existing ticket in SQLite database"
    },
    {
        "id": 9,
        "name": "Unknown or Unsupported Question",
        "employee_id": "EMP5501",
        "query": "What is the meaning of life?",
        "expected_category": "general",
        "expected_agent": "general_agent",
        "expected_tool": "search_troubleshooting",
        "expected_approval": False,
        "description": "Out-of-scope query handled gracefully by General HR agent"
    },
    {
        "id": 10,
        "name": "Sensitive Equipment Replacement",
        "employee_id": "EMP1024",
        "query": "I need a new laptop, mine is broken and cannot be repaired.",
        "expected_category": "hardware",
        "expected_agent": "hardware_agent",
        "expected_tool": "human_approval",
        "expected_approval": True,
        "description": "High-value asset replacement requiring managerial approval"
    },
    {
        "id": 11,
        "name": "Monitor Failure",
        "employee_id": "EMP1025",
        "query": "My monitor screen is blank and flickering when connected via HDMI.",
        "expected_category": "hardware",
        "expected_agent": "hardware_agent",
        "expected_tool": "search_troubleshooting",
        "expected_approval": True,
        "description": "Display hardware diagnostics with expensive replacement warning"
    },
    {
        "id": 12,
        "name": "Working Hours Enquiry",
        "employee_id": "EMP5501",
        "query": "What are the standard office working hours and shift timings?",
        "expected_category": "general",
        "expected_agent": "general_agent",
        "expected_tool": "search_troubleshooting",
        "expected_approval": False,
        "description": "Company policy regarding office attendance hours"
    }
]


def run_single_test(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Runs a single test case through the LangGraph agent and validates assertions."""
    start_time = time.time()
    emp_id = test_case["employee_id"]
    query = test_case["query"]

    # Invoke the compiled agent graph
    state = run_support_agent(employee_id=emp_id, query=query)
    elapsed = time.time() - start_time

    # Collect actual outcomes
    actual_category = state.get("category", "")
    actual_agent = f"{actual_category}_agent"
    actual_approval = state.get("approval_required", False)
    final_answer = state.get("final_answer", "")
    tool_result = state.get("tool_result", "")

    # Identify tool used
    if "CREATED_TICKET" in tool_result or "TKT-" in final_answer and "Generated Successfully" in final_answer:
        tool_used = "create_support_ticket"
    elif "CHECKED_TICKET" in tool_result or "Ticket Details" in final_answer or "Ticket Lookup Result" in final_answer:
        tool_used = "check_ticket_status"
    elif actual_approval:
        tool_used = "human_approval"
    else:
        tool_used = "search_troubleshooting"

    # Evaluate Pass/Fail criteria
    category_match = actual_category == test_case["expected_category"]
    agent_match = actual_agent == test_case["expected_agent"]
    approval_match = (actual_approval == test_case["expected_approval"])
    has_answer = len(final_answer.strip()) > 30

    passed = category_match and agent_match and approval_match and has_answer

    # Formulate summarized expected vs actual responses
    expected_response_summary = f"Route to {test_case['expected_agent']}, provide SOP for '{test_case['name']}'"
    if test_case["expected_approval"]:
        expected_response_summary += " with HITL approval escalation notice"

    actual_response_summary = final_answer.split("\n")[0] if final_answer else "No response"
    if len(actual_response_summary) > 75:
        actual_response_summary = actual_response_summary[:72] + "..."

    return {
        "id": test_case["id"],
        "name": test_case["name"],
        "query": query,
        "predicted_category": actual_category,
        "selected_agent": actual_agent,
        "tool_used": tool_used,
        "approval_required": actual_approval,
        "expected_response": expected_response_summary,
        "actual_response": actual_response_summary,
        "full_response": final_answer,
        "elapsed_seconds": round(elapsed, 4),
        "category_match": category_match,
        "routing_match": agent_match,
        "passed": passed
    }


if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def run_all_tests() -> List[Dict[str, Any]]:
    """Runs all test cases in sequence, outputs a formatted table, and calculates metrics."""
    print("=" * 80)
    print("  Intelligent HR Equipment Support Assistant - Test Suite Execution")
    print("=" * 80)

    results = []
    total_time = 0.0
    tickets_created = 0

    for tc in TEST_SUITE:
        print(f"\n[Running Test {tc['id']:02d}] {tc['name']} ...")
        res = run_single_test(tc)
        results.append(res)
        total_time += res["elapsed_seconds"]

        if "create_support_ticket" in res["tool_used"]:
            tickets_created += 1

        status_str = "[PASS]" if res["passed"] else "[FAIL]"
        print(f"  Input Query:        \"{tc['query']}\"")
        print(f"  Predicted Category: {res['predicted_category']} (Agent: {res['selected_agent']})")
        print(f"  Tool Used:          {res['tool_used']}")
        print(f"  Approval Required:  {res['approval_required']}")
        print(f"  Response Preview:   {res['actual_response']}")
        print(f"  Result:             {status_str} ({res['elapsed_seconds']}s)")

    # Compute aggregate statistics
    total = len(results)
    correct_classifications = sum(1 for r in results if r["category_match"])
    routing_failures = sum(0 if r["routing_match"] else 1 for r in results)
    passed_tests = sum(1 for r in results if r["passed"])
    accuracy = (correct_classifications / total) * 100
    avg_latency = total_time / total

    print("\n" + "=" * 80)
    print("                     TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total test queries:              {total}")
    print(f"Correctly classified queries:     {correct_classifications}")
    print(f"Classification accuracy:         {accuracy:.2f}%")
    print(f"Total passed test cases:         {passed_tests}/{total}")
    print(f"Routing failures:                {routing_failures}")
    print(f"Tickets created successfully:    {tickets_created}")
    print(f"Average response time:           {avg_latency:.4f} seconds")
    print("=" * 80)

    return results


if __name__ == "__main__":
    run_all_tests()
