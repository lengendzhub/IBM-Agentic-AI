"""
app.py
Intelligent HR Equipment Support Assistant
Integrated Streamlit Web Application and Terminal CLI Interface.

Supports:
- Ollama local model / IBM Granite / watsonx.ai
- LangChain & LangGraph Multi-Agent Orchestration
- Short-term conversation history and SQLite long-term memory
- Tool calling: Ticketing, Knowledge Base SOPs, Safe Calculator, Word Count
- Human-in-the-Loop (HITL) approval workflows
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List

# Ensure project directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from models.schemas import EmployeeQuery, IssueCategory
from memory.database import get_db
from workflow.graph import run_support_agent
from tools.ticket_tools import check_ticket_status, list_employee_tickets
from tools.utility_tools import safe_calculator, word_count, get_current_datetime
from agents.classifier import is_ollama_online, OLLAMA_MODEL, LLM_BACKEND


# ==============================================================================
# Terminal CLI Interface
# ==============================================================================

def run_terminal_mode():
    """Runs an interactive terminal CLI interface with rich formatting."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.markdown import Markdown
        from rich.prompt import Prompt, Confirm
        console = Console()
    except ImportError:
        console = None

    print("\n" + "=" * 75)
    print("  Intelligent HR Equipment Support Assistant (IBM Agentic AI)")
    print("=" * 75)
    print(f"  Backend: {LLM_BACKEND.upper()} (Model: {OLLAMA_MODEL})")
    print(f"  Ollama Daemon Status: {'ONLINE' if is_ollama_online() else 'OFFLINE (Using Rule/Pattern Fallback)'}")
    print("=" * 75 + "\n")

    emp_id = input("Enter your Employee ID [Default: EMP1024]: ").strip().upper()
    if not emp_id:
        emp_id = "EMP1024"

    db = get_db()
    profile = db.get_employee_memory(emp_id)
    print(f"Logged in as: {emp_id} | Department: {profile.get('department')} | Language: {profile.get('preferred_language')}\n")
    print("Type your support issue below. Type 'exit' or 'quit' to end.\n")

    while True:
        try:
            query = input(f"[{emp_id}] > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting Assistant. Have a productive day!")
                break

            # Validate input using Pydantic
            try:
                validated = EmployeeQuery(employee_id=emp_id, query=query)
            except Exception as val_err:
                print(f"[Input Error]: {val_err}\n")
                continue

            print("\n  [Routing query through LangGraph multi-agent workflow...]")
            state = run_support_agent(employee_id=validated.employee_id, query=validated.query)

            category = state.get("category", "general")
            agent_name = f"{category.capitalize()} Agent"
            priority = state.get("priority", "medium")
            approval = state.get("approval_required", False)

            print(f"  [Category]: {category.upper()}  |  [Agent]: {agent_name}  |  [Priority]: {priority.upper()}")
            if approval:
                print("  [Notice]: Human-in-the-loop approval required for this action.")

            print("-" * 75)
            print(state.get("final_answer", "No answer generated."))
            print("-" * 75 + "\n")

        except KeyboardInterrupt:
            print("\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"[System Error]: {str(e)}\n")


# ==============================================================================
# Streamlit Web Application Interface
# ==============================================================================

def run_streamlit_app():
    """Renders the modern, responsive Streamlit Web UI."""
    import streamlit as st

    st.set_page_config(
        page_title="HR & Equipment Support Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.1rem;
            font-weight: 700;
            color: #0F62FE;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #525252;
            margin-bottom: 1.2rem;
        }
        .badge-hardware { background-color: #0F62FE; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .badge-technical { background-color: #8A3FFC; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .badge-access { background-color: #FA4D56; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .badge-general { background-color: #007D79; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .stAlert { border-radius: 8px; }
        </style>
    """, unsafe_allow_html=True)

    db = get_db()

    # --------------------------------------------------------------------------
    # Sidebar: Profile, Memory, Tickets, HITL Approvals
    # --------------------------------------------------------------------------
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=110)
        st.markdown("### 👤 Employee Profile & Memory")

        # Employee selection
        default_employees = ["EMP1024", "EMP1025", "EMP1026", "EMP5501", "New Employee..."]
        selected_emp = st.selectbox("Select Employee Session", default_employees, index=0)

        if selected_emp == "New Employee...":
            employee_id = st.text_input("Enter Employee ID", value="EMP2026").strip().upper()
        else:
            employee_id = selected_emp

        # Fetch Long-term memory
        emp_memory = db.get_employee_memory(employee_id)
        st.markdown(f"**Department**: `{emp_memory.get('department', 'General')}`")
        st.markdown(f"**Language**: `{emp_memory.get('preferred_language', 'English')}`")
        st.markdown(f"**Interactions**: `{emp_memory.get('interaction_count', 0)}`")

        with st.expander("📜 Recent Issues History", expanded=False):
            prev_issues = emp_memory.get("previous_issues", [])
            if prev_issues:
                for issue in prev_issues[-4:]:
                    st.caption(f"• {issue}")
            else:
                st.caption("No previous issues on record.")

        st.divider()

        # Backend Status
        st.markdown("### ⚙️ Agentic AI Backend")
        ollama_status = is_ollama_online()
        if ollama_status:
            st.success(f"🟢 Ollama Online ({OLLAMA_MODEL})")
        else:
            st.info(f"⚪ Hybrid Fallback Active (Ollama Offline on :11434)")
        st.caption("Architecture: LangGraph StateGraph (8 Nodes, Conditional Routing)")

        st.divider()

        # Ticket Lookup Tool Widget
        st.markdown("### 🔍 Support Ticket Lookup")
        tkt_search = st.text_input("Lookup Ticket ID", placeholder="TKT-12345678").strip().upper()
        if st.button("Check Ticket", use_container_width=True):
            if tkt_search:
                tkt_info = check_ticket_status(tkt_search)
                if tkt_info.get("status") == "Ticket not found":
                    st.warning(f"No ticket found matching `{tkt_search}`.")
                else:
                    st.success(f"**Ticket Found**: `{tkt_info['status']}`")
                    st.write(tkt_info)
            else:
                st.error("Please enter a valid ticket number.")

        # Employee Tickets List
        with st.expander("📋 My Support Tickets", expanded=False):
            tickets = db.list_employee_tickets(employee_id)
            if tickets:
                for t in tickets:
                    st.markdown(f"**`{t['ticket_id']}`** — {t['status']}")
                    st.caption(f"*{t['category'].upper()}* | {t['description'][:50]}...")
            else:
                st.caption("No support tickets raised yet.")

        # Safe Calculator Widget
        with st.expander("🧮 Utility: Safe Calculator", expanded=False):
            calc_expr = st.text_input("Expression", value="65000 * 1.18")
            if st.button("Calculate", key="calc_btn"):
                calc_res = safe_calculator(calc_expr)
                if calc_res.get("success"):
                    st.write(f"Result: **{calc_res['result']}**")
                else:
                    st.error(calc_res.get("error"))

    # --------------------------------------------------------------------------
    # Main Chat Area
    # --------------------------------------------------------------------------
    st.markdown('<div class="main-header">Intelligent HR Equipment Support Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">LangChain & LangGraph Multi-Agent System with Short-Term Memory, SQLite Long-Term Memory, and HITL Approval.</div>', unsafe_allow_html=True)

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Quick prompt pills
    st.markdown("**Quick Prompts:**")
    cols = st.columns(5)
    sample_prompts = [
        "My laptop is not turning on.",
        "Office printer is not printing.",
        "Payroll application crashes.",
        "I forgot my portal password.",
        "How can I apply for leave?"
    ]
    prompt_to_submit = None
    for i, p in enumerate(sample_prompts):
        if cols[i].button(p, key=f"quick_{i}"):
            prompt_to_submit = p

    # Render previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "category" in msg and msg["category"]:
                cat = msg["category"]
                st.markdown(f'<span class="badge-{cat}">{cat.upper()} AGENT</span>', unsafe_allow_html=True)
            st.markdown(msg["content"])

    # Handle user input (from chat input or quick prompt)
    user_query = st.chat_input("Describe your hardware, technical, access, or HR issue here...")
    if prompt_to_submit:
        user_query = prompt_to_submit

    if user_query:
        # Validate input with Pydantic
        try:
            validated = EmployeeQuery(employee_id=employee_id, query=user_query)
        except Exception as val_err:
            st.error(f"Input validation error: {str(val_err)}")
            return

        # Display user message
        st.session_state.messages.append({"role": "user", "content": validated.query})
        with st.chat_message("user"):
            st.markdown(validated.query)

        # Execute multi-agent graph
        with st.chat_message("assistant"):
            with st.spinner("Classifying and routing to specialized agent..."):
                state = run_support_agent(employee_id=validated.employee_id, query=validated.query)

            category = state.get("category", "general")
            final_answer = state.get("final_answer", "Request completed.")
            approval_needed = state.get("approval_required", False)

            # Display agent category badge
            st.markdown(f'<span class="badge-{category}">{category.upper()} AGENT</span>', unsafe_allow_html=True)
            st.markdown(final_answer)

            # Interactive Human Approval confirmation widget in UI
            if approval_needed:
                st.warning("⚠️ **Action Blocked**: Requires Human-in-the-Loop Administrator Approval.")
                col_app1, col_app2 = st.columns([1, 4])
                with col_app1:
                    if st.button("Simulate Admin Approval ✅", key=f"appr_{len(st.session_state.messages)}"):
                        st.success("Human authorization granted. Action completed and recorded.")
                with col_app2:
                    if st.button("Reject Request ❌", key=f"rej_{len(st.session_state.messages)}"):
                        st.error("Request rejected by Administrator.")

        # Save assistant message in session
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_answer,
            "category": category
        })


# ==============================================================================
# Main Entrypoint
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intelligent HR Equipment Support Assistant")
    parser.add_argument("--terminal", "-t", action="store_true", help="Launch in interactive terminal CLI mode")
    args, unknown = parser.parse_known_args()

    # Detect if invoked via `streamlit run` or with `--terminal`
    if args.terminal:
        run_terminal_mode()
    else:
        # If run directly with python (not streamlit), check if user wants terminal mode
        if "streamlit" in sys.modules or os.environ.get("STREAMLIT_SERVER_PORT") or (len(sys.argv) > 0 and "streamlit" in sys.argv[0]):
            run_streamlit_app()
        else:
            # When run as `python app.py`, launch terminal mode or inform about streamlit
            print("Tip: Run `streamlit run app.py` to start the interactive web interface.")
            print("Starting interactive terminal interface now...\n")
            run_terminal_mode()
