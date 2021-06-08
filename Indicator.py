from StockData import StockData


class IndicatorBase:
    def __init__(self, ticker):
        self.ticker = StockData