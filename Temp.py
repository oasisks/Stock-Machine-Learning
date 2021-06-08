from twelvedata import TDClient
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".idea/.env")

APIKEY = os.getenv("APIKEY")

td = TDClient(apikey=APIKEY)
ts = td.time_series(
    symbol="SNDL",
    interval="5min"
)

print(ts.as_json())
