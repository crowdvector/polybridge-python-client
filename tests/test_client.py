"""Unit tests for PolybridgeClient."""

import pytest
from unittest.mock import Mock, patch

from polybridge import PolybridgeClient
from polybridge.types import TimeseriesResult


class TestPolybridgeClient:
    """Test cases for PolybridgeClient."""

    def test_init_requires_api_key(self):
        """Test that API key is required."""
        with pytest.raises(ValueError, match="API key is required"):
            PolybridgeClient(api_key="")

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = PolybridgeClient(api_key="test-key")
        assert client.base_url == "https://us-central1-polymarket-analytics-api.cloudfunctions.net"
        assert client.timeout == 60
        assert client.session.headers["X-API-Key"] == "test-key"

    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL."""
        client = PolybridgeClient(api_key="test-key", base_url="https://custom.example.com")
        assert client.base_url == "https://custom.example.com"

    def test_init_with_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = PolybridgeClient(api_key="test-key", timeout=120)
        assert client.timeout == 120

    def test_init_with_custom_session(self):
        """Test client initialization with custom session."""
        custom_session = Mock()
        client = PolybridgeClient(api_key="test-key", session=custom_session)
        assert client.session is custom_session

    def test_to_iso(self):
        """Test datetime to ISO conversion."""
        from datetime import datetime, timezone

        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        iso = PolybridgeClient._to_iso(dt)
        assert iso == "2024-01-01T12:00:00Z"

    def test_ensure_datetime_with_value(self):
        """Test datetime parsing from ISO string."""
        from datetime import datetime, timezone

        dt = PolybridgeClient._ensure_datetime(
            "2024-01-01T12:00:00Z", fallback=datetime.now(timezone.utc)
        )
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_ensure_datetime_with_none(self):
        """Test datetime fallback when value is None."""
        from datetime import datetime, timezone

        fallback = datetime(2024, 1, 1, tzinfo=timezone.utc)
        dt = PolybridgeClient._ensure_datetime(None, fallback=fallback)
        assert dt == fallback

    def test_chunk(self):
        """Test sequence chunking."""
        sequence = ["a", "b", "c", "d", "e"]
        chunks = list(PolybridgeClient._chunk(sequence, 2))
        assert chunks == [["a", "b"], ["c", "d"], ["e"]]

    @patch("polybridge.client.requests.Session")
    def test_post_success(self, mock_session_class):
        """Test successful POST request."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200

        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = PolybridgeClient(api_key="test-key")
        result = client._post("test_endpoint", {"key": "value"})

        assert result == {"data": "test"}
        mock_session.post.assert_called_once()

    @patch("polybridge.client.requests.Session")
    def test_post_http_error(self, mock_session_class):
        """Test POST request with HTTP error."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.text = "Error message"
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")

        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session

        client = PolybridgeClient(api_key="test-key")
        with pytest.raises(Exception):
            client._post("test_endpoint", {})

    def test_merge_responses_empty_destination(self):
        """Test merging responses with empty destination."""
        source = {
            "probabilities": {"columns": ["col1"], "rows": [{"col1": "value1"}]},
            "meta": {"key": "value"},
        }
        result = PolybridgeClient._merge_responses({}, source)
        assert result == source

    def test_merge_responses_non_empty_destination(self):
        """Test merging responses with non-empty destination."""
        destination = {
            "probabilities": {"columns": ["col1"], "rows": [{"col1": "value1"}]},
        }
        source = {
            "probabilities": {"columns": ["col1"], "rows": [{"col1": "value2"}]},
        }
        result = PolybridgeClient._merge_responses(destination, source)
        assert len(result["probabilities"]["rows"]) == 2

    def test_response_to_frames(self):
        """Test conversion of response to DataFrames."""
        import pandas as pd

        response = {
            "probabilities": {"rows": [{"col1": "value1"}, {"col1": "value2"}]},
            "prices": {"rows": [{"price": 100}]},
        }
        frames = PolybridgeClient._response_to_frames(response)
        assert "probabilities" in frames
        assert "prices" in frames
        assert isinstance(frames["probabilities"], pd.DataFrame)
        assert len(frames["probabilities"]) == 2

    def test_fetch_timeseries_no_horizons(self):
        """Test fetch_timeseries with no horizons raises error."""
        client = PolybridgeClient(api_key="test-key")
        with pytest.raises(ValueError, match="At least one horizon must be provided"):
            client.fetch_timeseries(asset="BTC", horizons=[])

