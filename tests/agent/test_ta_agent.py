from unittest.mock import MagicMock

import pytest

from google.adk.tools.tool_context import ToolContext

from stock_analysis_mcp.agent.ta_agent import exit_loop


def test_exit_loop_with_actions():
    """Test exit_loop sets actions.escalate to True when actions is present."""
    mock_context = MagicMock(spec=ToolContext)

    result = exit_loop(mock_context)

    assert result == {}
    assert mock_context.actions.escalate is True


def test_exit_loop_missing_actions():
    """Test exit_loop raises AttributeError when actions is missing."""
    mock_context = MagicMock(spec=ToolContext)
    del mock_context.actions

    with pytest.raises(AttributeError):
        exit_loop(mock_context)
