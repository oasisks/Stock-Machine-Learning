# from pandas import read_csv
# import tensorflow as tf
import time

startTime = time.time()
sum = 0
for num in range(1, 10000000):
    sum += num
endTime = time.time()

print(endTime - startTime)