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
            standardDevation = np.std(queue, dtype=np.float32)
            smas[date] = sma, standardDevation

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
        smas = self.SMA(periods=periods)
        bbands = {}

        for date, smaStd in smas.items():
            (sma, standardDeviation) = smaStd
            upperBand = sma + std * standardDeviation
            lowerBand = sma - std * standardDeviation

            bbands[date] = {"middleBand": sma, "upperBand": upperBand, "lowerBand": lowerBand}

        return bbands

    def EMA(self, periods=10):
        """

        :param periods: the number of periods
        :return: dict
        """
        # Calculate SMA
        smas = self.SMA(periods=periods)

        # Calculate multiplier
        multiplier = 2 / (periods + 1)

        # Calculate EMA
        emas = {}
        dates = []
        for index in range(len(self._df.index)):
            date = self._df.Date[index]
            close = self._df.Close[index]
            # we can only calculate ema after period
            if index < periods - 1:
                emas[date] = None
                dates.append(date)
                continue
            elif index == periods - 1:
                # the ema for this day will just be the simple moving average of that day
                emas[date] = smas[date]
                dates.append(date)
                continue

            ema = close * multiplier + emas[dates[index - 1]] * (1 - multiplier)

            emas[date] = ema

        return emas

    def MACD(self):
        pass

    def PercentB(self):
        pass

    def RSI(self):
        pass

    def STOCH(self):
        pass
