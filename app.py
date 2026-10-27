import os
import threading
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)

CITY = os.getenv("WEATHER_CITY", "Kolkata")
BLYNK_TOKEN = os.getenv("BLYNK_AUTH_TOKEN", "").strip()
WEATHER_URL = f"https://wttr.in/{CITY}?format=j1"
BLYNK_UPDATE_URL = "https://blynk.cloud/external/api/update"

state = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "updated_at": None,
    "weather_source": "wttr.in",
    "blynk_status": "Not configured" if not BLYNK_TOKEN else "Waiting for first update",
    "error": None,
}
state_lock = threading.Lock()


def get_weather():
    """Fetch current weather data from wttr.in."""
    response = requests.get(
        WEATHER_URL,
        headers={"User-Agent": "OnlineWeatherMonitoringStation/1.0"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    current = payload["current_condition"][0]

    return {
        "temperature": float(current["temp_C"]),
        "humidity": float(current["humidity"]),
        "pressure": float(current["pressure"]),
    }


def send_to_blynk(values):
    """Send values to the Blynk datastreams V0, V1, and V2."""
    if not BLYNK_TOKEN:
        return "Not configured (set BLYNK_AUTH_TOKEN)"

    params = {
        "token": BLYNK_TOKEN,
        "v0": values["temperature"],
        "v1": values["humidity"],
        "v2": values["pressure"],
    }
    response = requests.get(BLYNK_UPDATE_URL, params=params, timeout=15)
    response.raise_for_status()
    return f"HTTP {response.status_code}"


def refresh_loop():
    """Refresh the cached readings once per minute."""
    while True:
        try:
            values = get_weather()
            try:
                blynk_status = send_to_blynk(values)
            except requests.RequestException as exc:
                blynk_status = f"Update failed: {exc}"

            with state_lock:
                state.update(values)
                state["updated_at"] = datetime.now(timezone.utc).isoformat()
                state["blynk_status"] = blynk_status
                state["error"] = None
        except Exception as exc:
            with state_lock:
                state["error"] = str(exc)

        time.sleep(60)


@app.route("/")
def home():
    return render_template("index.html", city=CITY)


@app.route("/api/weather")
def api_weather():
    with state_lock:
        snapshot = dict(state)

    if snapshot["temperature"] is None:
        return jsonify({
            **snapshot,
            "message": "Waiting for the first weather update. Check your internet connection.",
        }), 503

    return jsonify(snapshot)


# Start one background updater for the local development server.
# For a production deployment, use a dedicated worker/scheduler.
_worker_started = False
_worker_lock = threading.Lock()


@app.before_request
def start_worker_once():
    global _worker_started
    with _worker_lock:
        if not _worker_started:
            threading.Thread(target=refresh_loop, daemon=True).start()
            _worker_started = True


if __name__ == "__main__":
    app.run(debug=True)
