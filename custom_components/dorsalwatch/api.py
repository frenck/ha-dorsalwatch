"""DorsalWatch API client."""
import logging
import requests
from typing import List, Dict, Any, Optional

from .const import API_URL

_LOGGER = logging.getLogger(__name__)


class DorsalWatchAPI:
    """API client for DorsalWatch."""

    def __init__(
        self,
        country: str,
        public_key: str,
        state: Optional[str] = None,
        page_size: int = 12,
        time_range: int = 0,
    ):
        """Initialize the API client."""
        self.country = country
        self.state = state
        self.public_key = public_key
        self.page_size = page_size
        self.time_range = time_range

    def get_reports(self) -> List[Dict[str, Any]]:
        """Get reports from DorsalWatch API."""
        payload = {
            "country": self.country,
            "pageIndex": 0,
            "pageSize": self.page_size,
            "publicKey": self.public_key,
            "timeRange": self.time_range,
        }

        if self.state:
            payload["state"] = self.state

        headers = {"Content-Type": "application/json"}

        try:
            _LOGGER.debug("Fetching reports from DorsalWatch API")
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            json_data = response.json()

            # Handle the API response structure - extract responseData array
            if isinstance(json_data, dict) and "responseData" in json_data:
                reports = json_data["responseData"]
                _LOGGER.debug(f"Received {len(reports)} reports from responseData array")
                return reports
            elif isinstance(json_data, list):
                _LOGGER.debug(f"Received {len(json_data)} reports as direct list")
                return json_data
            else:
                _LOGGER.debug("Received single report, converting to list")
                return [json_data]

        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Request failed: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error: {e}")
            raise