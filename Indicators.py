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
            date = self._df.Date[index]
            close = self._df.Close[index]
            if len(queue) > periods:
                queue.pop(0)  # pop the first one out

            # only calculate sma on the periodth date
            if index < periods - 1:
                smas[date] = None, None
                continue

            queue.append(float(close))

            sumOfClose = sum(queue)
            sma = sumOfClose / len(queue)
            standardDevation = np.std(queue, dtype=np.float32)
            smas[date] = sma, standardDevation
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
            if sma is None and standardDeviation is None:
                bbands[date] = {"middleBand": None, "upperBand": None, "lowerBand": None}
                continue
            upperBand = sma + std * standardDeviation
            lowerBand = sma - std * standardDeviation

            bbands[date] = {"middleBand": sma, "upperBand": upperBand, "lowerBand": lowerBand}

        for key, value in bbands.items():
            print(f"Date: {key}, Data: {value}")
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
            # print(f"Current Index: {index}, Previous Index: {index- 1}, Length of list: {len(self._df.index)}")
            date = self._df.Date[index]
            close = float(self._df.Close[index])
            # we can only calculate ema after period
            if index < periods - 1:
                emas[date] = None
                dates.append(date)
                continue
            elif index == periods - 1:
                # the ema for this day will just be the simple moving average of that day
                emas[date] = smas[date][0]
                dates.append(date)
                continue
            dates.append(date)

            ema = close * multiplier + emas[dates[index - 1]] * (1 - multiplier)

            emas[date] = ema

        for date, value in emas.items():
            print(f"Date: {date}, EMA: {value}")

        return emas

    def MACD(self, shortTermPeriod=12, longTermPeriod=26):
        shortTermEMAs = self.EMA(periods=shortTermPeriod)
        longTermEMAs = self.EMA(periods=longTermPeriod)

        macds = {}

        for date in longTermEMAs:
            longTermEMA = longTermEMAs[date]

            if longTermEMA is None:
                macds[date] = None
                continue

            macds[date] = shortTermEMAs[date] - longTermEMAs[date]

        return macds

    def RSI(self):
        pass

    def STOCH(self):
        pass
