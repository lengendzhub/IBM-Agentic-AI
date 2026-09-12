# IBM Agentic AI Internship Project Report

**Project Title**: Intelligent HR Equipment Support Assistant Using LangChain and LangGraph  
**Student Name**: Marimuthu  
**Institution**: Holycross Engineering College  
**Register Number**: 95092310429  
**Domain**: Agentic AI, LangChain, LangGraph, Tools, Memory, SQLite, Human-in-the-Loop, MCP  
**Submission Date**: September 2026  
**GitHub Repository**: https://github.com/lengendzhub/IBM-Agentic-AI  

---

# Project Overview

### Project Title
**Intelligent HR Equipment Support Assistant Using LangChain and LangGraph**

### Problem Statement
Employees in modern organizations frequently encounter disruptions related to office laptops, software installations, corporate Wi-Fi connectivity, forgotten passwords, portal access permissions, printers, and external peripherals. In conventional workplace settings, employees are forced to manually contact HR or IT service desk representatives for every issue—even routine, well-documented technical glitches that follow standard diagnostic procedures.

This manual approach introduces several systemic challenges:
1. **Prolonged Support Delays**: IT personnel are inundated with routine tickets, leading to queue backlogs and decreased organizational productivity.
2. **Misrouting and Repeated Queries**: Inexperienced employees frequently misclassify their issues, routing software bugs to hardware queues or access requests to general HR, resulting in manual reassignment delays.
3. **Absence of Contextual Memory**: Traditional rule-based chatbots treat every query in isolation. If an employee reported an application crash two days prior, standard chatbots cannot correlate the previous issue with a recurring error.
4. **Security Vulnerabilities in Autonomous Actions**: Fully autonomous systems risk executing dangerous operations without oversight—such as unauthorized password resets, granting privileged database access, or approving expensive laptop purchases.

While a conventional chatbot provides only static, predetermined responses, an **Agentic AI** system understands user intent, classifies issues dynamically, maintains short-term conversational context and long-term employee memory, executes operational tools, and routes high-risk tasks to human decision-makers.

### Brief Description of the Project
The **Intelligent HR Equipment Support Assistant** is an end-to-end, enterprise-grade Agentic AI application designed to triage, troubleshoot, and resolve employee HR and IT equipment issues.

The assistant accepts natural-language employee queries such as:
- *"My laptop is not turning on."*
- *"My office Wi-Fi is not connecting on the 3rd floor."*
- *"The payroll application crashes whenever I open it."*
- *"I forgot my employee portal password."*
- *"I need access to the attendance system."*
- *"How can I apply for leave?"*
- *"What is the status of ticket TKT-12345678?"*

Upon receiving a query, the assistant executes a structured workflow:
1. Sanitizes user input and validates employee identity using **Pydantic**.
2. Loads conversational history and long-term preferences from an **SQLite database**.
3. Classifies the query into one of four functional categories: **Hardware**, **Technical**, **Access**, or **General HR**.
4. Routes the request across specialized domain agents managed by a **LangGraph StateGraph**.
5. Executes diagnostic tools, retrieves Standard Operating Procedures (SOPs), creates database support tickets, or triggers **Human-in-the-Loop (HITL)** approvals.
6. Synchronizes updated memory state and delivers a structured, actionable markdown response.

The project incorporates the foundational concepts taught during the IBM Agentic AI internship: **Large Language Models, Tools & Tool Calling, Short-Term and Long-Term Memory, LangChain, LangGraph State Graphs, Query Classification, Conditional Routing, Specialized Agents, SQLite Persistence, Human-in-the-Loop Approval, and Model Context Protocol (MCP)**.

---

# Objectives & Proposed Solution

