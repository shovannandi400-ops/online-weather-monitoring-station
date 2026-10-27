# Online Weather Monitoring Station

A hardware-free student project that fetches current weather for Kolkata from `wttr.in`, displays temperature/humidity/pressure on a Flask website, and optionally sends the readings to Blynk Cloud.

## Features

- Python weather data retrieval
- Flask web dashboard
- Temperature (°C), humidity (%), and pressure (hPa)
- Optional Blynk updates through Virtual Pins V0, V1, and V2
- Refreshes the weather data approximately every 60 seconds
- Blynk token is read from an environment variable, not stored in source code

## Project structure

```text
online-weather-monitoring-station/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── templates/
    └── index.html
```

## Requirements

- Python 3.10 or newer
- Internet access
- A Blynk template/device with:
  - V0: Temperature (Double)
  - V1: Humidity (Double)
  - V2: Pressure (Double)

This project uses online weather data. It does **not** measure conditions with physical sensors.

## Run on Windows PowerShell

1. Open this folder in VS Code.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Set your own Blynk token in the current terminal (optional; omit this step if not using Blynk):

   ```powershell
   $env:BLYNK_AUTH_TOKEN="YOUR_OWN_BLYNK_TOKEN"
   ```

4. Run the website:

   ```powershell
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

The first weather request can take a few seconds. Keep the terminal running while using the dashboard.

## Blynk setup

Create three datastreams in Blynk:

| Virtual pin | Name | Unit |
|---|---|---|
| V0 | Temperature | °C |
| V1 | Humidity | % |
| V2 | Pressure | hPa |

Set `BLYNK_AUTH_TOKEN` to the device's own token. Do not publish a real token in GitHub, screenshots, or chat. If a token has been exposed, regenerate it in Blynk Console.

A successful HTTP request does not by itself mean that the Blynk device status will show Online. This project sends readings using the Blynk HTTP API; device connectivity status is separate.

## Troubleshooting

- **No data:** Check internet access and whether `wttr.in` is reachable.
- **Blynk update fails:** Check the token and datastream pin names.
- **Website says token is not configured:** Set the `BLYNK_AUTH_TOKEN` environment variable before starting `python app.py`.
- **Port 5000 is busy:** Stop the other app using that port or change the port in `app.py`.

## Security

Never commit a real Blynk token. The `.gitignore` excludes `.env`, but still review files before pushing to GitHub.

## Future improvements

- Host the Flask app online
- Add historical charts and weather-condition icons
- Add unit tests and more robust API error handling

## License

MIT License — see `LICENSE`.
