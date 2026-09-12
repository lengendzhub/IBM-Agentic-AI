"""
tools/utility_tools.py
General utility tools including:
- get_current_datetime: for timestamps and SLA calculations
- safe_calculator: AST-based mathematical evaluator (no unrestricted eval)
- word_count: text analysis tool for diagnostic logs and queries
"""

import ast
import operator as op
from datetime import datetime
from typing import Dict, Any, Union

try:
    from langchain_core.tools import tool
except ImportError:
    def tool(func):
        return func


def get_current_datetime() -> str:
    """
    Returns the current date and time formatted as YYYY-MM-DD HH:MM:SS.
    Useful for checking operating hours, SLA deadlines, or timestamping requests.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Allowed AST operators mapped to standard python operator functions
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _eval_ast_node(node: ast.AST) -> Union[int, float]:
    """
    Recursively evaluates an AST node safely.
    Strictly forbids function calls, attribute access, variable names, and imports.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    # For Python < 3.8 compatibility
    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.BinOp):
        left = _eval_ast_node(node.left)
        right = _eval_ast_node(node.right)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            if op_type is ast.Div and right == 0:
                raise ZeroDivisionError("Division by zero is not permitted.")
            return ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

    if isinstance(node, ast.UnaryOp):
        operand = _eval_ast_node(node.operand)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

    raise ValueError(f"Unsafe or disallowed expression element: {type(node).__name__}")


def safe_calculator(expression: str) -> Dict[str, Any]:
    """
    Safely evaluates a mathematical expression using an AST parser.
    Strictly prevents code injection, OS commands, or unrestricted eval().

    Args:
        expression: A mathematical expression string, e.g. "65000 * 1.18" or "(120 + 80) / 2".

    Returns:
        A dictionary with the evaluated result, or an error message if invalid.
    """
    cleaned = expression.strip()
    try:
        parsed = ast.parse(cleaned, mode="eval")
        result = _eval_ast_node(parsed.body)
        return {
            "expression": cleaned,
            "result": result,
            "success": True
        }
    except ZeroDivisionError as zde:
        return {
            "expression": cleaned,
            "error": str(zde),
            "success": False
        }
    except Exception as exc:
        return {
            "expression": cleaned,
            "error": f"Invalid expression: {str(exc)}",
            "success": False
        }


def word_count(text: str) -> Dict[str, int]:
    """
    Analyzes a text string and returns count of words, characters, and sentences.
    Useful for diagnostic log inspection or ticket description length validation.

    Args:
        text: The text to analyze.

    Returns:
        Dictionary with words, characters, characters_without_spaces, and sentences count.
    """
    if not text:
        return {
            "words": 0,
            "characters": 0,
            "characters_without_spaces": 0,
            "sentences": 0
        }

    words = text.split()
    characters = len(text)
    characters_without_spaces = len(text.replace(" ", "").replace("\t", "").replace("\n", ""))
    # Count basic sentence terminators
    sentences = sum(text.count(mark) for mark in [".", "!", "?"])
    if sentences == 0 and len(words) > 0:
        sentences = 1

    return {
        "words": len(words),
        "characters": characters,
        "characters_without_spaces": characters_without_spaces,
        "sentences": sentences
    }


# Export LangChain Tool instances
get_current_datetime_tool = tool(get_current_datetime)
safe_calculator_tool = tool(safe_calculator)
word_count_tool = tool(word_count)
