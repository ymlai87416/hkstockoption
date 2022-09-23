from pymongo import MongoClient
import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr
import numpy as np
import scipy
from scipy.stats import norm
from datetime import datetime, timedelta, date
import json
import requests
import urllib
pd.options.display.float_format = '{:,.4f}'.format
import config
import sys
import pytz

mongodbAdamUrl = "mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority".\
    format(urllib.parse.quote_plus(config.MONGO_USER), urllib.parse.quote_plus(config.MONGO_PASSWORD), config.MONGO_URL)

mongodConfigbUrl = "mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority".\
    format(urllib.parse.quote_plus(config.MONGO_USER), urllib.parse.quote_plus(config.MONGO_PASSWORD), config.MONGO_URL)

history_date_range = 60
forward_date_range = 20  #around 1 month

# This is the template of the config
# crypto: none
# commodity: crude oil, soybean, gold, wheat from https://finance.yahoo.com/commodities/
# currency: jpy, gbp, chf, cad, aud https://www.investopedia.com/ask/answers/06/maincurrencypairs.asp
# stock: https://finviz.com/map.ashx?t=sec_all
# default config (all symbol data are fetch from yahoo for simplication)
default_config = \
"""{
    "name": "adam_config",
    "crypto": ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD"],
    "commodity": ["CL=F", "ZS=F", "GC=F", "ZC=F"],
    "stock": {
        "technology": ["MSFT", "AAPL", "GOOG"],
        "consumer": ["AMZN", "TSLA", "PG", "WMT"],
        "finance": ["JPM", "V", "BAC"],
        "biotech": ["JNJ", "PFE", "UNH"],
        "industry": ["LMT", "UPS", "GE"]
    },
    "currency": ["JPY=X", "GBP=X", "CHF=X",  "CAD=X", "AUD=X"]
}"""

def reverse_adam(data, day_reverse):
    # pandas timeseries
    # now we find the central point of the bar and reverse all the bar
    #print(data)

    predict = pd.DataFrame(columns=['Date','High','Low','Open','Close'])
    last_date = data.tail(1).index.item()
    mid = ( data.loc[last_date, 'High'] + data.loc[last_date, 'Low'] ) / 2
    records = []
    for date in reversed(data.index):
        dict = {}
        if day_reverse < 0:
            break
        
        dict["Date"] = last_date
        dict["Low"] = mid - (data.loc[date, 'High'] - mid)
        dict["High"] = mid - (data.loc[date, 'Low'] - mid )
        dict["Open"] = mid - (data.loc[date, 'Open'] - mid)
        dict["Close"] = mid - (data.loc[date, 'Close'] - mid)
        
        if last_date != date:
            records.append(dict)

        last_date = last_date + timedelta(days=1)
        day_reverse -=1

    predict = pd.DataFrame.from_records(records)
    predict.set_index('Date', inplace=True)
    
    return predict

def get_data(symbol, start_date, end_date):
    # get data from yahoo
    yf.pdr_override() 

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    data = pdr.get_data_yahoo(symbol, start=start_date_str, end=end_date_str)
    return data

def process_list(batch_date, asset_list):
    
    start_date = batch_date  + timedelta(days=-history_date_range)
    end_date = batch_date

    result = []
    for c in asset_list:
        #print("DD " + c )

        record = {}
        price = get_data(c, start_date, end_date)
        predict = reverse_adam(price, forward_date_range)

        ## remove the key
        price["Date"] = price.index
        predict["Date"] = predict.index
        price = price.reset_index(drop=True)
        predict = predict.reset_index(drop=True)

        record["name"] = c
        record["price"] = price.to_dict('record')  # record means export format
        record["predict"] = predict.to_dict('record')

        result.append(record)

    return result

def process_list_2(batch_date, sector):

    result = []
    for k in sector.keys():
        record = process_list(batch_date, sector[k])
        result.append( {"sector": k, "data": record} )

    return result

def read_config():
    config = {}
    client = None
    try:
        client = MongoClient(mongodbAdamUrl)
        db = client[config.MONGO_CONFIG_DB_NAME]
        collection = db["config"]

        config = collection.find_one("name", "adam_config")
        client.close()
    except Exception as e:
        print(e)
        config = json.loads(default_config)
    finally:
        if client is not None:
            client.close()

    return config

# save to mongo db format
#  {
#       crypto: {...},
#       commodity: {...},
#  }
def save_mongo(data):
    client = MongoClient(mongodbAdamUrl)

    db = client[config.MONGO_ADAM_DB_NAME]
    #date_str = batchDate.strftime('%Y%m%d')
    collection = db["adam"]

    # ok if failed to delete
    try:
        collection.delete_many({"batch_date": data["batch_date"]})
    except: 
        print("There is no record in collection")

    result=collection.insert_one(data)
    client.close()

def main(batch_date):
    batch_date = datetime.strptime(batch_date, '%Y%m%dT%H%M%S')
    result = {}

    config = read_config()

    result["crypto"] = process_list(batch_date, config["crypto"])
    result["commodity"] = process_list(batch_date, config["commodity"])
    result["currency"] = process_list(batch_date, config["currency"])
    result["stock"] = process_list_2(batch_date, config["stock"])
    result["batch_date"] = batch_date.strftime("%Y%m%d") # US new york time

    save_mongo(result)


if __name__ == "__main__":
    batch_date = sys.argv[1]
    
    main(batch_date)