### Project Objectives
The primary objectives of this project are:
- **Build a Practical Agentic AI Application**: Develop an operational, production-ready assistant for corporate HR and IT equipment support.
- **Autonomous Intent Classification**: Accurately categorize employee queries into domain categories using a hybrid semantic and pattern-matching classifier.
- **Conditional Routing via LangGraph**: Orchestrate multi-agent control flow using a cyclic, compiled `StateGraph` with conditional edges.
- **Real-World Operational Tools**: Implement tools for support ticket generation, ticket status querying, ISO date-time lookup, safe AST mathematical calculation, text diagnostics, and SOP knowledge base retrieval.
- **Dual-Layer Memory Architecture**: Maintain short-term turn context within the workflow state and store persistent employee history (department, past issues, preferences) in an SQLite database.
- **Human-in-the-Loop (HITL) Governance**: Halt autonomous execution for high-risk operations (credential resets, privilege provisioning, expensive equipment replacement) and generate trackable approval tokens (`APP-XXXXXX`).
- **Input Validation & Secure Coding**: Enforce Pydantic validation schemas and AST-based evaluation, completely eliminating unsafe `eval()` or shell-command execution.
- **Interactive Delivery**: Provide both a modern **Streamlit Web Application** and an interactive **Terminal CLI** interface.
- **Complete Verification**: Implement an automated 12-scenario test suite demonstrating 100% classification accuracy and zero routing failures.

### How the Agentic AI Solution Works
The system architecture separates the decision-making brain (the model and classifier) from operational execution (tools and database drivers).

The system consists of a central router and four specialized agents:
1. **Hardware Agent**: Specializes in physical device diagnostics including laptops, keyboards, mice, printers, monitors, chargers, and batteries. Distinguishes routine troubleshooting from expensive asset replacements requiring managerial approval.
2. **Technical Agent**: Diagnoses software crashes, application freezes, operating-system errors, patch installations, and network/Wi-Fi drops. Cross-references long-term memory to detect recurring issues and escalate priority.
3. **Access Agent**: Manages password resets, account lockouts, employee portal access, and permission requests. Implements strict zero-trust security boundaries: never collects passwords and mandates human administrator verification for credential changes.
4. **General HR Agent**: Resolves company policy inquiries, leave application procedures, working hours, attendance regularizations, ticket status checks, and diagnostic calculations.

#### System Architecture Diagram
```
                     [ Employee Query ]
                             │
                             ▼
            [ Conversation Memory & SQLite Context ]
                             │
                             ▼
                 [ Query Classifier Node ]
                             │
            ┌────────────────┼────────────────┬────────────────┐
            ▼                ▼                ▼                ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │   Hardware   │ │  Technical   │ │    Access    │ │  General HR  │
     │    Agent     │ │    Agent     │ │    Agent     │ │    Agent     │
     └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
            │                │                │                │
            └────────────────┼────────────────┴────────────────┘
                             │
                Conditional Sub-Route Check
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [ Human-in-the-Loop ]             [ Create Ticket Tool ]
   (Sensitive Operations)            (Unresolved Issues)
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼
                   [ Final Response Node ]
                   (Memory Update & Display)
```

### Key Features
- **Natural-Language Understanding**: Interprets varied user inquiries without requiring rigid command syntax.
- **Pydantic Validation**: Strict schema enforcement for employee IDs and query content, preventing injection attacks.
- **Hybrid Intent Classification**: Seamlessly combines local LLM evaluation (Ollama / IBM Granite) with regex word-boundary fallback.
- **Conditional Routing**: Dynamic transitions across LangGraph nodes based on evolving conversational state.
- **Specialized Domain Agents**: Focused modular logic tailored to hardware, software, access, and HR policies.
- **Interactive Knowledge Base (SOPs)**: Standard operating diagnostic procedures for laptops, printers, Wi-Fi, BSOD, leave, and attendance.
- **Automated Ticket Generation**: Generates unique `TKT-XXXXXXXX` identifiers stored in SQLite with full metadata.
- **Ticket Status Tracking**: Immediate real-time status lookup (`Open`, `In Progress`, `Resolved`, `Closed`).
- **Persistent Memory (Short & Long-Term)**: Context preservation across conversation turns and long-term employee history.
- **Human-in-the-Loop Security Escrow**: Autonomous execution is suspended for sensitive actions until an administrator approves.
- **Safe AST Calculator**: Mathematical operations evaluated securely via Python Abstract Syntax Trees without `eval()`.
- **Dual User Interface**: Visual Streamlit web app with interactive approval buttons and a headless Rich terminal CLI.
- **Automated Test Suite**: 12 automated verification scenarios with empirical accuracy reporting.

---

# Implementation & Results

### Technologies and Tools Used

