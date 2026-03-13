import os

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field


class PlotDataOutput(BaseModel):
    x_values: list[str] = Field(..., description="Ordered x-axis values")
    y_values: list[float] = Field(..., description="Ordered y-axis values")
    title: str = Field(default="Plot")
    xlabel: str = Field(default="X-axis")
    ylabel: str = Field(default="Y-axis")


generate_plot_code_agent = LlmAgent(
    model=LiteLlm(
        model=os.environ.get("LITE_LLM_MODEL", ""),
        api_key=os.environ.get("LITE_LLM_API_KEY", ""),
    ),
    name="generate_plot_agent",
    output_schema=PlotDataOutput,
    instruction="""
You are a single-series plotting data agent.

Your responsibility is to convert the given input data into a JSON object
that represents exactly ONE line series suitable for plotting.

Output rules (STRICT):
- Output MUST be valid JSON only.
- Do NOT include explanations, markdown, or extra text.
- Do NOT call or reference any tools.
- Do NOT fabricate or guess data.

JSON schema (exact keys, no extras):
{
  "x_values": [...],
  "y_values": [...],
  "title": "...",
  "xlabel": "...",
  "ylabel": "..."
}

Data rules:
- A series consists of exactly one x_values list and one y_values list.
- x_values may be dates, timestamps, or categories.
- y_values must be numerical and aligned with x_values.
- Number of points in x_values and y_values MUST be the same.
- Do NOT modify, truncate, round, or transform values.

Failure cases:
- If plotting is not possible due to insufficient data or multi-series input,
  return the following JSON exactly:
  {
    "error": "Plotting not possible with the given data"
  }
""",
)
