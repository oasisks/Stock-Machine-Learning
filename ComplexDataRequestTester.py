from dotenv import load_dotenv
from os import getenv
import requests

# load_dotenv(dotenv_path=".idea/.env")
# APIKEY = getenv("APIKEY")
#
# url = "https://api.twelvedata.com/complex_data?apikey=" + str(APIKEY)
#
#
# data = '''{
#     "symbols": ["AAPL", "MSFT", "GOOG"],
#     "intervals": ["5min", "1day"],
#     "outputsize": 25,
#     "methods": [
#         "time_series",
#         {
#             "name": "ema",
#             "time_period": 12
#         },
#         "quote",
#         {
#             "name": "adx",
#             "symbol": ["MMM"],
#             "order": "ASC"
#         }
#     ]
# }'''
#
#
# request = requests.post(url, data=data)
# print(request.text)

file = open("lol.txt", "r", encoding="utf-8")

for line in file:
    print(line)
