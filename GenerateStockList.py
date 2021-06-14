import csv

tickers = []
with open("12data_stocks.csv", "r", encoding="utf-8") as csvFile:
    csvReader = csv.DictReader(csvFile, delimiter=";")

    count = 0
    for index, row in enumerate(csvReader):
        # we only want NYSE and NASDAQ (for now at least)
        if row["exchange"] in ["NYSE", "NASDAQ"]:
            tickers.append(row["symbol"].strip("\n"))

print(tickers)
tickersFile = open("tickers.txt", "w", encoding="utf-8")

tickersFile.write("\n".join(tickers))

tickersFile.close()
