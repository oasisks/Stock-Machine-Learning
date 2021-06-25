from twelvedata.exceptions import BadRequestError, TwelveDataError
from twelvedata import TDClient
from dotenv import load_dotenv
from time import sleep
from json import dump, load
from datetime import datetime
import os
import csv
import pandas as pd
from json import dump
# import Indicators as indicator
import sqlite3


# Twelve Data API: https://twelvedata.com/docs#getting-started
# Twelve Data GitHub: https://github.com/twelvedata/twelvedata-python

def saveJsonFile(fileName="data.json", data=None):
    """

    :param fileName: the file name of the json file (default is data.json)
    :param data: data in a dictionary
    :return:
    """
    with open(fileName, "a") as jsonFile:
        dump(data, jsonFile)


def saveProgress(tickers: list, fileName="progress.txt"):
    progressFile = open(fileName, "a", encoding="utf-8")
    tickers[0] = "\n" + tickers[0]
    progressFile.write("\n".join(tickers))
    progressFile.close()
    print("SAVED PROGRESS.")


def saveTickerProgress(ticker: str, filename):
    progressFile = open(filename, "w", encoding="utf-8")
    progressFile.write("\n" + ticker)
    progressFile.close()
    print("SAVED PROGRESS.")


def getProgress(fileName="progress.txt"):
    if os.stat(fileName).st_size == 0:
        return None

    progressFile = open(fileName, "r", encoding="utf-8")
    progress = [ticker.strip("\n") for ticker in progressFile]

    return progress


def createConnection(dbFile=".idea/data.db"):
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


def selectDataByTicker(conn, ticker):
    cur = conn.cursor()
    cur.execute("SELECT * FROM Stocks WHERE Ticker=?", (ticker,))

    rows = cur.fetchall()

    return rows


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


# initialization
load_dotenv(dotenv_path=".idea/.env")
APIKEY = os.getenv("APIKEY")


def getData():
    td = TDClient(apikey=APIKEY)

    tickersFile = open("tickers.txt", "r", encoding="utf-8")
    tickers = [ticker.strip("\n") for ticker in tickersFile]
    tickersFile.close()

    tickerBatch = []
    index = 1

    # at the start of the program, we extract the current progress
    progress = getProgress()  # list of ticker or None

    # database connection object
    conn = createConnection()

    if not tableExists(conn, "Stocks"):
        SQL_COMMAND_CREATE_TABLE = '''CREATE TABLE Stocks
                                    (Ticker text,
                                    Date text,
                                    Open text,
                                    High text,
                                    Low text,
                                    Close text,
                                    Volume text);'''
        createTable(conn, SQL_COMMAND_CREATE_TABLE)

    for position, ticker in enumerate(tickers):
        ticker = ticker.strip("\n")
        if progress is not None:
            progress = set(progress)
            if ticker in progress:
                # we already finished this ticker
                continue
        if index % 9 != 0:
            tickerBatch.append(ticker)
        # we are at the last ticker
        elif position == len(tickers):
            # we will do a request with whatever is left
            ts = td.time_series(
                symbol=tickerBatch,
                interval="1day",
                start_date="2000-01-01",
                outputsize=5000
            )
            cachedData = ts.as_json()

            for cTicker, cData in cachedData.items():
                for entry in cData:
                    SQL_COMMAND_INSERT_DATA = f'''INSERT INTO Stocks (Ticker, Date, Open, High, Low, Close, Volume)
                    Values ("{cTicker}", "{entry["datetime"]}", "{entry["open"]}", "{entry["high"]}", "{entry["low"]}",
                    "{entry["low"]}", "{entry["volume"]}")'''
                    insertData(conn, insertDataSQL=SQL_COMMAND_INSERT_DATA)

            conn.commit()
            saveProgress(tickerBatch)
        else:
            # do the batch request here
            ts = td.time_series(
                symbol=tickerBatch,
                interval="1day",
                start_date="2000-01-01",
                outputsize=5000
            )
            cachedData = ts.as_json()

            for cTicker, cData in cachedData.items():
                for entry in cData:
                    SQL_COMMAND_INSERT_DATA = f'''INSERT INTO Stocks (Ticker, Date, Open, High, Low, Close, Volume)
                    Values ("{cTicker}", "{entry["datetime"]}", "{entry["open"]}", "{entry["high"]}", "{entry["low"]}",
                    "{entry["low"]}", "{entry["volume"]}")'''
                    insertData(conn, insertDataSQL=SQL_COMMAND_INSERT_DATA)

            conn.commit()
            saveProgress(tickerBatch)

            # the program will sleep for approximately 60 seconds
            for sec in range(1, 61):
                print(f"Program Sleeping for {sec}.")
                sleep(1)

            tickerBatch = [ticker]
            index = 1
        index += 1


def convertDataToCSV():
    conn = createConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Stocks")

    rows = cursor.fetchall()

    with open("data.csv", "w", encoding="utf-8", newline='') as file:
        csvWriter = csv.writer(file)
        header = ["Ticker", "Date", "Open", "High", "Low", "Close", "Volume"]

        csvWriter.writerow(header)
        for row in rows:
            print(row)
            csvWriter.writerow(row)


def priceDifference(data: list) -> dict:
    df = pd.DataFrame(data, columns=["Ticker", "Date", "Open", "High", "Low", "Close", "Volume"])
    priceDifferences = {}
    days = [1, 2, 3, 5, 8, 13, 21, 34]
    size = len(df.index)
    for index in range(size):
        date = df.Date[index]
        close = float(df.Close[index])

        c_priceDifferences = {}
        for day in days:
            # if it is not within the dataset
            daysAfter = index + day
            if not daysAfter < size:
                break
            futurePrice = float(df.Close[daysAfter])
            c_priceDifferences[f"{day} Days After"] = futurePrice - close

        priceDifferences[date] = c_priceDifferences

    return priceDifferences


def processData():
    """
    Calculate the price difference between two stocks and record them
    :return:
    """

    # there are some tickers that are not usable for analysis
    badTickers = [x.strip("\n") for x in open("Data/badTicker.txt", "r", encoding="utf-8")]

    # list of tickers
    tickers = [x.strip("\n") for x in open("tickers.txt", "r", encoding="utf-8")]

    conn = createConnection()

    index = 0
    d_Tickers = {}
    for ticker in tickers:
        if ticker in badTickers:
            continue

        tickerData = selectDataByTicker(conn, ticker)

        # if the list is empty
        if not tickerData:
            continue
        tickerData = tickerData[::-1]

        d_Tickers[ticker] = priceDifference(tickerData)

        print(f"Finished {ticker}")

    with open("PriceDifferences.json", "w", encoding="utf-8") as outfile:
        dump(d_Tickers, outfile)


# getData()

# convertDataToCSV()

processData()
