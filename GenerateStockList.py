file = open(
    "nasdaq_screener_1623280440492.csv",
    "r",
    encoding="utf-8"
)

tickers = []
for index, line in enumerate(file):
    if index == 0:
        continue
    line = line.split(",")
    tickers.append(line[0])
    print(line)

print(tickers)
file.close()

tickerFile = open("tickers.txt", "w", encoding="utf-8")

tickerFile.write("\n".join(tickers))

tickerFile.close()
