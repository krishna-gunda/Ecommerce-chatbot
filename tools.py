"""
tools.py
--------
These are the "action" tools the agent can call - things that need to look
something up in our (dummy) database, not just search documents.

Each function has:
  - the @tool decorator, which tells LangChain "this is a tool the LLM can call"
  - a docstring, which the LLM actually READS to decide when to use this tool
    (so keep docstrings clear and specific!)
  - type hints (order_id: str), so LangChain knows what input to expect
"""

import sqlite3
from langchain_core.tools import tool


def get_db_connection():
    """Small helper to open a connection to our dummy orders.db file."""
    return sqlite3.connect("data/orders.db")


@tool
def get_order_status(order_id: str) -> str:
    """
    Look up the current status of an order using its order ID.
    Use this when the customer asks where their order is, when it will
    arrive, or what stage it's at (e.g. "Where is my order ORD1005?").
    The order_id should look like ORD1001, ORD1002, etc.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT status, current_location, expected_delivery FROM orders WHERE order_id = ?",
        (order_id,)
    )
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return f"I couldn't find any order with ID {order_id}. Please double-check the order ID."

    status, location, expected_delivery = row
    return (
        f"Order {order_id} is currently '{status}'. "
        f"It is at {location}, and the expected delivery date is {expected_delivery}."
    )


@tool
def get_order_details(order_id: str) -> str:
    """
    Get full details about an order: product name, amount paid, payment
    method, and order date. Use this when the customer asks about what
    they ordered, how much they paid, or which payment method was used.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """SELECT product_name, order_date, amount, payment_method
           FROM orders WHERE order_id = ?""",
        (order_id,)
    )
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return f"I couldn't find any order with ID {order_id}."

    product_name, order_date, amount, payment_method = row
    return (
        f"Order {order_id}: {product_name}, ordered on {order_date} "
        f"for Rs. {amount:.2f}, paid via {payment_method}."
    )


@tool
def initiate_return(order_id: str, reason: str) -> str:
    """
    Start a return request for an order. Use this when the customer
    explicitly wants to return an item and has given a reason
    (e.g. "I want to return ORD1003, it doesn't fit").
    This only works if the order status is 'Delivered'.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return f"I couldn't find any order with ID {order_id}."

    status = row[0]
    if status != "Delivered":
        return (
            f"Order {order_id} cannot be returned right now because its "
            f"current status is '{status}'. Returns are only possible after delivery."
        )

    # In a real system, this would insert a row into a "returns" table
    # and trigger a pickup workflow. For this project, we just confirm it.
    return (
        f"Return initiated for order {order_id}. Reason noted: '{reason}'. "
        f"A pickup will be scheduled within 2-4 business days, and a refund "
        f"will be processed after quality inspection."
    )


# This list is what we import into agent.py
custom_tools = [get_order_status, get_order_details, initiate_return]
