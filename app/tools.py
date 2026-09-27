"""The three simple tools the LangChain agent can call.

Each tool is a plain function wrapped with LangChain's @tool decorator: the
docstring tells the LLM when to pick it, and the return value is fed back to
the model as the tool result.
"""

import ast
import operator

from langchain_core.tools import tool

from app.rag import retrieve_policy


@tool
def policy_search(query: str) -> str:
    """Search internal customer-support policy documents (refund, cancellation,
    shipping, account). Use this for ANY question about store policies."""
    return retrieve_policy(query)


# In-memory demo data — swap for a real database later without touching the agent.
ORDERS = {
    "ORD1001": "Shipped",
    "ORD1002": "Processing",
    "ORD1003": "Delivered",
    "ORD1004": "Cancelled",
}


@tool
def order_status(order_id: str) -> str:
    """Look up the current status of a customer order by its ID, e.g. ORD1001."""
    order_id = order_id.strip().upper()
    status = ORDERS.get(order_id)
    if status is None:
        return "Order not found."
    return f"Order {order_id} status: {status}"


# Calculator: only numbers and + - * / ( ) are ever evaluated. We parse the
# expression into a syntax tree and walk it ourselves, so no raw eval() happens.
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_ALLOWED_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval_node(node: ast.AST) -> float:
    """Recursively evaluate an expression tree, allowing only safe operations."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](
            _safe_eval_node(node.left), _safe_eval_node(node.right)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_safe_eval_node(node.operand))
    raise ValueError("only numbers and + - * / ( ) are supported")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression with +, -, * and /. Example input: '125 * 8'."""
    try:
        tree = ast.parse(expression, mode="eval")  # parse first, never eval raw text
        return f"{expression} = {_safe_eval_node(tree.body)}"
    except (SyntaxError, ValueError, ZeroDivisionError) as exc:
        return f"Could not calculate '{expression}': {exc}"
