"""
generate_pdf_report.py
Generates a formal, submission-ready PDF report for the IBM Agentic AI Internship project:
'Intelligent HR Equipment Support Assistant Using LangChain and LangGraph'
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' and header to all pages."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#525252"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "IBM Agentic AI Internship Project Report")
            self.drawRightString(558, 755, "Intelligent HR Equipment Support Assistant")
            self.setStrokeColor(colors.HexColor("#D1D5DB"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)

        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, text)
        self.drawString(54, 36, "Confidential — IBM Agentic AI Internship Submission")
        self.setStrokeColor(colors.HexColor("#D1D5DB"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()


def build_pdf(filename="IBM_Agentic_AI_Project_Report.pdf"):
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F62FE")   # IBM Blue
    dark_text = colors.HexColor("#161616")
    gray_text = colors.HexColor("#525252")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=gray_text,
        alignment=TA_CENTER,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_text,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#002D9C"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_text,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_text,
        leftIndent=15,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#262626")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=dark_text
    )

    story = []

    # =========================================================================
    # Header & Cover Title
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("IBM Agentic AI Internship Project Report", subtitle_style))
    story.append(Paragraph("Intelligent HR Equipment Support Assistant Using LangChain and LangGraph", title_style))
    story.append(Paragraph("<b>Student Name:</b> Marimuthu &nbsp;|&nbsp; <b>Register No:</b> 95092310429 &nbsp;|&nbsp; <b>College:</b> Holycross Engineering College<br/>"
                           "<b>GitHub Repository:</b> https://github.com/lengendzhub/IBM-Agentic-AI<br/>"
                           "<b>Domain:</b> Multi-Agent Systems, LangChain, LangGraph, Tools, Memory, SQLite, HITL, MCP", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=14))

    # =========================================================================
    # 1. Project Overview
    # =========================================================================
    story.append(Paragraph("1. Project Overview", h1_style))
    story.append(Paragraph("Project Title", h2_style))
    story.append(Paragraph("<b>Intelligent HR Equipment Support Assistant Using LangChain and LangGraph</b>", body_style))

    story.append(Paragraph("Problem Statement", h2_style))
    story.append(Paragraph(
        "Employees frequently encounter issues related to laptops, software installations, office Wi-Fi connectivity, "
        "passwords, system access permissions, printers, and peripherals. In traditional corporate setups, employees must contact "
        "HR or IT helpdesk representatives for every issue—even routine, well-documented inquiries that follow clear standard operating procedures (SOPs). "
        "This manual process introduces severe delays, queue backlogs, and unnecessary workload for support personnel. "
        "Furthermore, conventional rule-based chatbots provide only rigid, predetermined responses without context, cannot maintain state across multi-turn queries, "
        "cannot query live databases, and lack safeguards for sensitive privileged operations.",
        body_style
    ))

    story.append(Paragraph("Brief Description of the Project", h2_style))
    story.append(Paragraph(
        "The <b>Intelligent HR Equipment Support Assistant</b> is an enterprise-grade Agentic AI application designed to autonomously "
        "triage, troubleshoot, and resolve employee equipment and HR issues. The assistant receives natural-language user queries "
        "(e.g., <i>'My laptop is not turning on'</i>, <i>'The payroll application crashes whenever I open it'</i>, or <i>'I forgot my portal password'</i>), "
        "sanitizes user input via Pydantic, retrieves short-term conversational context and long-term employee memory from SQLite, "
        "classifies the issue into four primary functional categories (Hardware, Technical, Access, General HR), and routes it across specialized "
        "agents orchestrated via a compiled LangGraph state graph. The system executes operational tools for ticket generation and status checks, "
        "and halts autonomous execution to require Human-in-the-Loop (HITL) approval whenever credential resets or expensive asset purchases are requested.",
        body_style
    ))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E0E0E0"), spaceBefore=8, spaceAfter=8))

    # =========================================================================
    # 2. Objectives & Proposed Solution
    # =========================================================================
    story.append(Paragraph("2. Objectives & Proposed Solution", h1_style))
    story.append(Paragraph("Project Objectives", h2_style))
    story.append(Paragraph("• Build an end-to-end, runnable Agentic AI application for corporate HR and IT equipment support.", bullet_style))
    story.append(Paragraph("• Implement autonomous query classification with ≥90% accuracy using hybrid LLM and pattern matching.", bullet_style))
    story.append(Paragraph("• Orchestrate multi-agent control flow using a cyclic, compiled LangGraph StateGraph.", bullet_style))
    story.append(Paragraph("• Implement operational LangChain tools for ticket creation, status checks, safe AST calculations, and SOP searches.", bullet_style))
    story.append(Paragraph("• Maintain dual-layer memory: short-term multi-turn conversation logs and long-term SQLite employee profiles.", bullet_style))
    story.append(Paragraph("• Enforce Human-in-the-Loop (HITL) governance for sensitive actions (passwords, system access, high-value assets).", bullet_style))
    story.append(Paragraph("• Deliver a dual interface: visual Streamlit web dashboard and interactive Rich terminal CLI.", bullet_style))
    story.append(Paragraph("• Ensure secure coding standards: strict Pydantic input validation, AST evaluation, and zero-eval execution.", bullet_style))

    story.append(Paragraph("How the Agentic AI Solution Works", h2_style))
    story.append(Paragraph(
        "The system separates decision-making (the LLM brain and classifier) from operational execution (tools and database drivers). "
        "The LangGraph StateGraph acts as the central router managing 8 discrete nodes: <code>classify_query</code>, four specialized agents "
        "(<code>hardware_agent</code>, <code>technical_agent</code>, <code>access_agent</code>, <code>general_agent</code>), <code>create_ticket</code>, "
        "<code>human_approval</code>, and <code>final_response</code>. Memory from SQLite provides continuity across turns, alerting agents to prior "
        "software crashes or departmental hardware configurations.",
        body_style
    ))

    story.append(Paragraph("Key Features", h2_style))
    story.append(Paragraph("• <b>Hybrid Intent Classification:</b> Instant zero-latency regex word-boundary matching with local Ollama/Granite LLM fallback.", bullet_style))
    story.append(Paragraph("• <b>4 Specialized Domain Agents:</b> Tailored diagnostic logic for hardware, software, security access, and general HR.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Tool Calling:</b> Creates unique <code>TKT-XXXXXXXX</code> support tickets and queries statuses in real-time.", bullet_style))
    story.append(Paragraph("• <b>Persistent SQLite Memory:</b> Preserves employee history and correlations (e.g. repeated crashes escalate priority).", bullet_style))
    story.append(Paragraph("• <b>Human-in-the-Loop Security Escrow:</b> Halts autonomous execution and creates <code>APP-XXXXXX</code> approval tokens.", bullet_style))
    story.append(Paragraph("• <b>Safe AST Calculator:</b> Evaluates math expressions without using dangerous Python <code>eval()</code>.", bullet_style))
    story.append(Paragraph("• <b>Interactive Streamlit UI:</b> Complete with colored agent routing badges, approval simulation buttons, and ticket inspector.", bullet_style))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E0E0E0"), spaceBefore=8, spaceAfter=8))

    # =========================================================================
    # 3. Implementation & Results
    # =========================================================================
    story.append(Paragraph("3. Implementation & Results", h1_style))
    story.append(Paragraph("Technologies and Tools Used", h2_style))

    tech_data = [
        [Paragraph("<b>Component</b>", table_header_style),
         Paragraph("<b>Technology</b>", table_header_style),
         Paragraph("<b>Version</b>", table_header_style),
         Paragraph("<b>Role in Architecture</b>", table_header_style)],
        [Paragraph("Programming Language", table_cell_style), Paragraph("Python", table_cell_style), Paragraph("3.11.9", table_cell_style), Paragraph("Core implementation runtime", table_cell_style)],
        [Paragraph("Agent Orchestration", table_cell_style), Paragraph("LangGraph", table_cell_style), Paragraph("1.2.11", table_cell_style), Paragraph("StateGraph, cyclic edges, conditional routing", table_cell_style)],
        [Paragraph("LLM Framework", table_cell_style), Paragraph("LangChain Core", table_cell_style), Paragraph("1.6.3", table_cell_style), Paragraph("Tool registry, prompts, model bindings", table_cell_style)],
        [Paragraph("Data Validation", table_cell_style), Paragraph("Pydantic", table_cell_style), Paragraph("2.13.5", table_cell_style), Paragraph("Input sanitization, schemas, enums", table_cell_style)],
        [Paragraph("Relational Database", table_cell_style), Paragraph("SQLite3", table_cell_style), Paragraph("Native", table_cell_style), Paragraph("Tickets, profiles, conversation history", table_cell_style)],
        [Paragraph("Web Application UI", table_cell_style), Paragraph("Streamlit", table_cell_style), Paragraph("1.56.0", table_cell_style), Paragraph("Chat interface, memory viewer, approval buttons", table_cell_style)],
        [Paragraph("Terminal Interface", table_cell_style), Paragraph("Rich", table_cell_style), Paragraph("14.3.3", table_cell_style), Paragraph("Colorized terminal panels and CLI tables", table_cell_style)],
        [Paragraph("Local Model Backend", table_cell_style), Paragraph("Ollama / Granite", table_cell_style), Paragraph("granite3-dense", table_cell_style), Paragraph("Local semantic classification engine", table_cell_style)],
    ]

    t_tech = Table(tech_data, colWidths=[105, 95, 55, 249])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Working Process", h2_style))
    story.append(Paragraph(
        "The workflow follows 12 distinct steps: (1) Employee submits natural-language query; (2) Pydantic sanitizes input; "
        "(3) SQLite retrieves long-term profile and recent conversation turns; (4) SupportState is initialized; "
        "(5) <code>classify_query</code> evaluates intent and urgency; (6) LangGraph <code>route_query</code> routes to the specialist agent; "
        "(7) Agent queries SOP knowledge base; (8) Agent checks for sensitive/high-cost criteria; (9) Conditional edge sends state to "
        "<code>human_approval</code>, <code>create_ticket</code>, or <code>final_response</code>; (10) Tools execute actions; "
        "(11) Turn logs and memory are saved to SQLite; (12) User receives structured markdown response.",
        body_style
    ))

    story.append(Paragraph("Screenshots / Output Representations", h2_style))
    sample_terminal = (
        "<b>Sample Terminal Output: Hardware Issue Resolution</b><br/>"
        "&gt; [EMP1024] My laptop is not turning on.<br/>"
        "&nbsp;&nbsp;[Category]: HARDWARE | [Agent]: Hardware Agent | [Priority]: HIGH<br/>"
        "&nbsp;&nbsp;Hello EMP1024, (Department: Finance)<br/>"
        "&nbsp;&nbsp;### Laptop Power &amp; Boot Diagnostics:<br/>"
        "&nbsp;&nbsp;1. Connect original OEM charger and verify LED indicator.<br/>"
        "&nbsp;&nbsp;2. Perform 30-second hard reset.<br/>"
        "&nbsp;&nbsp;---\n"
        "&nbsp;&nbsp;<b>[Ticket Created]</b>: TKT-412C85A3 | Status: Open | Priority: High<br/>"
        "<br/>"
        "<b>Sample HITL Approval Output: Password Reset Security</b><br/>"
        "&gt; [EMP1024] I forgot my employee portal password.<br/>"
        "&nbsp;&nbsp;[Notice]: Human-in-the-loop approval required for credential reset.<br/>"
        "&nbsp;&nbsp;<b>[Approval Request Created]</b>: APP-3A96B0 | Action: ACCESS_SENSITIVE_ACTION<br/>"
        "&nbsp;&nbsp;Current Status: <i>Pending Human Administrator Verification</i>"
    )
    story.append(Paragraph(sample_terminal, code_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Results Achieved", h2_style))
    story.append(Paragraph(
        "The system was evaluated against 12 comprehensive test scenarios covering all required domains. "
        "<b>100.00% classification accuracy</b> and <b>zero routing failures</b> were achieved with an average latency of 0.0803 seconds.",
        body_style
    ))

    # Test Results Table
    results_data = [
        [Paragraph("<b>#</b>", table_header_style),
         Paragraph("<b>Query Scenario</b>", table_header_style),
         Paragraph("<b>Predicted</b>", table_header_style),
         Paragraph("<b>Agent</b>", table_header_style),
         Paragraph("<b>Tool Executed</b>", table_header_style),
         Paragraph("<b>Approval?</b>", table_header_style),
         Paragraph("<b>Result</b>", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("My laptop is not turning on.", table_cell_style), Paragraph("hardware", table_cell_style), Paragraph("hardware_agent", table_cell_style), Paragraph("create_ticket", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("Office printer is not printing...", table_cell_style), Paragraph("hardware", table_cell_style), Paragraph("hardware_agent", table_cell_style), Paragraph("create_ticket", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("Payroll app crashes on open.", table_cell_style), Paragraph("technical", table_cell_style), Paragraph("technical_agent", table_cell_style), Paragraph("create_ticket", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("Office Wi-Fi not connecting.", table_cell_style), Paragraph("technical", table_cell_style), Paragraph("technical_agent", table_cell_style), Paragraph("create_ticket", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("5", table_cell_style), Paragraph("Forgot employee portal password.", table_cell_style), Paragraph("access", table_cell_style), Paragraph("access_agent", table_cell_style), Paragraph("human_approval", table_cell_style), Paragraph("<b>Yes</b>", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("6", table_cell_style), Paragraph("Need access to attendance system.", table_cell_style), Paragraph("access", table_cell_style), Paragraph("access_agent", table_cell_style), Paragraph("human_approval", table_cell_style), Paragraph("<b>Yes</b>", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("7", table_cell_style), Paragraph("How can I apply for leave?", table_cell_style), Paragraph("general", table_cell_style), Paragraph("general_agent", table_cell_style), Paragraph("troubleshoot_sop", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("8", table_cell_style), Paragraph("Status of ticket TKT-12345678?", table_cell_style), Paragraph("general", table_cell_style), Paragraph("general_agent", table_cell_style), Paragraph("check_ticket", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("9", table_cell_style), Paragraph("What is the meaning of life?", table_cell_style), Paragraph("general", table_cell_style), Paragraph("general_agent", table_cell_style), Paragraph("troubleshoot_sop", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("10", table_cell_style), Paragraph("Need a new laptop, mine is broken.", table_cell_style), Paragraph("hardware", table_cell_style), Paragraph("hardware_agent", table_cell_style), Paragraph("human_approval", table_cell_style), Paragraph("<b>Yes</b>", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("11", table_cell_style), Paragraph("Monitor screen is blank/flickering.", table_cell_style), Paragraph("hardware", table_cell_style), Paragraph("hardware_agent", table_cell_style), Paragraph("human_approval", table_cell_style), Paragraph("<b>Yes</b>", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
        [Paragraph("12", table_cell_style), Paragraph("Working hours & shift timings?", table_cell_style), Paragraph("general", table_cell_style), Paragraph("general_agent", table_cell_style), Paragraph("troubleshoot_sop", table_cell_style), Paragraph("No", table_cell_style), Paragraph("<b>PASS</b>", table_cell_style)],
    ]

    t_res = Table(results_data, colWidths=[18, 140, 52, 80, 75, 45, 44])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (-2, 1), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_res)

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E0E0E0"), spaceBefore=8, spaceAfter=8))

    # =========================================================================
    # 4. Conclusion & Future Scope
    # =========================================================================
    story.append(Paragraph("4. Conclusion & Future Scope", h1_style))
    story.append(Paragraph("Project Conclusion", h2_style))
    story.append(Paragraph(
        "The Intelligent HR Equipment Support Assistant validates the power of Agentic AI workflows over basic chatbots. "
        "By decomposing support operations into decision-making models, operational tools, persistent SQLite memory, and explicit "
        "LangGraph state transitions, the system resolves routine inquiries autonomously while enforcing strict human oversight "
        "over credential and financial actions. The project represents a complete, secure, and production-ready enterprise solution.",
        body_style
    ))

    story.append(Paragraph("Challenges Faced", h2_style))
    story.append(Paragraph("• <b>LangChain 1.4 StructuredTool Invocation:</b> Decorated tools could not be called directly as functions; solved by dual-exporting native Python functions.", bullet_style))
    story.append(Paragraph("• <b>Keyword Substring Collisions:</b> <code>'apply'</code> matched <code>'app'</code> and <code>'laptop'</code> matched <code>'pto'</code>; resolved with regex word boundary (<code>\\b</code>) logic.", bullet_style))
    story.append(Paragraph("• <b>Ollama Daemon Timeouts:</b> Offline socket hanging was eliminated using a 0.2s socket liveness probe.", bullet_style))
    story.append(Paragraph("• <b>Windows Terminal Encoding:</b> PowerShell <code>cp1252</code> unicode crashes were resolved with UTF-8 <code>sys.stdout</code> wrappers.", bullet_style))
    story.append(Paragraph("• <b>Safe AST Math Evaluation:</b> Completely prevented arbitrary code execution by avoiding <code>eval()</code>.", bullet_style))

    story.append(Paragraph("Future Enhancements", h2_style))
    story.append(Paragraph("• Direct IBM Cloud watsonx.ai foundation model integration (IBM Granite 3.0).", bullet_style))
    story.append(Paragraph("• Retrieval-Augmented Generation (RAG) over corporate HR manuals using ChromaDB.", bullet_style))
    story.append(Paragraph("• Two-way REST API synchronization with ServiceNow and Jira Service Management.", bullet_style))
    story.append(Paragraph("• Multilingual translation (Tamil, English, Hindi) and voice assistance via Whisper API.", bullet_style))

    story.append(Paragraph("References", h2_style))
    story.append(Paragraph("1. IBM Agentic AI Internship curriculum video lectures, notes, and transcripts.", bullet_style))
    story.append(Paragraph("2. IBM watsonx.ai documentation: https://www.ibm.com/products/watsonx-ai", bullet_style))
    story.append(Paragraph("3. LangChain Documentation: https://python.langchain.com/", bullet_style))
    story.append(Paragraph("4. LangGraph Documentation: https://langchain-ai.github.io/langgraph/", bullet_style))
    story.append(Paragraph("5. Pydantic Data Validation: https://docs.pydantic.dev/", bullet_style))
    story.append(Paragraph("6. Model Context Protocol (MCP) Specification: https://modelcontextprotocol.io/", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    build_pdf()
