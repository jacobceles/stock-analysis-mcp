import io
import json
import logging
import re
import uuid

from typing import Any

import google.genai.types as types
import matplotlib.pyplot as plt

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from stock_analysis_mcp.agent.subagent import generate_plot_code_agent
from stock_analysis_mcp.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("tools")


async def generate_plot_data_agent(data: str, tool_context: ToolContext) -> dict:
    """Generates a single series plot data for the given data and stores it inside context. STRICTLY ensure that the data is plottable."""
    agent_tool = AgentTool(agent=generate_plot_code_agent)
    generate_plot_code_output = await agent_tool.run_async(args={"request": data}, tool_context=tool_context)
    tool_context.state["plot_code_output"] = generate_plot_code_output
    return generate_plot_code_output


async def generate_plot(tool_context: ToolContext) -> bool:
    """Plots equity data and saves it as an artifact."""
    plot_data_raw = tool_context.state.get("plot_code_output", "")
    plot_data = normalize_plot_payload(plot_data_raw)
    x_values = plot_data.get("x_values", [])
    y_values = plot_data.get("y_values", [])
    title = plot_data.get("title", "Plot")
    xlabel = plot_data.get("xlabel", "X-axis")
    ylabel = plot_data.get("ylabel", "Y-axis")
    x_values, y_values = sample_equally_spaced(x_values, y_values, max_points=10)
    plt.figure(figsize=(15, 6))
    plt.plot(x_values, y_values, marker="o", linestyle="-")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    plot_filename = f"generated_plot_{uuid.uuid4().hex}.png"
    report_artifact = types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")
    try:
        version = await tool_context.save_artifact(filename=plot_filename, artifact=report_artifact)
        logger.info("Successfully saved Python artifact '%s' as version %s.", plot_filename, version)
        return True
    except Exception as e:
        logger.exception("An unexpected error occurred during Python artifact save: %s", e)
    return False


def normalize_plot_payload(payload: Any) -> dict:
    if isinstance(payload, dict):
        return payload

    if isinstance(payload, str):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", payload.strip(), flags=re.IGNORECASE)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input: {e}") from e

    raise TypeError("Payload must be a dict or JSON string")


def sample_equally_spaced(x: list[Any], y: list[Any], max_points: int = 10) -> tuple:
    n = len(x)

    if n <= max_points:
        return x, y

    # Generate equally spaced indices including first and last
    indices = [round(i * (n - 1) / (max_points - 1)) for i in range(max_points)]

    # Ensure uniqueness & order (rounding can collide)
    indices = sorted(set(indices))

    return [x[i] for i in indices], [y[i] for i in indices]
