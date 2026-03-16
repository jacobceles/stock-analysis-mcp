import io
import json
import logging
import os
import re
import uuid

from typing import Any

import finplot as fplt  # type:ignore
import google.genai.types as types
import pandas as pd

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from stock_analysis_mcp.agent.plot_agent import generate_plot_code_agent
from stock_analysis_mcp.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Set offscreen platform for headless operation
os.environ["QT_QPA_PLATFORM"] = "offscreen"


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
    open_values = plot_data.get("open", [])
    high_values = plot_data.get("high", [])
    low_values = plot_data.get("low", [])
    close_values = plot_data.get("close", [])

    title = plot_data.get("title", "Candlestick Chart")
    ylabel = plot_data.get("ylabel", "Price")

    # Sample data for better visualization if there are too many points
    indices = get_sample_indices(len(x_values), max_points=100)
    x_values = [x_values[i] for i in indices]
    open_values = [open_values[i] for i in indices]
    high_values = [high_values[i] for i in indices]
    low_values = [low_values[i] for i in indices]
    close_values = [close_values[i] for i in indices]

    if not x_values or not close_values:
        logger.error("No data to plot")
        return False

    try:
        # Prepare DataFrame for finplot
        df = pd.DataFrame(
            {
                "Date": x_values,
                "Open": open_values,
                "High": high_values,
                "Low": low_values,
                "Close": close_values,
            }
        )

        # Try to convert Date to datetime
        try:
            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)
        except (ValueError, TypeError):
            # Fallback to simple range if x is not datetime
            df.index = pd.Index(range(len(df)))

        # Initialize app (needed for finplot/pyqtgraph)
        app = QApplication.instance() or QApplication([])

        # Clear any previous plots
        fplt.close()

        # Create plot and get axis object
        ax = fplt.create_plot(title)
        if isinstance(ax, list):
            ax = ax[0]

        # Plot candlestick
        # finplot candlestick expects a DataFrame with columns: [Open, Close, High, Low] in that order or OHLC
        fplt.candlestick_ochl(df[["Open", "Close", "High", "Low"]])
        # Set y-axis label on the left (finplot often defaults to right for price)
        ax.setLabel("left", ylabel)

        buf = io.BytesIO()

        def take_screenshot() -> None:
            nonlocal buf
            try:
                fplt.screenshot(buf)
                buf.seek(0)
            except Exception as e:
                logger.error("Error taking screenshot: %s", e)
            finally:
                app.quit()

        # Schedule screenshot after a short delay to allow rendering
        QTimer.singleShot(100, take_screenshot)

        # Run app event loop (blocks until app.quit() is called)
        fplt.show(qt_exec=True)

        if buf.getbuffer().nbytes == 0:
            logger.error("Generated plot buffer is empty")
            return False

        plot_filename = f"generated_plot_{uuid.uuid4().hex}.png"
        report_artifact = types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png")

        version = await tool_context.save_artifact(filename=plot_filename, artifact=report_artifact)
        logger.info("Successfully saved Python artifact '%s' as version %s.", plot_filename, version)
        return True

    except Exception as e:
        logger.exception("An unexpected error occurred during plotting or artifact save: %s", e)
        return False
    finally:
        fplt.close()


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


def get_sample_indices(n: int, max_points: int = 100) -> list[int]:
    if n <= max_points:
        return list(range(n))

    # Generate equally spaced indices including first and last
    indices = [round(i * (n - 1) / (max_points - 1)) for i in range(max_points)]

    # Ensure uniqueness & order (rounding can collide)
    return sorted(set(indices))
