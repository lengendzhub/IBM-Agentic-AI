# Intelligent HR Equipment Support Assistant Using LangChain and LangGraph

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1.4%2B-green.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2%2B-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/SQLite-Long--Term%20Memory-003B57.svg)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)]()

> **IBM Agentic AI Internship Capstone Project**  
> An enterprise-grade, stateful multi-agent support ecosystem for automating HR and IT equipment troubleshooting, ticket generation, and managerial approvals.

---

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Specialized Agents](#-specialized-agents)
- [Tool Registry](#-tool-registry)
- [Dual-Layer Memory Architecture](#-dual-layer-memory-architecture)
- [Human-in-the-Loop (HITL) Security](#-human-in-the-loop-hitl-security)
- [Project Directory Structure](#-project-directory-structure)
- [Quick Start Guide](#-quick-start-guide)
- [Automated Test Suite & Results](#-automated-test-suite--results)
- [Model Context Protocol (MCP) Integration](#-model-context-protocol-mcp-integration)
- [GitHub Submission Instructions](#-github-submission-instructions)
- [License & References](#-license--references)

---

## 🚀 Project Overview

In corporate environments, employees encounter recurrent IT equipment failures (laptops not booting, printer jams, display errors) and technical roadblocks (application crashes, Wi-Fi drops, password lockouts). Handling every minor inquiry manually overwhelms IT and HR helpdesk personnel.

The **Intelligent HR Equipment Support Assistant** leverages **Agentic AI** to autonomously:
1. Classify incoming employee queries into discrete functional categories.
2. Route tickets via conditional edges to specialized domain agents.
3. Provide interactive Standard Operating Procedure (SOP) troubleshooting steps.
4. Execute tools for ticket creation, status checks, mathematical calculations, and diagnostic word counting.
5. Enforce **Human-in-the-Loop (HITL)** governance for sensitive operations (password resets, high-value asset replacements).
6. Maintain short-term turn context and persistent long-term employee memory in SQLite.

---

## 🏛️ System Architecture

The project is architected as an 8-node stateful workflow managed by **LangGraph**:

```
                 [START]
                    │
                    ▼
           ┌─────────────────┐
           │ classify_query  │ ◄─── Pydantic Sanitization & Intent Scoring
           └────────┬────────┘
                    │
       ┌────────────┼────────────┬────────────┐
       ▼            ▼            ▼            ▼
 ┌───────────┐┌───────────┐┌───────────┐┌───────────┐
 │ hardware  ││ technical ││  access   ││  general  │
 │   agent   ││   agent   ││   agent   ││   agent   │
 └─────┬─────┘└─────┬─────┘└─────┬─────┘└─────┬─────┘
       │            │            │            │
       └────────────┼────────────┴────────────┘
                    │
        Conditional Routing Check
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
 ┌──────────────┐          ┌──────────────┐
 │ human_approval│         │create_ticket │
 └──────┬───────┘          └──────┬───────┘
        │                         │
        └───────────┬─────────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ final_response  │ ◄─── SQLite Conversation Logging
           └────────┬────────┘
                    │
                    ▼
                  [END]
```

---

## ✨ Key Features

- **Pydantic Validation**: Input queries and Employee IDs are sanitized to prevent injection and malformed requests.
- **Hybrid Classifier**: Combines zero-latency regex word-boundary pattern matching with semantic LangChain LLM evaluation (Ollama / IBM Granite / watsonx.ai).
- **LangGraph StateGraph**: Explicit state container tracking `user_query`, `employee_id`, `category`, `priority`, `conversation_history`, `employee_memory`, `tool_result`, `approval_required`, and `final_answer`.
- **4 Specialized Agents**: Domain-focused prompt and diagnostic logic for Hardware, Technical, Access, and General HR inquiries.
- **Human-in-the-Loop (HITL)**: Safeguards enterprise systems by halting autonomous actions and issuing verifiable approval tokens (`APP-XXXXXX`) for high-value replacements or password changes.
- **Dual Interface**:
  - **Streamlit Web UI**: Interactive dashboard with profile lookups, ticket inspection, and one-click admin approval simulations.
  - **Terminal CLI**: Fast, headless CLI interface featuring colored banners and interactive prompts.

---

## 🤖 Specialized Agents

| Agent Node | Scope & Responsibilities | Sample Queries Handled |
|---|---|---|
| **`hardware_agent`** | Laptops, monitors, printers, keyboards, mice, chargers, batteries, docks. | *"My laptop is not turning on."*, *"Office printer is not printing."* |
| **`technical_agent`** | Software crashes, OS errors, patch installation, Wi-Fi, VPN, and network drops. | *"The payroll application crashes whenever I open it."*, *"Wi-Fi drops."* |
| **`access_agent`** | Password resets, account lockouts, MFA issues, system permission requests. | *"I forgot my employee portal password."*, *"Need attendance access."* |
| **`general_agent`** | Leave requests, attendance regularization, working hours, benefits, ticketing lookups. | *"How can I apply for leave?"*, *"Status of ticket TKT-12345678"*, *"Office hours?"* |

---

## 🛠️ Tool Registry

All tools are encapsulated as callable functions and registered as LangChain `@tool` instances:

1. **`create_support_ticket(employee_id, category, description, priority)`**: Generates unique `TKT-XXXXXXXX` tickets stored in SQLite.
2. **`check_ticket_status(ticket_id)`**: Queries ticket status (`Open`, `In Progress`, `Resolved`, `Closed`) from SQLite.
3. **`list_employee_tickets(employee_id)`**: Retrieves all tickets filed by a specific employee.
4. **`search_troubleshooting(query, category)`**: Searches built-in Standard Operating Procedure (SOP) diagnostic knowledge base.
5. **`safe_calculator(expression)`**: Secure mathematical expression evaluator built on Python AST (strictly blocks `eval`, `exec`, and OS calls).
6. **`word_count(text)`**: Computes word, character, and sentence counts for diagnostic logs.
7. **`get_current_datetime()`**: Formatted ISO datetime for SLA calculations.

---

## 🧠 Dual-Layer Memory Architecture

1. **Short-Term Memory (Session History)**:
   - Tracks ongoing conversational turns within the `conversation_history` list in `SupportState`.
   - Persisted across turns into SQLite `conversation_logs` table for session recovery.
2. **Long-Term Memory (Employee Profile)**:
   - Stored in SQLite `employee_memory` table (`preferred_language`, `department`, `previous_issues` JSON list, `interaction_count`).
   - Automatically loaded upon login; e.g., alerts agents if an employee experienced repeated application crashes in the past.

---

## 🛡️ Human-in-the-Loop (HITL) Security

To prevent unauthorized privileges and budget leakage, the workflow routes to `human_approval` when:
- Password resets or account unlock requests are submitted.
- Application access or elevated administrative roles are requested.
- Hardware replacement requests involve high-value capital assets (e.g., laptops, monitors).
- Equipment purchase approvals or sensitive employee data transfers are detected.

---

## 📂 Project Directory Structure

```text
project/
├── app.py                      # Main entrypoint: Streamlit Web UI + Terminal CLI
├── agents/                     # Specialized LangGraph agent nodes
│   ├── __init__.py
│   ├── classifier.py           # Intent classifier & conditional router
│   ├── hardware_agent.py       # Hardware troubleshooting & replacement agent
│   ├── technical_agent.py      # Software & network diagnostics agent
│   ├── access_agent.py         # Credential & privilege management agent
│   └── general_agent.py        # HR policies & general queries agent
├── tools/                      # LangChain tool registry
│   ├── __init__.py
│   ├── ticket_tools.py         # SQLite ticket CRUD tools
│   ├── utility_tools.py        # AST safe calculator, word count, datetime
│   └── knowledge_tools.py      # SOP troubleshooting knowledge base
├── memory/                     # Long-term and short-term persistence
│   ├── __init__.py
│   └── database.py             # SQLite database manager & data seeder
├── workflow/                   # LangGraph graph orchestration
│   ├── __init__.py
│   └── graph.py                # 8-node compiled LangGraph StateGraph
├── models/                     # Schema definitions & validation
│   ├── __init__.py
│   └── schemas.py              # Pydantic schemas & SupportState TypedDict
├── data/                       # Persistent database storage
│   ├── .gitkeep
│   └── support.db              # SQLite database (auto-generated)
├── tests/                      # Automated test suite
│   ├── __init__.py
│   └── test_cases.py           # 12 scenario test suite with empirical metrics
├── requirements.txt            # Pinned dependency manifest
├── .env.example                # LLM and backend configuration template
├── .gitignore                  # Git tracking exclusion rules
├── README.md                   # Project documentation & setup guide
└── report.md                   # Comprehensive formal internship submission report
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10 or 3.11 installed.
- Git installed.
- (Optional) [Ollama](https://ollama.ai/) installed with `granite3-dense:8b` or `llama3.2:3b`.

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/<your-username>/intelligent-hr-equipment-support-assistant.git
cd intelligent-hr-equipment-support-assistant/project
pip install -r requirements.txt
```

### 3. Launching the Application

#### Option A: Streamlit Web Dashboard (Recommended)
```bash
python -m streamlit run app.py
```
*(Or `streamlit run app.py` if Scripts is on your PATH)*
Open your browser at `http://localhost:8501`.

#### Option B: Interactive Terminal CLI Mode
```bash
python app.py --terminal
```

---

## 🧪 Automated Test Suite & Results

Execute the complete 12-scenario test suite:
```bash
python -m tests.test_cases
```

### Empirical Test Execution Results

| # | Test Scenario | Predicted Category | Selected Agent | Tool Executed | Approval Required? | Status |
|---|---|---|---|---|---|---|
| **01** | Laptop Failure | `hardware` | `hardware_agent` | `create_support_ticket` | No | **PASS** |
| **02** | Printer Failure | `hardware` | `hardware_agent` | `create_support_ticket` | No | **PASS** |
| **03** | Software Crash | `technical` | `technical_agent` | `create_support_ticket` | No | **PASS** |
| **04** | Wi-Fi Connectivity | `technical` | `technical_agent` | `create_support_ticket` | No | **PASS** |
| **05** | Password Reset | `access` | `access_agent` | `human_approval` | **Yes** | **PASS** |
| **06** | Portal Access Request | `access` | `access_agent` | `human_approval` | **Yes** | **PASS** |
| **07** | Leave Application | `general` | `general_agent` | `search_troubleshooting` | No | **PASS** |
| **08** | Ticket Status Lookup | `general` | `general_agent` | `check_ticket_status` | No | **PASS** |
| **09** | Out-of-Scope Query | `general` | `general_agent` | `search_troubleshooting` | No | **PASS** |
| **10** | Laptop Replacement | `hardware` | `hardware_agent` | `human_approval` | **Yes** | **PASS** |
| **11** | Monitor Failure | `hardware` | `hardware_agent` | `human_approval` | **Yes** | **PASS** |
| **12** | Working Hours Policy | `general` | `general_agent` | `search_troubleshooting` | No | **PASS** |

```text
================================================================================
                     TEST EXECUTION SUMMARY
================================================================================
Total test queries:              12
Correctly classified queries:     12
Classification accuracy:         100.00%
Total passed test cases:         12/12
Routing failures:                0
Tickets created successfully:    4
Average response time:           0.0803 seconds
================================================================================
```

---

## 🌐 Model Context Protocol (MCP) Integration

The project architecture is designed to support **Model Context Protocol (MCP)** standards:
- **MCP Server**: Can wrap `tools/ticket_tools.py` and `memory/database.py` over standard JSON-RPC (stdio).
- **Exposed MCP Resources**: `support://tickets/{ticket_id}`, `support://employees/{employee_id}`.
- **Exposed MCP Tools**: `create_ticket`, `check_ticket`, `request_approval`.

---

## 📤 GitHub Submission Instructions

Follow these steps to submit this capstone project to GitHub:

1. **Initialize Git repository**:
   ```bash
   cd d:\Agentic AI-IBM\project
   git init
   ```
2. **Add files and create initial commit**:
   ```bash
   git add .
   git commit -m "feat: complete Intelligent HR Equipment Support Assistant implementation"
   ```
3. **Create a new repository on GitHub**:
   - Go to [github.com/new](https://github.com/new).
   - Name the repository: `intelligent-hr-equipment-support-assistant`.
   - Keep it Public.
4. **Push local code to remote**:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<your-github-username>/intelligent-hr-equipment-support-assistant.git
   git push -u origin main
   ```
5. **Capturing Screenshots for Submission**:
   - Run `streamlit run app.py` and capture screenshots of:
     - The main chat interface with routing badges.
     - The sidebar showing Employee Memory and Support Tickets.
     - A Human-in-the-Loop approval prompt.
   - Run `python -m tests.test_cases` and screenshot the 100% PASS summary table.
   - Place image files inside an `assets/` or `screenshots/` directory.

---

## 📚 References
1. IBM Agentic AI Internship Curriculum & Video Transcripts.
2. LangChain Documentation: [https://python.langchain.com/](https://python.langchain.com/)
3. LangGraph Framework Documentation: [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
4. Streamlit Python Documentation: [https://docs.streamlit.io/](https://docs.streamlit.io/)
5. Model Context Protocol (MCP) Specification: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)

---

*Submitted in partial fulfillment of the requirements for the IBM Agentic AI Internship Program.*
