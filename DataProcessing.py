from twelvedata import TDClient
from twelvedata.exceptions import BadRequestError
from twelvedata import TDClient
from dotenv import load_dotenv
from json import dump, load
from datetime import datetime
from StockData import StockDatumEntry, processRawDateTime
import os
import sqlite3


# Twelve Data API: https://twelvedata.com/docs#getting-started
# Twelve Data GitHub: https://github.com/twelvedata/twelvedata-python

# initialization
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


def getData(symbols, interval: str, startDate: str, endDate: str, outputSize=5000):
    td = TDClient(apikey=APIKEY)
    try:
        ts = td.time_series(
            symbol=symbols,
            interval=interval,
            start_date=startDate,
            end_date=endDate,
            outputsize=outputSize
        )
        data = ts.with_adx().with_bbands().with_ema().with_macd().with_percent_b().with_rsi().with_stoch().as_json()
        for datum in data:
            print(datum)
        saveJsonFile("data.json", data)
    except BadRequestError as e:
        print("The given symbol does is not within twelve data API. The program will skip this entry")


def loadData(fileName) -> dict:
    file = open(fileName, "r", encoding="utf-8")
    data = load(file)

    stockData = {}
    for index, datum in enumerate(data):
        # print(datum)
        stock = StockDatumEntry(datum)
        stockData[stock.datetime] = stock

    return stockData


def createConnection(dbFile):
    conn = sqlite3.connect(dbFile)
    return conn


def createTable(conn, createTableSQL):
    c = conn.cursor()
    c.execute(createTableSQL)
    print("Table has been created")


def insertData(conn, insertDataSQL):
    c = conn.cursor()
    c.execute(insertDataSQL)
    print("Data has been inserted")


def createDatabase(tickersFile):
    conn = createConnection("data.db")
    SQL_COMMAND_CREATE_TABLE = '''CREATE TABLE Stocks
                                (Ticker varchar(255),
                                Date datetime,
                                Open price,
                                High price,
                                Low price,
                                Close price,
                                Volume float,
                                Adx text,
                                Bbands text,
                                EMA text,
                                MACD text,
                                PercentB text,
                                RSI text,
                                STOCH text);'''
    createTable(conn, createTableSQL=SQL_COMMAND_CREATE_TABLE)
    for ticker in tickersFile:
        getData(ticker, "1day", "2020-04-01", "2021-05-30")
        stockData = loadData("data.json")
        for date, data in stockData.items():
            SQL_COMMAND_INSERT_DATA = f'''INSERT INTO Stocks
                                        (Ticker,
                                        Date,
                                        Open,
                                        High,
                                        Low,
                                        Close,
                                        Volume,
                                        Adx,
                                        Bbands,
                                        EMA,
                                        MACD,
                                        PercentB,
                                        RSI,
                                        STOCH) VALUES 
                                        ({ticker}, {str(data.datetime)}, {data.open},
                                        {data.high}, {data.low}, {data.close}, {data.volume},
                                        {str(data.indicators.adx)}, {str(data.indicators.bbands)},
                                        {str(data.indicators.ema)}, {str(data.indicators.macd)},
                                        {str(data.indicators.rsi)}, {str(data.indicators.stoch)});'''
            insertData(conn, SQL_COMMAND_INSERT_DATA)


# stockData = loadData("data.json")
#
# date = processRawDateTime("2020-05-05")
#
# conn = createConnection("data.db")
#
# #
# # createTable(conn, SQLCOMMAND)
# conn.cursor().execute('''INSERT INTO SNDL (Ticker, Date) Values ('SNDL', '2021-05-01 00:00:00')''')

tickers = open("tickers.txt", "r", encoding="utf-8")

