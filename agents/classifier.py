"""
agents/classifier.py
Query classification node and conditional router for the LangGraph state graph.
Classifies employee queries into hardware, technical, access, or general categories,
assigns initial priority, and provides routing decisions.
"""

import os
import json
import re
from typing import Dict, Any
from models.schemas import SupportState, IssueCategory, TicketPriority

# Configurable LLM Backend toggle (can be overridden via environment variable)
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite3-dense:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def _keyword_classify(query: str) -> Dict[str, Any]:
    """
    High-precision pattern & keyword classification with reasoning.
    Serves as an autonomous classifier or immediate zero-latency fallback
    when local LLM server is starting or unreachable.
    """
    q = query.lower()

    # Priority / Urgency detection
    priority = TicketPriority.MEDIUM.value
    if any(term in q for term in ["urgent", "emergency", "immediately", "critical", "blocked", "asap"]):
        priority = TicketPriority.HIGH.value
    elif any(term in q for term in ["crash", "dead", "won't boot", "cannot work", "failing"]):
        priority = TicketPriority.HIGH.value
    elif any(term in q for term in ["when you have time", "low priority", "fyi", "curious", "general question"]):
        priority = TicketPriority.LOW.value

    # Specific keyword banks
    hardware_patterns = [
        "laptop", "desktop", "computer", "keyboard", "mouse", "printer", "printing",
        "monitor", "screen", "display", "charger", "battery", "adapter", "power cord",
        "headset", "earphones", "hdmi", "cable", "hardware", "not turning on", "won't turn on",
        "overheating", "fan noise", "physical damage", "broken"
    ]

    technical_patterns = [
        "crash", "crashes", "crashing", "software", "application", "desktop app", "mobile app", "payroll application",
        "install", "installation", "update", "operating system", "windows", "linux", "os error",
        "blue screen", "bsod", "network", "wi-fi", "wifi", "internet", "vpn", "dns", "firewall",
        "connection", "freeze", "slow performance", "error code", "bug", "fails to open"
    ]

    access_patterns = [
        "password", "forgot password", "reset password", "change password", "login", "log in",
        "sign in", "account", "locked", "unlock", "access", "permission", "portal",
        "portal password", "attendance system", "mfa", "2fa", "two-factor", "credentials",
        "privilege", "role access", "authentication"
    ]

    general_patterns = [
        "leave", "sick leave", "casual leave", "pto", "vacation", "apply for leave",
        "attendance", "working hours", "timing", "shift", "holiday", "calendar",
        "hr policy", "policy", "handbook", "benefits", "insurance", "salary slip",
        "payroll cycle", "reimbursement", "contact hr", "meaning of life", "who are you",
        "help", "hello", "hi"
    ]

    # Word-aware pattern scoring
    def _score_patterns(patterns, text):
        score = 0
        for p in patterns:
            # Match whole words or phrase
            pattern_regex = r"\b" + re.escape(p) + r"\b"
            if re.search(pattern_regex, text):
                score += 2
        return score

    scores = {
        IssueCategory.HARDWARE.value: _score_patterns(hardware_patterns, q),
        IssueCategory.TECHNICAL.value: _score_patterns(technical_patterns, q),
        IssueCategory.ACCESS.value: _score_patterns(access_patterns, q),
        IssueCategory.GENERAL.value: _score_patterns(general_patterns, q),
    }

    # Disambiguation rules for compound queries:
    # E.g. "payroll application crashes" -> technical (even if payroll is mentioned)
    if re.search(r"\b(crash|crashes|crashing|software)\b", q) and not re.search(r"\b(leave|vacation)\b", q):
        scores[IssueCategory.TECHNICAL.value] += 4

    # "apply for leave" -> general HR (use word boundary so 'pto' does not match inside 'laptop'!)
    if re.search(r"\b(leave|vacation|pto|sick leave)\b", q):
        scores[IssueCategory.GENERAL.value] += 6
        scores[IssueCategory.TECHNICAL.value] = 0
        scores[IssueCategory.HARDWARE.value] = 0

    # "office wi-fi" -> technical
    if re.search(r"\b(wi-fi|wifi|network|dns|vpn)\b", q):
        scores[IssueCategory.TECHNICAL.value] += 4

    # Hardware keywords (laptop, monitor, printer, etc.)
    if re.search(r"\b(laptop|desktop|monitor|printer|keyboard|mouse|charger|battery|adapter|hardware)\b", q):
        scores[IssueCategory.HARDWARE.value] += 5

    # Access keywords (password, portal access, login)
    if re.search(r"\b(password|login|locked|unlock|credentials)\b", q) or (re.search(r"\baccess\b", q) and not re.search(r"\bleave\b", q)):
        scores[IssueCategory.ACCESS.value] += 5

    # Determine highest scoring category
    best_category = max(scores, key=scores.get)
    max_score = scores[best_category]

    if max_score == 0:
        # Default fallback to general
        best_category = IssueCategory.GENERAL.value
        confidence = 0.50
        reason = "No domain-specific equipment or technical keywords detected; categorized as General HR."
    else:
        confidence = min(0.95, 0.70 + (max_score * 0.05))
        reason = f"Detected key terms matching {best_category.upper()} domain indicators."

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "reason": reason,
        "priority": priority
    }


