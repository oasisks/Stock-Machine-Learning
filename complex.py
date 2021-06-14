from dotenv import load_dotenv
import json
import requests
import os

# initialization
load_dotenv(dotenv_path=".idea/.env")
APIKEY = os.getenv("APIKEY")

url = "https://api.twelvedata.com/complex_data?apikey=" + str(APIKEY)

data = {
    "symbols": ["AAPL", "MSFT", "GOOG"],
    "intervals": ["1day"],
    "outputsize": 25,
    "methods": [
        "time_series",
        {
            "name": "ema",
            "time_period": 12
        }

    ]
}

data = json.dumps(data)

request = requests.post(url, data)

print(request.text)