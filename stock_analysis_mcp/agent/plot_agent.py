import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field


class PlotDataOutput(BaseModel):
    x_values: list[str] = Field(..., description="Ordered x-axis values (dates/timestamps)")
    open: list[float] = Field(..., description="Opening prices")
    high: list[float] = Field(..., description="High prices")
    low: list[float] = Field(..., description="Low prices")
    close: list[float] = Field(..., description="Closing prices")
    title: str = Field(default="Candlestick Chart")
    xlabel: str = Field(default="Date")
    ylabel: str = Field(default="Price")


generate_plot_code_agent = LlmAgent(
    model=LiteLlm(
        model=os.environ.get("LITE_LLM_MODEL", ""),
        api_key=os.environ.get("LITE_LLM_API_KEY", ""),
    ),
    name="generate_plot_agent",
    output_schema=PlotDataOutput,
    instruction="""
You are a candlestick plotting data agent.

Your responsibility is to convert the given input data into a JSON object
that represents OHLC (Open, High, Low, Close) data suitable for a candlestick chart.

Output rules (STRICT):
- Output MUST be valid JSON only.
- Do NOT include explanations, markdown, or extra text.
- Do NOT call or reference any tools.
- Do NOT fabricate or guess data.

JSON schema (exact keys, no extras):
{
  "x_values": [...],
  "open": [...],
  "high": [...],
  "low": [...],
  "close": [...],
  "title": "...",
  "xlabel": "...",
  "ylabel": "..."
}

Data rules:
- x_values MUST be dates or timestamps.
- open, high, low, close MUST be numerical and aligned with x_values.
- All lists (x_values, open, high, low, close) MUST have the same length.
- Do NOT modify, truncate, round, or transform values.

Failure cases:
- If candlestick plotting is not possible due to insufficient data (missing OHLC components),
  return the following JSON exactly:
  {
    "error": "Candlestick plotting not possible with the given data"
  }
""",
)
