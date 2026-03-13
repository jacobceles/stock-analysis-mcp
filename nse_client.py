from datetime import datetime
from typing import Any

import requests

from constants import HISTORICAL_ENDPOINT, METADATA_ENDPOINT, NSE_HOST_URL


class NSEClient:
    """Minimal NSE client that ensures default headers are merged into requests.

    Usage:
        client = NSEClient()
        client.get_metadata('TCS')
        client.get_historical('TCS', '2025-04-01', '2025-07-01')
    """

    def __init__(self, host: str | None = None, timeout: int = 10, default_headers: dict[str, str] | None = None) -> None:
        """Initializes the NSEClient."""
        self.host = host or NSE_HOST_URL
        self.timeout = timeout
        self.default_headers = {
            "Authority": "www.nseindia.com",
            "Referer": "https://www.nseindia.com/",
            "Accept": "*/*",
            "Origin": "https://www.nseindia.com",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "application/json, text/plain, */*",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        }
        if default_headers:
            self.default_headers.update(default_headers)

    def get_metadata(self, symbol: str) -> dict[str, Any]:
        endpoint = METADATA_ENDPOINT.format(symbol=symbol)
        resp = self._request(endpoint, params={"symbol": symbol})
        return resp.json()

    def get_historical(self, symbol: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_formatted = start_dt.strftime("%d-%m-%Y")
            end_formatted = end_dt.strftime("%d-%m-%Y")
        except Exception:
            start_formatted = start_date
            end_formatted = end_date

        params = {
            "from": start_formatted,
            "to": end_formatted,
            "symbol": symbol,
            "type": "priceVolumeDeliverable",
            "series": "ALL",
        }

        resp = self._request(HISTORICAL_ENDPOINT, params=params)
        return resp.json()["data"]

    def _request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        method: str = "get",
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> requests.Response:
        """Internal request method: always treats `path` as an internal path and
        prefixes the configured host. This is intentionally private.
        """
        url = self.host.rstrip("/") + "/" + path.lstrip("/")

        headers_to_use = self.default_headers.copy()
        if headers:
            headers_to_use.update(headers)

        resp = requests.request(
            method,
            url,
            params=params,
            headers=headers_to_use,
            timeout=timeout or self.timeout,
        )
        resp.raise_for_status()
        return resp


# Default module-level client for convenience / backward compatibility
default_client = NSEClient()


# Thin module helpers that delegate to the default client (keeps older usage working)
def get_metadata(symbol: str) -> dict[str, Any]:
    return default_client.get_metadata(symbol)


def get_historical(symbol: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    return default_client.get_historical(symbol, start_date, end_date)
