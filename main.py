import requests
import logging
from pydantic import BaseModel
import tkinter as tk
from typing import Any
from sensor_types import Reading

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

PAGE_URL = "https://www.batc.be/en/meteo/meteo-readings"
API_URL = "https://www.batc.be/en/api/visualisation/meteo"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0"
FAKE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": USER_AGENT,
    "DNT": "1",
}

session: requests.Session = requests.Session()

def setup_cookies():
    response = session.get(PAGE_URL, headers=FAKE_HEADERS)
    log.info(f"Setup request got {response.status_code}")
    print(f"Setup request got {response.status_code}")

def fetch_doc() -> dict[str, Any] | None:
    global session
    response = session.get(API_URL, headers=FAKE_HEADERS)
    if response.status_code != 200:
        log.warning(f"Bad response from api, got status: {response.status_code} and {response.request.headers}")
        return None
    return response.json()

def get_latest_reading() -> Reading | None:
    data = fetch_doc()
    if not data:
        return None
    data = data['data']
    latest = data['timepoints'][data['currentLabel']]
    return Reading.model_validate(latest)

class Application(tk.Frame):
    reading: Reading | None = None

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.reading = get_latest_reading()
        self.createWidgets()

    def createWidgets(self) -> None:
        # Make top level window stretch
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.columnconfigure(1, weight=1)

        if self.reading is None:
            self.label = tk.Label(self, text="No meteo information found")
            self.label.grid()
            return

        for (idx, key) in enumerate(self.reading.wind_sensor_detail):
            print(idx, key)
            label = tk.Label(self, text=key)
            label.grid(column=0, row=idx)
            wind = tk.Label(self, text=self.reading.wind_sensor_detail[key].sensor_reading.to_human())
            wind.grid(column=1, row=idx)
    
    def clear(self):
        for w in self.winfo_children():
            w.destroy()

def main():
    setup_cookies()

    app = Application()
    app.master.title('Meteo Brussels')
    app.mainloop()

    session.close()

if __name__ == "__main__":
    main()
