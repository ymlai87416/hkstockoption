from pymongo import MongoClient
from datetime import datetime, timedelta
import json
import urllib

client = MongoClient("mongodb+srv://sec_user:" + urllib.parse.quote_plus("SecUser@123.com") + "@cluster0.44cqk.mongodb.net/?retryWrites=true&w=majority")

db = client.optionSpx

def read_item(date):
    date_str = date.strftime('%Y%m%d')
    collection = db[date_str]

    for x in collection.find({}, { }):
        print(x)

def write_item(date):
    date_str = date.strftime('%Y%m%d')
    collection = db[date_str]

    #insert 4 graphs 
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'netGamma.json') as f: 
        netGamma = json.load(f)
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'callPutGamma.json') as f: 
        putCallGamma = json.load(f)
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'netDailyGamma.json') as f: 
        dailyNetGamma = json.load(f)
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'gammaExposure.json') as f: 
        gammaExposure = json.load(f)
    #Step 3: Insert business object directly into MongoDB via insert_one
    result=collection.insert_one(netGamma)
    result=collection.insert_one(putCallGamma)
    result=collection.insert_one(dailyNetGamma)
    result=collection.insert_one(gammaExposure)

def delete_item(date):
    date_str = date.strftime('%Y%m%d')
    collection = db[date_str]
    collection.drop()

if __name__ == "__main__":
    write_item(datetime.now())

    #read_item(datetime.now())

    #delete_item(datetime.now())