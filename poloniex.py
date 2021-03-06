import urllib
import urllib2
import json
import time
import hmac,hashlib
import csv
import pprint
from time import sleep
import datetime

# NOTE: This can ONLY be used for the public API currently

# See API commands below

# ** returnTicker **
# Returns the ticker for all markets.
# {"BTC_LTC":{"last":"0.0251","lowestAsk":"0.02589999","highestBid":"0.0251","percentChange":"0.02390438",
# "baseVolume":"6.16485315","quoteVolume":"245.82513926"},"BTC_NXT":{"last":"0.00005730","lowestAsk":"0.00005710",
# "highestBid":"0.00004903","percentChange":"0.16701570","baseVolume":"0.45347489","quoteVolume":"9094"}, ... }
# Call: https://poloniex.com/public?command=returnTicker

# ** return24Volume **
# Returns the 24-hour volume for all markets, plus totals for primary currencies.
# {"BTC_LTC":{"BTC":"2.23248854","LTC":"87.10381314"},"BTC_NXT":{"BTC":"0.981616","NXT":"14145"}, ... "totalBTC":"81.89657704","totalLTC":"78.52083806"}
# Call: https://poloniex.com/public?command=return24hVolume

# ** returnOrderBook **
# Returns the order book for a given market.
# {"asks":[[0.00007600,1164],[0.00007620,1300], ... "bids":[[0.00006901,200],[0.00006900,408], ... }
# http://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_MRO

# ** returnTradeHistory **
# Returns the past 200 trades for a given market.
# [{"date":"2014-02-10 04:23:23","type":"buy","rate":"0.00007600","amount":"140","total":"0.01064"},{"date":"2014-02-10 01:19:37","type":"buy","rate":"0.00007600","amount":"655","total":"0.04978"}, ... ]
# Call: https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_MRO

#define output csv file for data
#ofile = csv.writer(open('output.dat', "wb+"))
#define CSV writing rules
#writer = csv.writer(ofile,delimiter='\t')

# hard-code the currency type to MRO/BTC
currencypair = 'BTC_DRK'

# instanciate an instance of the class
# poloniex = poloniexpublicapi.poloniex()
# data = poloniex.returnOrderBook('BTC_MRO')

# run for a while
count = 0
while count < 10000:
	# ** get orderbook data by requesting the API URL **
	print "\n\n Iteration ",count
	try:
		url = urllib2.Request('http://poloniex.com/public?command=returnOrderBook&currencyPair='+currencypair)
	except:
		print("An error occurred trying to connect to the server with the following:\n")
		print("Pausing for 5 minutes")
		sleep(10)
		continue
	# Parse the API output as JSON
	try:
		parsed_data = json.load(urllib2.urlopen(url))
	except:
		print("An error occurred trying to connect to the server with the following:\n")
		print("Pausing for 5 minutes")
		sleep(10)
		continue
	
	# ** get last order data by requesting the API URL **
	try:
		url = urllib2.Request('https://poloniex.com/public?command=returnTicker')
	except:
		print("An error occurred trying to connect to the server with the following:\n")
		print("Pausing for 5 minutes")
		sleep(10)
		continue
	# Parse the API output as JSON
	try:
		parsed_data2 = json.load(urllib2.urlopen(url))
	except:
		print("An error occurred trying to connect to the server with the following:\n")
		print("Pausing for 5 minutes")
		sleep(10)
		continue
	# Get just relevant information (API outputs more than I want)
	lasttrade = parsed_data2.get(currencypair).get("last")
	
	# Open csv data files for writing
	# Format for asks.csv: currencypair, datetime, askprice, quantity
	writeask = csv.writer(open('asks.csv', 'wb'))
	# Format for bids.csv: currencypair, datetime, bidprice, quantity
	writebid = csv.writer(open('bids.csv', 'wb'))
	# Format for askavg.csv: currencypair, datetime, average ask price, average quantity, lasttrade
	writeaskavg = csv.writer(open('askavg.csv', 'ab'))
	# Format for askavg.csv: currencypair, datetime, average bid price, average quantity, lasttrade
	writebidavg = csv.writer(open('bidavg.csv', 'ab'))
	# Format for history.csv (contains last 200 trades for the currency pair): currencypair, datetime, quantity, price, totalvalue (qty*price), type(buy/sell)
	writehistory = csv.writer(open('history.csv', 'wb'))
	headers = ['value', 'amount']
	print '\n\nSaving to file... \n'
	
	# ** Initialize some values **
	value = 0
	amount = 0
	i = 0
	averages = []
	# Get time stamp for data
	ts = time.time()
	# Reformat datetime
	dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	
	# Parse asks array
	for item in parsed_data['asks']:
		row = []
		# add the currency pair type so I know what it was in the csv file
		row.append(currencypair)
		row.append(dt)
		row.append(item[0])
		value += item[0]
		row.append(item[1])
		amount += item[1]
		# This is a counter for averaging
		i += 1
		# Write values to CSV file
		writeask.writerow(row)

	# Create an array of datetime and average values
	averages.append(currencypair)
	averages.append(dt)
	averages.append(value / i)
	averages.append(amount / i)
	averages.append(lasttrade)
	# Write the averages arrary to CSV file
	writeaskavg.writerow(averages)
	
	# Re-initialize values
	value = 0
	amount = 0
	i = 0
	averages = []
	# Parse bids array
	for item in parsed_data['bids']:
		row = []
		row.append(currencypair)
		row.append(dt)
		row.append(item[0])
		value += item[0]
		row.append(item[1])
		amount += item[1]
		writebid.writerow(row)
		i += 1
	averages.append(currencypair)
	averages.append(dt)
	averages.append(value / i)
	averages.append(amount / i)
	averages.append(lasttrade)
	writebidavg.writerow(averages)
	
	# ** Get the trade history **
	try:
		url = urllib2.Request('https://poloniex.com/public?command=returnTradeHistory&currencyPair='+currencypair)
	except:
		print("An error occurred trying to connect to the server with the following:\n")
		print("Pausing for 5 minutes")
		sleep(10)
		continue
	try:
		# Parse the API output as JSON
		parsed_history = json.load(urllib2.urlopen(url))
	except:
		print("An error occurred trying to connect to the server with the following:\n")
		print("Pausing for 5 minutes")
		sleep(10)
		continue
	length = range(0,len(parsed_history))
	for x in length:
		row = []
		temp = parsed_history[x]
		# print (temp) # Only for debugging
		# Types: tradeID, amount, rate, date, total, type
		row.append(currencypair)
		row.append(temp['date'])
		# row.append(temp['tradeID']) # I don't need this
		row.append(temp['amount'])
		row.append(temp['rate'])
		row.append(temp['total'])
		row.append(temp['type'])
		# Write values to CSV file
		writehistory.writerow(row)
	
	
	# Counter for keeping track of iterations
	count += 1
	print "Iteration: ", count, "\n"
	print "Waiting 10 seconds"
	# Put a delay so I don't get banned from the API
	sleep(10)