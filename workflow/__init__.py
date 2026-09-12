"""
Workflow package for Intelligent HR Equipment Support Assistant.
Exposes the compiled LangGraph state graph.
"""

from workflow.graph import build_graph, run_support_agent

__all__ = ["build_graph", "run_support_agent"]
