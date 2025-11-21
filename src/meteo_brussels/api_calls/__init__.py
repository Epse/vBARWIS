import requests
import logging
from typing import Any
from sensor_types import Reading

PAGE_URL = "https://www.batc.be/en/meteo/meteo-readings"
API_URL = "https://www.batc.be/en/api/visualisation/meteo"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
FAKE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": USER_AGENT,
    "DNT": "1",
}

class BatcAPI():
	session: requests.Session = requests.Session()
	log = logging.getLogger("BatcAPI")

	def setup_cookies(self) -> None:
		"""The purpose of this is to set up some plausibly deniable cookies for the following requests"""
		response = self.session.get(PAGE_URL, headers=FAKE_HEADERS)
		self.log.info(f"Setup request got {response.status_code}")

	def fetch_doc(self) -> dict[str, Any] | None:
		response = self.session.get(API_URL, headers=FAKE_HEADERS)
		if response.status_code != 200:
			self.log.warning(f"Bad response from api, got status: {response.status_code} and {response.request.headers}")
			return None
		return response.json()

	def get_latest_reading(self, fetched: dict[str, Any] | None = None) -> Reading | None:
		data = fetched or self.fetch_doc()
		if not data:
			return None
		data = data['data']
		latest = data['timepoints'][data['currentLabel']]
		return Reading.model_validate(latest)

	def close(self):
         self.session.close()