#data = read.csv(file.choose())
#uniques = unique(data["Ticker"])

#print(unique(data[]))
directory = "C:/Users/brian/Stonk/Data"
finishedStocks <- function() {
  files = list.files(path = directory)
  tickers = c()
  
  for (file in files){
    file = strsplit(file, "[.]")
    ticker = file[[1]][1]
    tickers = append(tickers, ticker)
  }
  
  return(tickers)
}
library(TTR)
badTickers = c()

stocks = finishedStocks()
for (ticker in uniques$Ticker) {
  # Before performing any calculations, we need to check if the ticker has
  # already been calculated
  if (ticker %in% stocks){
    # if the ticker already exists then we continue
    print(paste("ALREADY DID", ticker, sep = " "))
    next
  }

  # getting the desired data
  matrix = data[data$Ticker == ticker, ]
  matrix = matrix[nrow(matrix):1, ]

  highLowClose = matrix[,c("High", "Low", "Close")]
  closingPrice = matrix[,"Close"]
  dates = matrix[, "Date"]

  an.error.occured <- FALSE
  tryCatch( {adx = ADX(highLowClose); c_stoch = stoch(highLowClose); bband = BBands(highLowClose); rsi = RSI(closingPrice); sma = SMA(closingPrice, n = 25); ema = EMA(closingPrice, n = 14); macd = MACD(closingPrice)}
            ,error = function(e) {an.error.occured <<- TRUE})
  if (an.error.occured == TRUE) {
    badTickerFile = paste(directory, "badTicker.txt", sep = "/")
    write(ticker, file=badTickerFile, append=TRUE, sep = "\n")
  }
  else {
    # Once the program has calculated all of the values
    df = data.frame("Date"= dates, "ADX"= adx[, "ADX"], "STOCHFK" = c_stoch[, "fastK"],
                    "STOCHFD" = c_stoch[, "fastD"], "STOCHSD" = c_stoch[, "slowD"],
                    "BBandsUp" = bband[, "up"], "BbandsDn" = bband[, "dn"],
                    "BbandsMiddle" = bband[, "mavg"], "PercentB" = bband[, "pctB"],
                    "RSI" = rsi, "SMA" = sma, "EMA" = ema, "MACD" = macd[, "macd"],
                    "Signal" = macd[, "signal"])
    csvFileName = paste(ticker, "csv", sep = ".")
    fileDirectory = paste(directory, csvFileName, sep = "/")
    write.csv(df, fileDirectory)
  }
}
