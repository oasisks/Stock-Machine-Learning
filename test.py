from twelvedata import TDClient
from dotenv import load_dotenv
from json import load
import os

load_dotenv(dotenv_path=".idea/.env")
APIKEY = os.getenv("APIKEY")

td = TDClient(apikey=APIKEY)

ts = td.time_series(
    symbol=["GOOG", "VOO", "SNDL"],
    interval="30min",
    outputsize=10
)


df = ts.with_adx().with_bbands().with_ema().with_macd().with_percent_b().with_rsi().with_stoch().as_json()

print(df)
