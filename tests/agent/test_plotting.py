import pytest

from stock_analysis_mcp.agent.tools.plotting import get_sample_indices, normalize_plot_payload


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
