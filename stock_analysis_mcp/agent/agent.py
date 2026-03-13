import datetime
import logging
import os

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import SseConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.tool_context import ToolContext

from stock_analysis_mcp.agent.tools import generate_plot, generate_plot_data_agent
from stock_analysis_mcp.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# --- State Keys ---
STATE_TA = "technical_analysis"
STATE_EVAL = "evaluation"
COMPLETION_PHRASE = "STOP EXECUTION"


def exit_loop(tool_context: ToolContext) -> dict[str, Any]:
    """Call this function ONLY when the critique indicates no further changes are needed, signaling
    the iterative process should end."""
    logger.info("  [Tool Call] exit_loop triggered by %s", tool_context.agent_name)
    tool_context.actions.escalate = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}


mcp_toolset = MCPToolset(connection_params=SseConnectionParams(url=os.environ.get("MCP_URL", "")))

today_date = datetime.datetime.now().strftime("%A, %d %B %Y")

ta_agent = LlmAgent(
    name="stock_ta_assistant",
    model=LiteLlm(
        model=os.environ.get("LITE_LLM_MODEL", ""),
        api_key=os.environ.get("LITE_LLM_API_KEY", ""),
    ),
    instruction=f"""
    You are an agent that helps to perform technical analysis for Indian stocks. The user will provide you the stock symbol from NSE.
    You have to use the given tools to perform technical analysis and provide sound information to the user. 
    You can also fetch recent stock-related news and discussions from Reddit.
    You can also plot ONLY A SINGLE series line graphs.
    While performing analysis try to plot relevant graphs for each of the indicators to support your analysis.
    You have to decide whether to BUY or SELL stock and at what price should the action to be taken.
    This action will then executed inside a simulated enviroment to evaluate your capabilities.

    While generating plots, STRICTLY ensure you follow these workflow:
    1. Call the `generate_plot_data_agent` tool with valid data.
    2. Call the `generate_plot` tool with the output from previous step to generate and save the plot as an artifact.

    Today's date is {today_date}.
    """,
    tools=[mcp_toolset, generate_plot_data_agent, generate_plot],
    output_key=STATE_TA,
)

root_agent = ta_agent