import socket
from urllib.parse import urlparse

_ollama_available = None


def is_ollama_online(base_url: str = OLLAMA_BASE_URL) -> bool:
    """Fast probe to determine if local Ollama daemon is actively listening."""
    global _ollama_available
    if _ollama_available is not None:
        return _ollama_available
    try:
        parsed = urlparse(base_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 11434
        with socket.create_connection((host, port), timeout=0.2):
            _ollama_available = True
            return True
    except Exception:
        _ollama_available = False
        return False


def _llm_classify(query: str) -> Dict[str, Any]:
    """Attempts to use LangChain + Ollama/Granite for semantic classification."""
    if not is_ollama_online():
        # Immediate fallback to zero-latency pattern classifier if daemon is offline
        return _keyword_classify(query)

    try:
        from langchain_ollama import ChatOllama
        from langchain_core.prompts import PromptTemplate

        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.0,
            timeout=5.0
        )

        template = """You are an HR and IT Equipment Support classifier.
Analyze the following employee query and classify it into EXACTLY ONE category:
- hardware (laptops, monitors, printers, keyboards, mice, chargers, batteries)
- technical (application crashes, software errors, OS issues, Wi-Fi, network)
- access (passwords, logins, account lockouts, portal access permissions)
- general (leave, attendance, working hours, HR policies, benefits)

Respond ONLY with a JSON object in this format:
{{"category": "<hardware|technical|access|general>", "confidence": <float 0-1>, "reason": "<brief reason>", "priority": "<low|medium|high|critical>"}}

Query: {query}
JSON:"""

        prompt = PromptTemplate(template=template, input_variables=["query"])
        chain = prompt | llm
        response = chain.invoke({"query": query})
        content = response.content.strip()

        # Extract JSON substring
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            category = data.get("category", "").lower().strip()
            if category in [c.value for c in IssueCategory]:
                return {
                    "category": category,
                    "confidence": float(data.get("confidence", 0.9)),
                    "reason": str(data.get("reason", "LLM semantic classification")),
                    "priority": str(data.get("priority", "medium")).lower()
                }
    except Exception:
        # Silently fall back to keyword classifier if Ollama is not active
        pass

    return _keyword_classify(query)


def classify_query(state: SupportState) -> SupportState:
    """
    LangGraph Node: classify_query
    Inspects user_query, assigns category and priority, and updates state.
    """
    query = state.get("user_query", "")

    # Perform classification
    if LLM_BACKEND == "ollama":
        result = _llm_classify(query)
    else:
        result = _keyword_classify(query)

    state["category"] = result["category"]
    state["priority"] = result["priority"]

    # Record classification step in conversation history
    history = state.get("conversation_history", [])
    history.append(f"System: Classified query into '{result['category']}' category (Priority: {result['priority']}).")
    state["conversation_history"] = history

    return state


def route_query(state: SupportState) -> str:
    """
    LangGraph Conditional Router Function:
    Inspects state['category'] and returns the next agent node name.

    Returns one of:
    - 'hardware_agent'
    - 'technical_agent'
    - 'access_agent'
    - 'general_agent'
    """
    category = state.get("category", "general").lower().strip()

    if category == IssueCategory.HARDWARE.value:
        return "hardware_agent"
    elif category == IssueCategory.TECHNICAL.value:
        return "technical_agent"
    elif category == IssueCategory.ACCESS.value:
        return "access_agent"
    else:
        return "general_agent"
