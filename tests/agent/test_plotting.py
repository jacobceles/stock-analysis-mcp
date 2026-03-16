from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from google.adk.tools import ToolContext

from stock_analysis_mcp.agent.tools.plotting import (
    generate_plot_data_agent,
    get_sample_indices,
    normalize_plot_payload,
)


def test_normalize_plot_payload_dict() -> None:
    payload = {"x_values": [1, 2], "y_values": [3, 4]}
    assert normalize_plot_payload(payload) == payload


def test_normalize_plot_payload_json_string() -> None:
    payload = '{"x_values": [1, 2], "y_values": [3, 4]}'
    expected = {"x_values": [1, 2], "y_values": [3, 4]}
    assert normalize_plot_payload(payload) == expected


def test_normalize_plot_payload_markdown_json() -> None:
    payload = '```json\n{"x_values": [1, 2], "y_values": [3, 4]}\n```'
    expected = {"x_values": [1, 2], "y_values": [3, 4]}
    assert normalize_plot_payload(payload) == expected


def test_normalize_plot_payload_invalid_json() -> None:
    with pytest.raises(ValueError, match="Invalid JSON input"):
        normalize_plot_payload("{invalid}")


def test_normalize_plot_payload_invalid_json_string() -> None:
    with pytest.raises(ValueError, match="Invalid JSON input"):
        normalize_plot_payload("invalid json")


def test_normalize_plot_payload_invalid_type() -> None:
    with pytest.raises(TypeError, match="Payload must be a dict or JSON string"):
        normalize_plot_payload(123)


def test_get_sample_indices_small() -> None:
    n = 10
    max_points = 100
    indices = get_sample_indices(n, max_points)
    assert indices == list(range(10))


def test_get_sample_indices_large() -> None:
    n = 1000
    max_points = 100
    indices = get_sample_indices(n, max_points)
    assert len(indices) == max_points
    assert indices[0] == 0
    assert indices[-1] == n - 1
    assert sorted(indices) == indices
    assert len(set(indices)) == max_points


@pytest.mark.asyncio
async def test_generate_plot_data_agent_success() -> None:
    data = "AAPL stock prices"
    expected_output = {"x_values": ["2023-01-01"], "close": [150.0]}

    mock_tool_context = MagicMock(spec=ToolContext)
    mock_tool_context.state = {}

    with patch("stock_analysis_mcp.agent.tools.plotting.AgentTool") as mock_agent_tool_class:
        mock_instance = mock_agent_tool_class.return_value
        mock_instance.run_async = AsyncMock(return_value=expected_output)

        result = await generate_plot_data_agent(data, mock_tool_context)

        assert result == expected_output
        assert mock_tool_context.state["plot_code_output"] == expected_output
        mock_agent_tool_class.assert_called_once()
        mock_instance.run_async.assert_awaited_once_with(args={"request": data}, tool_context=mock_tool_context)


@pytest.mark.asyncio
async def test_generate_plot_data_agent_handles_error() -> None:
    data = "invalid data"

    mock_tool_context = MagicMock(spec=ToolContext)
    mock_tool_context.state = {}

    with patch("stock_analysis_mcp.agent.tools.plotting.AgentTool") as mock_agent_tool_class:
        mock_instance = mock_agent_tool_class.return_value
        mock_instance.run_async = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception, match="API Error"):
            await generate_plot_data_agent(data, mock_tool_context)

        assert "plot_code_output" not in mock_tool_context.state
        mock_agent_tool_class.assert_called_once()
        mock_instance.run_async.assert_awaited_once_with(args={"request": data}, tool_context=mock_tool_context)