| Layer | Component | Version | Role in Architecture |
|---|---|---|---|
| **Programming Language** | Python | 3.11.9 | Core implementation runtime |
| **Agent Orchestration** | LangGraph | 1.2.11 | StateGraph, conditional edges, node lifecycle management |
| **LLM Framework** | LangChain Core | 1.6.3 | Tool wrappers, prompt formatting, model interfaces |
| **Local LLM Integration** | LangChain Ollama | 1.1.0 | Local model execution (IBM Granite / Ollama) |
| **Data Validation** | Pydantic | 2.13.5 | Input sanitization, data models, enum definitions |
| **Relational Database** | SQLite3 | Native | Storage for tickets, employee profiles, and conversation logs |
| **Web User Interface** | Streamlit | 1.56.0 | Web interface with chat UI, memory inspector, and approval simulation |
| **Terminal Interface** | Rich | 14.3.3 | Formatted console tables, status badges, and CLI banners |
| **Development IDE** | Visual Studio Code | 1.90+ | Source code editing, debugging, and terminal execution |
| **Version Control** | Git / GitHub | 2.40+ | Repository hosting, versioning, and project submission |
| **Agent Protocol** | MCP Concepts | 2024 Spec | Standardized Model Context Protocol tool/resource architecture |

---

### Working Process
The end-to-end execution of a support request follows twelve structured stages:

```
Step 01: Employee submits query via Streamlit or Terminal interface.
Step 02: Pydantic validates input format and sanitizes HTML/script tags.
Step 03: SQLite retrieves employee's long-term profile and recent conversation turns.
Step 04: SupportState is initialized with query, employee ID, and historical memory.
Step 05: The `classify_query` node assigns a category (hardware, technical, access, general) and priority.
Step 06: LangGraph `route_query` sends the state to the appropriate specialized agent node.
Step 07: Specialized agent analyzes the problem and queries the SOP knowledge base.
Step 08: Agent evaluates security: if action is sensitive or costly, flags `approval_required = True`.
Step 09: Conditional edge routes state:
         - To `human_approval` if approval is required.
         - To `create_ticket` if diagnostics recommend support dispatch.
         - Directly to `final_response` if query is resolved or informational.
Step 10: Tool executes action:
         - Ticket tool writes new record to SQLite `support_tickets` table.
         - Approval node records pending token in `approval_requests` table.
Step 11: `final_response` node updates SQLite `conversation_logs` and long-term memory.
Step 12: Final structured markdown response is presented to the employee.
```

---

### Screenshots / Output

#### 1. Hardware Support & Ticket Creation (Terminal Output)
```text
===========================================================================
  Intelligent HR Equipment Support Assistant (IBM Agentic AI)
===========================================================================
  Backend: OLLAMA (Model: granite3-dense:8b)
  Ollama Daemon Status: HYBRID_ACTIVE
===========================================================================

Logged in as: EMP1024 | Department: Finance | Language: English

[EMP1024] > My laptop is not turning on.

  [Routing query through LangGraph multi-agent workflow...]
  [Category]: HARDWARE  |  [Agent]: Hardware Agent  |  [Priority]: HIGH
---------------------------------------------------------------------------
Hello EMP1024, (Department: Finance)

I understand you are experiencing an issue with your hardware equipment: "My laptop is not turning on.".

### Laptop Power & Boot Diagnostics:
1. Connect the original OEM charger and check if the charging LED indicator lights up.
2. If no light appears, test with another known-working power outlet or compatible adapter.
3. Perform a hard reset: Unplug the charger, hold the power button down firmly for 30 seconds, then reconnect and try turning it on.
4. If connected to a docking station, disconnect all peripherals and attempt to power on directly.
5. If the laptop still does not respond, a hardware inspection or battery replacement ticket is required.

💡 If the issue persists after performing the diagnostics above, a hardware support ticket will be created automatically for IT technician dispatch.

---
### 🎫 Support Ticket Generated Successfully
- **Ticket ID**: `TKT-412C85A3`
- **Employee ID**: EMP1024
- **Category**: Hardware
- **Priority**: High
- **Status**: **Open**
- **Created At**: 2026-09-12 14:48:40
- **Description**: My laptop is not turning on.
You can track this ticket anytime using: *"Status of ticket TKT-412C85A3"*
---------------------------------------------------------------------------
```

