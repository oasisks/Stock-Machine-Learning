from twelvedata.exceptions import BadRequestError, TwelveDataError
from twelvedata import TDClient
from dotenv import load_dotenv
from time import sleep
from json import dump, load
from Indicators import Indicators
from datetime import datetime
import os
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


def saveProgress(tickers, fileName="progress.txt"):
    progressFile = open(fileName, "a", encoding="utf-8")
    tickers[0] = "\n" + tickers[0]
    progressFile.write("\n".join(tickers))
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
        elif position == len(tickers) - 1:
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


def processData():
    # create a connection to a data.db which contains the basic numeric information to perform indicator calculations
    dataConn = createConnection()

    # create another connection to a database file that will store the data in data.db and indicator values
    newDataConn = createConnection(dbFile=".idea/completeData.db")

    tickersFile = open("tickers.txt", "r", encoding="utf-8")
    tickers = [ticker.strip("\n") for ticker in tickersFile]
    tickersFile.close()

    for ticker in tickers:
        data = selectDataByTicker(dataConn, ticker)

        # for row in data:
        #     print(row)
        indicators = Indicators(data)
        indicators.SMA()

        break


getData()

# processData()
