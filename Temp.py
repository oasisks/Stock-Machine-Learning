from twelvedata import TDClient
from dotenv import load_dotenv
from json import dump, load
from datetime import datetime
from StockData import StockDatumEntry, processRawDateTime
import os


load_dotenv(dotenv_path=".idea/.env")

APIKEY = os.getenv("APIKEY")


def saveJsonFile(fileName, data):
    with open(fileName, "w") as jsonFile:
        dump(data, jsonFile)


def priceDifference(stockData: dict, startDate: str, endDate: str) -> float:
    """

    :param startDate: yyyy-mm-dd
    :param endDate: yyyy-mm-dd
    :return: float
    """
    startDate = processRawDateTime(startDate)
    endDate = processRawDateTime(endDate)
    print(endDate - startDate)
    return stockData[endDate].open - stockData[startDate].open

# Twelve Data API: https://twelvedata.com/docs#getting-started
# Twelve Data GitHub: https://github.com/twelvedata/twelvedata-python


# td = TDClient(apikey=APIKEY)
# ts = td.time_series(
#     symbol="SNDL",
#     interval="1day",
#     timezone="America/New_York",
#     start_date="2020-05-01",
#     end_date="2021-05-02",
#     outputsize=5000
# )
#
# saveJsonFile("data.json", ts.with_adx().with_bbands().with_ema().with_macd().with_percent_b().with_rsi().with_stoch().as_json())

file = open("data.json", "r", encoding="utf-8")

data = load(file)

stockData = {}
for index, datum in enumerate(data):
    print(datum)
    stock = StockDatumEntry(datum)
    stockData[stock.datetime] = stock

# print(stockData)
# print(priceDifference(stockData, "2020-05-01", "2021-04-30"))