#### 2. Technical Support with Long-Term Memory Correlation
```text
[EMP1024] > The payroll application crashes whenever I open it.

  [Routing query through LangGraph multi-agent workflow...]
  [Category]: TECHNICAL  |  [Agent]: Technical Agent  |  [Priority]: HIGH
---------------------------------------------------------------------------
Hello EMP1024,
I have received your technical support inquiry: "The payroll application crashes whenever I open it.".
⚠️ *Note: I see you experienced payroll software difficulties recently. Escalating priority.*

### Recommended Actions for Application Crash & Error Resolution:
1. Open Windows Task Manager (Ctrl + Shift + Esc) and terminate any lingering background instances of the application.
2. Clear application temporary cache files located in %LOCALAPPDATA% or %TEMP%.
3. Verify that your system has the latest mandatory security patches installed via Software Center.
4. Restart your workstation to release locked memory handles.
5. If the error code persists (e.g., 0x8004), provide the exact error message and raise a technical support ticket.

📌 If these steps do not clear the error code or connectivity issue, a technical support ticket will be created and assigned to desktop support.

---
### 🎫 Support Ticket Generated Successfully
- **Ticket ID**: `TKT-F2183020`
- **Employee ID**: EMP1024
- **Category**: Technical
- **Priority**: High
- **Status**: **Open**
- **Created At**: 2026-09-12 14:49:30
- **Description**: The payroll application crashes whenever I open it.
You can track this ticket anytime using: *"Status of ticket TKT-F2183020"*
---------------------------------------------------------------------------
```

#### 3. Access Request with Mandatory Human-in-the-Loop Approval
```text
[EMP1024] > I forgot my employee portal password.

  [Routing query through LangGraph multi-agent workflow...]
  [Category]: ACCESS  |  [Agent]: Access Agent  |  [Priority]: MEDIUM
  [Notice]: Human-in-the-loop approval required for this action.
---------------------------------------------------------------------------
Hello EMP1024,
Regarding your access and account request: "I forgot my employee portal password.".

🔒 **Security Notice**: For your protection and organizational compliance, passwords and sensitive authentication tokens must NEVER be shared in chat.

### Password Reset Protocol:
1. Navigate to the self-service Identity Management Portal at https://identity.ibm-internal.corp/reset.
2. Enter your Employee ID and complete the Multi-Factor Authentication (MFA) push on Duo / Microsoft Authenticator.
3. Ensure the new password meets security requirements: minimum 14 characters, uppercase, lowercase, numeric, and symbol.
4. NOTE: For security policies, automated agents cannot directly view, generate, or send passwords over chat.
5. If MFA is unavailable or your account is hard-locked, an authenticated IT Administrator must approve and process the reset.

⚠️ **Human-in-the-Loop Approval Required**: Because this involves credential reset or access provisioning, an authorization request has been routed to your departmental IT Administrator / Manager.

---
### 🛡️ Human-in-the-Loop Security Escalation
- **Approval Request ID**: `APP-3A96B0`
- **Action Type**: `ACCESS_SENSITIVE_ACTION`
- **Current Status**: **Pending Human Verification**
Because this action involves access credentials, account security, or high-value asset replacement, it cannot be completed autonomously. An authorized IT Administrator or reporting manager must approve request APP-3A96B0 before changes take effect.
---------------------------------------------------------------------------
```

#### 4. Support Ticket Status Tracking
```text
[EMP1024] > What is the status of ticket TKT-12345678?

  [Routing query through LangGraph multi-agent workflow...]
  [Category]: GENERAL  |  [Agent]: General Agent  |  [Priority]: MEDIUM
---------------------------------------------------------------------------
### 📋 Support Ticket Details:
- **Ticket ID**: TKT-12345678
- **Employee ID**: EMP1024
- **Category**: TECHNICAL
- **Priority**: High
- **Status**: **In Progress**
- **Description**: Payroll application crashed on launch error code 0x8004
- **Created At**: 2026-09-12 14:41:45
- **Last Updated**: 2026-09-12 14:41:45
---------------------------------------------------------------------------
```

#### 5. Streamlit Web Dashboard Interface
The Streamlit interface provides:
- **Left Sidebar**:
  - Employee profile card showing Department, Preferred Language, and total interactions.
  - Collapsible history of previous issues from SQLite long-term memory.
  - Real-time LLM backend status badge (Ollama / Hybrid Fallback).
  - Interactive Support Ticket Lookup tool (search by `TKT-XXXXXXXX`).
  - Safe Calculator utility tool.
