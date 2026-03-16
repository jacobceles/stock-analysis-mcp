import importlib
import os

from unittest.mock import patch

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

import stock_analysis_mcp.agent.plot_agent

from stock_analysis_mcp.agent.plot_agent import PlotDataOutput, generate_plot_code_agent


def test_generate_plot_code_agent_attributes() -> None:
    """Test that the plot agent is initialized with expected configurations."""
    assert isinstance(generate_plot_code_agent, LlmAgent)
    assert generate_plot_code_agent.name == "generate_plot_agent"
    assert generate_plot_code_agent.output_schema == PlotDataOutput
    instruction = generate_plot_code_agent.instruction
    assert isinstance(instruction, str)
    assert "You are a candlestick plotting data agent" in instruction


@patch.dict(os.environ, {"LITE_LLM_MODEL": "test-model", "LITE_LLM_API_KEY": "test-key"})
def test_generate_plot_code_agent_model_initialization() -> None:
    """Test the agent initialization with environment variables."""
    # Since generate_plot_code_agent is initialized at module load time,
    # we need to reload the module inside the test with patched environment variables.
    try:
        importlib.reload(stock_analysis_mcp.agent.plot_agent)

        reloaded_agent = stock_analysis_mcp.agent.plot_agent.generate_plot_code_agent

        assert isinstance(reloaded_agent.model, LiteLlm)
        assert reloaded_agent.model.model == "test-model"
        # api_key is not stored as an attribute on LiteLlm, so we just verify the model name was set correctly.
    finally:
        # Restore the original module state
        importlib.reload(stock_analysis_mcp.agent.plot_agent)
