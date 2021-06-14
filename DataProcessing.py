from twelvedata.exceptions import BadRequestError, TwelveDataError
from twelvedata import TDClient
from dotenv import load_dotenv
from time import sleep
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


def saveJsonFile(fileName="data.json", data=None):
    """

    :param fileName: the file name of the json file (default is data.json)
    :param data: data in a dictionary
    :return:
    """
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


def getData(symbol, interval: str, startDate: str, endDate: str, outputSize=5000):
    """

    :param symbol: the ticker symbol
    :param interval: the interval between each data
    :param startDate: the start date written as yyyy-mm-dd
    :param endDate: the end date written as yyyy-mm-dd
    :param outputSize: the maximum number of data points per request (default is 5000)
    :return: bool
    """
    td = TDClient(apikey=APIKEY)

    def requestData():
        ts = td.time_series(
            symbol=symbol,
            interval=interval,
            start_date=startDate,
            end_date=endDate,
            outputsize=outputSize
        )
        data = ts.with_adx().with_bbands().with_ema().with_macd().with_percent_b().with_rsi().with_stoch().as_json()
        # for datum in data:
        #     print(datum)
        saveJsonFile("data.json", data)

    try:
        requestData()
        return True
    except BadRequestError as be:
        print(f"{be} Skip the ticker {symbol}.")
        return False


def loadData(fileName="data.json") -> dict:
    """

    :param fileName: default is data.json
    :return: a dictionary in this format {datetime: StockDatumEntry}
    """
    file = open(fileName, "r", encoding="utf-8")
    data = load(file)

    stockData = {}
    for index, datum in enumerate(data):
        # print(datum)
        stock = StockDatumEntry(datum)
        stockData[stock.datetime] = stock

    return stockData


def createConnection(dbFile="data.db"):
    """

    :param dbFile: unless specified, the default database that the function will connect to is data.db
    :return: connection object
    """
    conn = sqlite3.connect(dbFile)
    print(f"Connected to {dbFile}")
    return conn


def createTable(conn, createTableSQL: str):
    """

    :param conn: the connection object
    :param createTableSQL: the sql str
    :return:
    """
    c = conn.cursor()
    try:
        c.execute(createTableSQL)
        print("Table has been created")
    except Exception as e:
        print(f"This table already exists within the database. ERROR: {e}")


def insertData(conn, insertDataSQL):
    c = conn.cursor()
    c.execute(insertDataSQL)
    print("Data inserted")


def saveProgress(index, ticker):
    """

    :param index: the current index within the tickers.txt
    :param ticker: the current symbol that the program is extracting data from
    :return:
    """
    file = open("progress.txt", "w", encoding="utf-8")
    file.write(",".join([str(index), str(ticker)]))
    file.close()


def getProgress(fileName: str = "progress.txt"):
    """

    :param fileName: the default file name for the progress is progress.txt
    :return: list [index, tuple]
    """
    file = open("progress.txt", "r", encoding="utf-8")
    progress = None
    # if the progress is not empty
    if not os.stat("progress.txt").st_size == 0:
        for line in file:
            progress = line.split(",")

        file.close()
        return progress

    return progress


def tableExists(conn, tableName):
    """

    :param conn: the connection to the database
    :param tableName: the name of the table
    :return: bool
    """

    c = conn.cursor()

    # get the count
    c.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tableName}' ''')

    # if there is one table with that name in the database
    if c.fetchone()[0] == 1:
        return True

    return False


def update(ticker, conn):
    # we start from the very beginning
    validTicker = getData(ticker, "1day", "2000-01-01", "2015-12-31")

    if validTicker:
        stockData = loadData()  # cached data located in data.json by default

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
                                        ("{str(ticker)}", "{str(data.datetime)}", "{str(data.open)}",
                                        "{str(data.high)}", "{str(data.low)}", "{str(data.close)}", "{str(data.volume)}",
                                        "{str(data.indicators.adx)}", "{str(data.indicators.bbands)}",
                                        "{str(data.indicators.ema)}", "{str(data.indicators.macd)}",
                                        "{str(data.indicators.percentB)}",
                                        "{str(data.indicators.rsi)}", "{str(data.indicators.stoch)}");'''
            insertData(conn, SQL_COMMAND_INSERT_DATA)


def updateDatabase(tickersFileName):
    tickersFile = open(tickersFileName, "r", encoding="utf-8")
    conn = createConnection()

    if not tableExists(conn, "Stocks"):
        SQL_COMMAND_CREATE_TABLE = '''CREATE TABLE Stocks
                                    (Ticker text,
                                    Date text,
                                    Open text,
                                    High text,
                                    Low text,
                                    Close text,
                                    Volume text,
                                    Adx text,
                                    Bbands text,
                                    EMA text,
                                    MACD text,
                                    PercentB text,
                                    RSI text,
                                    STOCH text);'''
        createTable(conn, SQL_COMMAND_CREATE_TABLE)

    for index, ticker in enumerate(tickersFile):
        progress = getProgress()  # [index, ticker]
        print(f"Progress: {progress}, Index: {index}")
        # if there is zero progress
        if progress is None:
            # we start updating from the beginning
            update(ticker, conn)

            # save the current progress
            saveProgress(index, ticker)

            # commit to the database
            conn.commit()
        # if there is progress, we resume from the index + 1 of the previous progress index
        elif index > int(progress[0]):
            update(ticker, conn)

            # save the current progress
            saveProgress(index, ticker)

            # commit to the database
            conn.commit()
        if index == 20:
            break

    conn.close()


# stockData = loadData("data.json")
#
# date = processRawDateTime("2020-05-05")
#
# conn = createConnection("data.db")
#
# #
# # createTable(conn, SQLCOMMAND)
# conn.cursor().execute('''INSERT INTO SNDL (Ticker, Date) Values ('SNDL', '2021-05-01 00:00:00')''')


updateDatabase("tickers.txt")