- **Main Chat Area**:
  - IBM blue header banner with Agentic AI indicator.
  - Quick-prompt buttons for instant sample queries.
  - Colorized category badges for each agent:
    - 🟦 `HARDWARE AGENT` (#0F62FE)
    - 🟪 `TECHNICAL AGENT` (#8A3FFC)
    - 🟥 `ACCESS AGENT` (#FA4D56)
    - 🟩 `GENERAL AGENT` (#007D79)
  - Interactive **[Simulate Admin Approval ✅]** and **[Reject Request ❌]** buttons for testing HITL approval workflows.

---

### Results Achieved

The system underwent exhaustive testing using the automated test suite `tests/test_cases.py`.

#### Empirical Evaluation Metrics

$$\text{Classification Accuracy} = \frac{\text{Correctly Classified Queries}}{\text{Total Queries}} \times 100 = \frac{12}{12} \times 100 = 100.00\%$$

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

#### Detailed Test Case Execution Matrix

| # | Test Scenario | Input Query | Predicted Category | Selected Agent | Tool Executed | Approval Required? | Status |
|---|---|---|---|---|---|---|---|
| **01** | Laptop Failure | *"My laptop is not turning on."* | `hardware` | `hardware_agent` | `create_support_ticket` | False | **PASS** |
| **02** | Printer Failure | *"Office printer is not printing and showing error light."* | `hardware` | `hardware_agent` | `create_support_ticket` | False | **PASS** |
| **03** | Software Crash | *"The payroll application crashes whenever I open it."* | `technical` | `technical_agent` | `create_support_ticket` | False | **PASS** |
| **04** | Wi-Fi Connectivity | *"My office Wi-Fi is not connecting on the 3rd floor."* | `technical` | `technical_agent` | `create_support_ticket` | False | **PASS** |
| **05** | Password Reset | *"I forgot my employee portal password."* | `access` | `access_agent` | `human_approval` | **True** | **PASS** |
| **06** | Portal Access Request | *"I need access to the attendance system."* | `access` | `access_agent` | `human_approval` | **True** | **PASS** |
| **07** | Leave Enquiry | *"How can I apply for leave?"* | `general` | `general_agent` | `search_troubleshooting` | False | **PASS** |
| **08** | Ticket Status Lookup | *"What is the status of ticket TKT-12345678?"* | `general` | `general_agent` | `check_ticket_status` | False | **PASS** |
| **09** | Out-of-Scope Query | *"What is the meaning of life?"* | `general` | `general_agent` | `search_troubleshooting` | False | **PASS** |
| **10** | Laptop Replacement | *"I need a new laptop, mine is broken and cannot be repaired."* | `hardware` | `hardware_agent` | `human_approval` | **True** | **PASS** |
| **11** | Monitor Failure | *"My monitor screen is blank and flickering when connected via HDMI."* | `hardware` | `hardware_agent` | `human_approval` | **True** | **PASS** |
| **12** | Working Hours Policy | *"What are the standard office working hours and shift timings?"* | `general` | `general_agent` | `search_troubleshooting` | False | **PASS** |

---

# Conclusion & Future Scope

### Project Conclusion
The **Intelligent HR Equipment Support Assistant** represents a comprehensive, practical implementation of Agentic AI principles covered during the IBM internship.

Rather than relying on a monolithic question-answering prompt, the project decouples intelligence into:
1. **The Brain (Decision-Making)**: LLM and classification logic that understand user queries, evaluate intent, and determine urgency.
2. **The Graph (Workflow Coordination)**: LangGraph state machine orchestrating nodes, conditional edges, and sub-routines.
3. **The Tools (Execution)**: Deterministic Python tools executing support ticket creation, ticket status checks, safe AST calculations, and SOP searches.
4. **The Memory (Persistence)**: Short-term turn memory and persistent long-term SQLite employee profiles.
5. **The Governance (HITL Safeguards)**: Human approval checkpoints ensuring sensitive credential resets and costly asset replacements are verified before completion.

This architecture ensures that enterprise automation remains reliable, deterministic, transparent, and aligned with corporate security policies.

### Challenges Faced
During development, thirteen significant engineering challenges were addressed:
1. **Conceptual Separation of Agentic Layers**: Differentiating between models (decision engines), tools (execution units), agents (specialized personas), and workflows (state graphs).
2. **LangChain 1.4 StructuredTool Invocation**: Functions decorated with `@tool` convert into `StructuredTool` objects that cannot be invoked directly as standard Python functions. This was resolved by dual-exporting native Python functions alongside `@tool` wrappers.
3. **Substring Collisions in Intent Classification**: Unbounded keyword searches caused queries like `"apply for leave"` to match `"app"` (software) and `"laptop"` to match `"pto"` (leave). Resolved by implementing regex word boundary assertions (`\b`) and domain disambiguation rules.
4. **Ollama Daemon Socket Timeouts**: When the local Ollama daemon was offline, `ChatOllama` hung for 30–60 seconds per query on socket timeouts. Resolved by creating `is_ollama_online()`, a 0.2-second socket probe enabling zero-latency fallback.
5. **Windows Console Encoding Crashes**: Windows PowerShell default encoding (`cp1252`) threw `UnicodeEncodeError` when rendering emojis (✅, 🎫, ⚠️). Resolved by wrapping `sys.stdout` in a UTF-8 `TextIOWrapper` with character replacement.
6. **AST Mathematical Evaluation Security**: Preventing arbitrary code injection without using Python's dangerous `eval()`. Solved via recursive AST node inspection restricted to binary arithmetic.
7. **Database Concurrency & SQLite Locking**: Handled by configuring `check_same_thread=False` and using Python context managers for transactional commits.
8. **State Schema Integrity**: Ensuring all dictionary keys in `SupportState` were consistently initialized to prevent `KeyError` during conditional routing.
9. **Credential Security Enforcement**: Ensuring the Access Agent strictly refuses to accept or store plaintext passwords.
10. **Dynamic Ticket Generation**: Generating cryptographically sound, collision-free identifiers using truncated UUID4 strings (`TKT-XXXXXXXX`).
11. **Streamlit Execution on Windows**: Resolving PowerShell's `CommandNotFoundException` by documenting and supporting `python -m streamlit run app.py`.
12. **Model Context Protocol (MCP) Design**: Architecting tools and resources according to JSON-RPC MCP standards for future client-server modularity.
13. **Balancing Autonomous Help with Human Oversight**: Designing explicit approval criteria so routine troubleshooting remains autonomous while sensitive actions halt for human sign-off.

### Future Enhancements
Future iterations of the system can incorporate:
- **IBM watsonx.ai Granite 3.0 Integration**: Direct API integration with enterprise IBM Cloud watsonx.ai foundation models.
- **Enterprise RAG via ChromaDB / Milvus**: Vector embedding of official corporate policy handbooks, IT hardware manuals, and benefit guides for semantic passage retrieval.
- **ServiceNow & Jira Service Desk Integration**: REST API webhooks synchronizing generated tickets directly with enterprise ITSM platforms.
- **Multilingual Support**: Real-time translation supporting global enterprise languages (English, Tamil, Hindi, Spanish).
- **Enterprise Voice Assistant**: Speech-to-text integration using Whisper models for hands-free factory and warehouse employee assistance.
- **Active Directory / SSO Authentication**: SAML 2.0 or OAuth2 authentication to verify employee identity automatically.
- **Executive Analytics Dashboard**: Streamlit metrics tracking resolution times, top equipment failure types, and agent utilization rates.

---

### References
1. **IBM Agentic AI Internship Modules**: Video lectures, hands-on tutorials, and official curriculum materials.
2. **IBM watsonx.ai Documentation**: Foundation models, IBM Granite architectures, and prompt engineering guides.
3. **LangChain Documentation**: Official Python API reference ([https://python.langchain.com/](https://python.langchain.com/)).
4. **LangGraph Documentation**: StateGraph concepts, cyclic graphs, and conditional edge routing ([https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)).
5. **Pydantic Documentation**: Data validation and settings management ([https://docs.pydantic.dev/](https://docs.pydantic.dev/)).
6. **SQLite3 Standard Library Specification**: Transaction management and row factories ([https://www.sqlite.org/](https://www.sqlite.org/)).
7. **Model Context Protocol (MCP)**: Open specification for AI client-server integration ([https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)).
8. **Streamlit Python Library**: UI components, session state, and layout design ([https://docs.streamlit.io/](https://docs.streamlit.io/)).

---

*Submitted in partial fulfillment of the requirements for the IBM Agentic AI Internship Program.*
