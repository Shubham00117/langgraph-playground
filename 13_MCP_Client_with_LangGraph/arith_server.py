from __future__ import annotations
from fastmcp import FastMCP

# Define an MCP Server instance
mcp = FastMCP("arith")

# Tool registration is separated out from client code
@mcp.tool()
async def add(a: float, b: float) -> float:
    """Return a + b."""
    return a + b

@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Return a - b."""
    return a - b

@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Return a / b. Raises on zero."""
    if b == 0:
        raise ZeroDivisionError("Division by zero")
    return a / b

# Run logic handles starting the server (can be tested locally)
if __name__ == "__main__":
    mcp.run()
