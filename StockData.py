from datetime import datetime


class Stock:
    def __init__(self, rawData: dict):
        self._rawData = rawData

    @property
    def datetime(self):
        # year-month-date hour-minute-second
        return processRawDateTime(self._rawData["datetime"])

    @property
    def open(self):
        return float(self._rawData["open"])

    @property
    def high(self):
        return float(self._rawData["high"])

    @property
    def low(self):
        return float(self._rawData["low"])

    @property
    def close(self):
        return float(self._rawData["close"])

    @property
    def volume(self):
        return float(self._rawData["volume"])


def processRawDateTime(rawDateTime):
    # year-month-date hour-minute-second
    rawDatetime = rawDateTime.split(" ")
    if len(rawDatetime) > 1:
        date, time = rawDatetime
        year, month, day = [int(x) for x in date.split("-")]
        hour, minute, second = [int(y) for y in time.split(":")]
        datetimeObject = datetime(year=year, month=month, day=day, hour=hour, minute=minute,
                                  second=second)
    else:
        date = rawDatetime[0]
        year, month, day = [int(x) for x in date.split("-")]
        datetimeObject = datetime(year=year, month=month, day=day)

    return datetimeObject


if __name__ == '__main__':
    data = {'datetime': '2021-06-08 12:05:00', 'open': '1.13500',
            'high': '1.14000', 'low': '1.13000', 'close': '1.14000',
            'volume': '472793'}
    stock = Stock(data)
