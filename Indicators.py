import pandas as pd
import numpy as np


# TODO Make MA, ADX, Bbands, EMA, MACD, PercentB, RSI, STOCH


class Indicators:
    def __init__(self, data):
        # Ticker, Date, Open, High, Low, Close, Volume

        self._df = pd.DataFrame(data[::-1], columns=["Ticker", "Date", "Open", "High", "Low", "Close", "Volume"])
        print(self._df.to_string())

    def SMA(self, periods=15) -> dict:
        """

        :param periods: the number of periods in days
        :return: dict
        """
        # it needs to return a dictionary
        smas = {}
        queue = []

        for index in range(len(self._df.index)):
            if len(queue) > periods:
                queue.pop(0)  # pop the first one out
            date = self._df.Date[index]
            close = self._df.Close[index]

            queue.append(float(close))

            sumOfClose = sum(queue)
            sma = sumOfClose / len(queue)
            smas[date] = sma

        for key, value in smas.items():
            print(key, value)
        return smas

    def ADX(self, periods=14):

        pass

    def BBands(self, periods=20, std=2):
        """

        :param periods: the number of periods
        :param std: the number of standard deviation
        :return: dict
        """
        queue = []
        bbands = {}
        for index in range(len(self._df.index)):
            if len(queue) > periods:
                queue.pop(0)  # pop the first one out

            date = self._df.Date[index]
            close = self._df.Close[index]

            queue.append(float(close))

            standardDeviation = np.std(queue, dtype=np.float32)

            middleBand = sum(queue) / len(queue)
            upperBand = middleBand + standardDeviation * std
            lowerBand = middleBand - standardDeviation * std

            bbands[date] = {"upperBand": upperBand, "middleBand": middleBand, "lowerBand": lowerBand}

        return bbands

    def EMA(self):
        pass

    def MACD(self):
        pass

    def PercentB(self):
        pass

    def RSI(self):
        pass

    def STOCH(self):
        pass
