import pandas as pd
import numpy as np


# TODO Make MA, ADX, Bbands, EMA, MACD, PercentB, RSI, STOCH
# df: Ticker, Date, Open, High, Low, Close, Volume

def SMA(df: pd.DataFrame, periods=15):
    smas = {}
    queue = []

    for index in range(len(df.index)):
        date = df.Date[index]
        close = df.Close[index]
        if len(queue) > periods:
            queue.pop(0)  # pop the first one out

        # only calculate sma on the periodth date
        if index < periods - 1:
            smas[date] = None, None
            continue

        queue.append(float(close))

        sumOfClose = sum(queue)
        sma = sumOfClose / len(queue)
        standardDeviation = np.std(queue, dtype=np.float32)
        smas[date] = sma, standardDeviation
        return smas


def ADX(df, periods=14):
    plusDMs = {}
    minusDMs = {}
    
    for index in range(len(df.index)):
        date = df.Date[index]
        currentHigh = df.High[index]
        currentLow = df.Low[index]
        # if its the first entry
        if index == 0:
            if currentHigh > currentLow > 0:
                plusDMs[date] = currentHigh
            else:
                plusDMs[date] = 0

            if currentLow > currentHigh > 0:
                minusDMs[date] = currentLow
            else:
                plusDMs[date] = 0

        plusDM = currentHigh - df.High[index - 1]
        minusDM = df.Low[index - 1] - currentLow

        if plusDM > minusDM > 0:
            plusDMs[date] = plusDM
        else:
            plusDMs[date] = 0

        if minusDM > plusDM > 0:
            minusDMs[date] = minusDM
        else:
            minusDMs[date] = 0
        
        # after collecting period amount of direction movement values
        if len(plusDMs) == periods:
            smoothedPlusDMs = sum(plusDMs) - (sum(plusDMs) / periods) + plusDM
            smoothedMinusDMs = sum(minusDMs) - (sum(minusDMs) / periods) + minusDM
            

def ATR(df, periods=14):
    atrs = {}
    trs = []
    for index in range(len(df.index)):
        date = df.Date[index]
        high = df.High[index]
        low = df.Low[index]
        closingPrice = df.Close[index]

        if index < periods - 1:
            atrs[date] = None

        tr = max([high - low, abs(high - closingPrice), abs(low - closingPrice)])

        trs.append(tr)

        if len(trs) == periods:
            atr = sum(trs) / periods
            atrs[date] = atr
            trs.pop(0)

    return atrs


def DM(df, periods=14):
    plusDMs = {}
    minusDMs = {}
    data = []

    for index in range(len(df.index)):
        date = df.Date[index]
        currentHigh = float(df.High[index])
        currentLow = float(df.Low[index])
        # if its the first entry
        if index == 0:
            if currentHigh > currentLow and currentHigh > 0:
                plusDMs[date] = currentHigh
            else:
                plusDMs[date] = 0

            if currentLow > currentHigh and currentLow > 0:
                minusDMs[date] = currentLow
            else:
                minusDMs[date] = 0
            data.append([date, plusDMs[date], minusDMs[date]])
            continue

        plusDM = currentHigh - float(df.High[index - 1])
        minusDM = float(df.Low[index - 1]) - currentLow

        if plusDM > minusDM and plusDM > 0:
            plusDMs[date] = plusDM
        else:
            plusDMs[date] = 0

        if minusDM > plusDM and minusDM > 0:
            minusDMs[date] = minusDM
        else:
            minusDMs[date] = 0
        data.append([date, plusDMs[date], minusDMs[date]])

    df = pd.DataFrame(data, columns=["Date", "Plus", "Minus"])

    print(df.to_string())


def DI(df, periods=14):
    pass

#
# def EMAForADX(df, periods=14):
#     numRows, numCols = df.shape
#
#     values = []
#     for i in range(0, numRows):
#         if i < periods - 1:



def BBands(df: pd.DataFrame, periods=20, std=2):
    """

    :param df: the dataframe
    :param periods: the number of periods
    :param std: the number of standard deviation
    :return: dict
    """
    smas = SMA(df, periods=periods)
    bbands = {}

    for date, smaStd in smas.items():
        (sma, standardDeviation) = smaStd
        if sma is None and standardDeviation is None:
            bbands[date] = {"middleBand": None, "upperBand": None, "lowerBand": None}
            continue
        upperBand = sma + std * standardDeviation
        lowerBand = sma - std * standardDeviation

        bbands[date] = {"middleBand": sma, "upperBand": upperBand, "lowerBand": lowerBand}
    return bbands


def EMA(df: pd.DataFrame, periods=10, smoothingMultiplier=2):
    """

    :param df: the dataframe
    :param periods: the number of periods
    :param smoothingMultiplier: the numerator of the multiplier 
    :return: dict
    """
    # Calculate SMA
    smas = SMA(df=df, periods=periods)

    # Calculate multiplier
    multiplier = smoothingMultiplier / (periods + 1)

    # Calculate EMA
    emas = {}
    dates = []
    for index in range(len(df.index)):
        # print(f"Current Index: {index}, Previous Index: {index- 1}, Length of list: {len(self.df.index)}")
        date = df.Date[index]
        close = float(df.Close[index])
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

    return emas


def MACD(df: pd.DataFrame, shortTermPeriod=12, longTermPeriod=26):
    """
    
    :param df: the dataframe
    :param shortTermPeriod: the signal
    :param longTermPeriod: the MACD Line
    :return: 
    """
    shortTermEMAs = EMA(df=df, periods=shortTermPeriod)
    longTermEMAs = EMA(df=df, periods=longTermPeriod)

    macds = {}

    for date in longTermEMAs:
        longTermEMA = longTermEMAs[date]

        if longTermEMA is None:
            macds[date] = None
            continue

        macds[date] = shortTermEMAs[date] - longTermEMAs[date]

    return macds


def RSI(df, periods):
    pass


def STOCH(df, periods):
    pass
