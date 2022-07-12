# Please run this job in EST timezone (New York)

from pymongo import MongoClient
import pandas as pd
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

# Inputs and Parameters
jsonUrl = "https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json"
mongodbUrl = "mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority".\
    format(urllib.parse.quote_plus(config.MONGO_USER), urllib.parse.quote_plus(config.MONGO_PASSWORD), config.MONGO_URL)

# Black-Scholes European-Options Gamma
def calcGammaEx(S, K, vol, T, r, q, optType, OI):
    if T == 0 or vol == 0:
        return 0

    dp = (np.log(S/K) + (r - q + 0.5*vol**2)*T) / (vol*np.sqrt(T))
    dm = dp - vol*np.sqrt(T) 

    if optType == 'call':
        gamma = np.exp(-q*T) * norm.pdf(dp) / (S * vol * np.sqrt(T))
        return OI * 100 * S * S * 0.01 * gamma 
    else: # Gamma is same for calls and puts. This is just to cross-check
        gamma = K * np.exp(-r*T) * norm.pdf(dm) / (S * S * vol * np.sqrt(T))
        return OI * 100 * S * S * 0.01 * gamma 

def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)

    return dt

def isThirdFriday(d):
    return d.weekday() == 4 and 15 <= d.day <= 21

def readCSVFile(filename):
    # This assumes the CBOE file format hasn't been edited, i.e. table beginds at line 4
    optionsFile = open(filename)
    optionsFileData = optionsFile.readlines()
    optionsFile.close()

    # Get SPX Spot
    spotLine = optionsFileData[1]
    spotPrice = float(spotLine.split('Last:')[1].split(',')[0])
    #fromStrike = 0.8 * spotPrice
    #toStrike = 1.2 * spotPrice
    fromStrike = spotPrice - 5 * 40
    toStrike = spotPrice + 5 * 40

    # The date format is suppoe to be July 10, 2022
    dateLine = optionsFileData[2]
    todayDate = dateLine.split('Date: ')[1].split(',')
    monthDay = todayDate[0].split(' ')

    print("DD" + str(todayDate))
    # Handling of US/EU date formats
    if len(monthDay) == 2:
        year = int(todayDate[1])
        month = monthDay[0]
        day = int(monthDay[1])
    else:
        year = int(monthDay[2])
        month = monthDay[1]
        day = int(monthDay[0])

    todayDate = datetime.strptime(month,'%B')
    todayDate = todayDate.replace(day=day, year=year)

    # Get SPX Options Data
    df = pd.read_csv(filename, sep=",", header=None, skiprows=4)
    df.columns = ['ExpirationDate','Calls','CallLastSale','CallNet','CallBid','CallAsk','CallVol',
                'CallIV','CallDelta','CallGamma','CallOpenInt','StrikePrice','Puts','PutLastSale',
                'PutNet','PutBid','PutAsk','PutVol','PutIV','PutDelta','PutGamma','PutOpenInt']

    df['ExpirationDate'] = pd.to_datetime(df['ExpirationDate'], format='%a %b %d %Y')
    df['ExpirationDate'] = df['ExpirationDate'] + timedelta(hours=16)
    df['StrikePrice'] = df['StrikePrice'].astype(float)
    df['CallIV'] = df['CallIV'].astype(float)
    df['PutIV'] = df['PutIV'].astype(float)
    df['CallGamma'] = df['CallGamma'].astype(float)
    df['PutGamma'] = df['PutGamma'].astype(float)
    df['CallOpenInt'] = df['CallOpenInt'].astype(float)
    df['PutOpenInt'] = df['PutOpenInt'].astype(float)
    df['today'] = [True if (np.busday_count(todayDate.date(), x.date())) == 0 \
                            else False for x in df.ExpirationDate]

    todayDate = todayDate.date()

    return todayDate, spotPrice, fromStrike, toStrike, df

def getExpirationDate(name):
    if name.startswith("SPXW"):
        dateStr = name[4:10]
    else:
        dateStr = name[3:9]
    return datetime.strptime(dateStr,'%y%m%d')

def getStrikePrice(name):
    if name.startswith("SPXW"):
        int_part = float(name[11:16])
        dec_part = float(name[16:19])
    else:
        int_part = float(name[10:15])
        dec_part = float(name[15:18])

    return int_part + dec_part /1000.0

def sameCategory(callName, putName):
    l = len(callName)
    if len(putName) != l:
        return False
    typeLoc = 10 if callName.startswith("SPXW") else 9
    for i in range(0, l):
        if callName[i] != putName[i] and i != typeLoc:
            return False

    return True

def readJson():
    # only consider option range today -> one month after today
    #f = open('./_SPX.json')
    #data = json.load(f)
    resp = requests.get(url=jsonUrl)
    data = resp.json()  
    
    spotPrice = float(data["data"]["current_price"])
    todayDate = datetime.strptime(data["timestamp"],'%Y-%m-%d %H:%M:%S')

    todayDate = convert_datetime_timezone(todayDate, 'UTC', 'America/New_York')

    lastTradeDate = datetime.strptime(data["data"]["last_trade_time"],'%Y-%m-%dT%H:%M:%S')
    est = pytz.timezone('America/New_York')
    lastTradeDate = est.localize(lastTradeDate)
    lastTradeDateTimeEnd = lastTradeDate.replace(hour=0, minute=0, second=0, microsecond=0)+ timedelta(hours=17)
    if todayDate >= lastTradeDateTimeEnd:
        todayDate = lastTradeDate + timedelta(days=1)
    todayDate = todayDate.date()
    # Flatten data
    df_option = pd.json_normalize(data, record_path =['data', 'options'])
    
    fromStrike = spotPrice - 5 * 40
    toStrike = spotPrice + 5 * 40

    columns = ['ExpirationDate','Calls','CallLastSale','CallNet','CallBid','CallAsk','CallVol',
                'CallIV','CallDelta','CallGamma','CallOpenInt','StrikePrice','Puts','PutLastSale',
                'PutNet','PutBid','PutAsk','PutVol','PutIV','PutDelta','PutGamma','PutOpenInt']
    
    data = []
    curRow = None
    callName = None
    for index, row in df_option.iterrows():
        if curRow is None:
            expDate = getExpirationDate(row["option"])
            strike = getStrikePrice(row["option"])
            curRow = [expDate, row["option"], row["last_trade_price"], row["change"], row["bid"],
                    row["ask"], row["volume"], row["iv"], row["delta"], row["gamma"], row["open_interest"],
                    strike]
            callName = row["option"]
        else:
            putName = row["option"]
            if not sameCategory(callName, putName):
                print("Shit" + " " + callName + " " + row["option"])

            putData = [row["option"], row["last_trade_price"], row["change"], row["bid"],
                    row["ask"], row["volume"], row["iv"], row["delta"], row["gamma"], row["open_interest"]]
            curRow = curRow + putData
            data.append(curRow)
            curRow = None
    df = pd.DataFrame(data, columns=columns)

    df['today'] = [True if (np.busday_count(todayDate, x.date())) == 0 \
                            else False for x in df.ExpirationDate]

    return todayDate, spotPrice, fromStrike, toStrike, df

def writeToFile(fp, content):
    f = open(fp, "w", encoding='UTF-8')
    f.write(content)
    f.close()

def saveJsonToMongo(batchDate, data):
    client = MongoClient(mongodbUrl)
    db = client[config.MONGO_DB_NAME]
    date_str = batchDate.strftime('%Y%m%d')
    collection = db[date_str]
    result=collection.insert_one(data)

    client.close()

def exportNetGammaExposureInfo(batch_date, date, spotPrice, strikes, totalGamma):
    result = dict()
    result["type"] = "net gamma"
    result["batchDate"] = batch_date.strftime('%Y%m%d %H%M')
    result["spotPrice"] = spotPrice
    result["strikes"] = strikes.tolist()
    result["totalGamma"] = totalGamma.tolist()
    json_object = json.dumps(result, indent = 2) 
    #print(json_object)
    saveJsonToMongo(date, result)

def exportDailyNetGammaExposureInfo(batch_date, date, spotPrice, strikes, totalGamma):
    result = dict()
    result["type"] = "net gamma daily"
    result["batchDate"] = batch_date.strftime('%Y%m%d %H%M')
    result["date"] = date.strftime('%Y%m%d')
    result["spotPrice"] = spotPrice
    result["strikes"] = strikes.tolist()
    result["totalGamma"] = totalGamma.tolist()

    saveJsonToMongo(date, result)

def exporCallPutGammaExposureInfo(batch_date, date, spotPrice, strikes, callGamma, putGamma):
    result = dict()
    result["type"] = "call put gamma"
    result["batchDate"] = batch_date.strftime('%Y%m%d %H%M')
    result["spotPrice"] = spotPrice
    result["strikes"] = strikes.tolist()
    result["callGamma"] = callGamma.tolist()
    result["putGamma"] = putGamma.tolist()
    saveJsonToMongo(date, result)

def exporGammaExposureProfileInfo(batch_date, todayDate, spotPrice, zeroGamma, levels, 
    totalGamma, totalGammaExNext, totalGammaExFri):
    result = dict()
    result["type"] = "gamma exposure"
    result["batchDate"] = batch_date.strftime('%Y%m%d %H%M')
    result["date"] = todayDate.strftime('%Y%m%d')
    result["spotPrice"] = spotPrice
    result["zeroGamma"] = zeroGamma
    result["levels"] = levels.tolist()
    result["totalGamma"] = totalGamma.tolist()
    result["totalGammaExNext"] = totalGammaExNext.tolist()
    result["totalGammaExFri"] = totalGammaExFri.tolist()

    saveJsonToMongo(todayDate, result)

def run(batch_date):
    batch_date = datetime.strptime(batch_date, '%Y%m%dT%H%M%S')

    todayDate, spotPrice, fromStrike, toStrike, df = readJson()

    # filter to only include date
    df['withinRange'] = [True if (np.busday_count(todayDate, x.date()) >= 0 and  np.busday_count(todayDate, x.date()) <= 20)\
                                else False for x in df.ExpirationDate]

    df = df[df.withinRange]

    #df.to_csv("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/data/" + "gammaJ.csv")

    # ---=== CALCULATE SPOT GAMMA ===---
    # Gamma Exposure = Unit Gamma * Open Interest * Contract Size * Spot Price 
    # To further convert into 'per 1% move' quantity, multiply by 1% of spotPrice
    df['CallGEX'] = df['CallGamma'] * df['CallOpenInt'] * 100 * spotPrice * spotPrice * 0.01
    df['PutGEX'] = df['PutGamma'] * df['PutOpenInt'] * 100 * spotPrice * spotPrice * 0.01 * -1

    df['TotalGamma'] = (df.CallGEX + df.PutGEX) / 10**9
    dfAgg = df.groupby(['StrikePrice']).sum()
    strikes = dfAgg.index.values

    exportNetGammaExposureInfo(batch_date, todayDate, spotPrice, strikes, dfAgg['TotalGamma'].to_numpy())
    exporCallPutGammaExposureInfo(batch_date, todayDate, spotPrice, strikes, dfAgg['CallGEX'].to_numpy() / 10**9, dfAgg['PutGEX'].to_numpy() / 10**9)

    # Chart 1.5: Absolute Gamma Exposure
    dfAggToday = df[df.today].groupby(['StrikePrice']).sum()
    strikes = dfAggToday.index.values
    exportDailyNetGammaExposureInfo(batch_date, todayDate, spotPrice, strikes, dfAggToday['TotalGamma'].to_numpy() )

    # ---=== CALCULATE GAMMA PROFILE ===---
    levels = np.linspace(fromStrike, toStrike, 60)  #origin 60
    #levels = np.range(fromStrike, toStrike)

    # For 0DTE options, I'm setting DTE = 1 day, otherwise they get excluded
    df['daysTillExp'] = [1/262 if (np.busday_count(todayDate, x.date())) == 0 \
                            else np.busday_count(todayDate, x.date())/262 for x in df.ExpirationDate]

    nextExpiry = df['ExpirationDate'].min()

    df['IsThirdFriday'] = [isThirdFriday(x) for x in df.ExpirationDate]
    thirdFridays = df.loc[df['IsThirdFriday'] == True]
    nextMonthlyExp = thirdFridays['ExpirationDate'].min()

    totalGamma = []
    totalGammaExNext = []
    totalGammaExFri = []

    # For each spot level, calc gamma exposure at that point
    for level in levels:
        df['callGammaEx'] = df.apply(lambda row : calcGammaEx(level, row['StrikePrice'], row['CallIV'], 
                                                            row['daysTillExp'], 0, 0, "call", row['CallOpenInt']), axis = 1)

        df['putGammaEx'] = df.apply(lambda row : calcGammaEx(level, row['StrikePrice'], row['PutIV'], 
                                                            row['daysTillExp'], 0, 0, "put", row['PutOpenInt']), axis = 1)    

        totalGamma.append(df['callGammaEx'].sum() - df['putGammaEx'].sum())

        exNxt = df.loc[df['ExpirationDate'] != nextExpiry]
        totalGammaExNext.append(exNxt['callGammaEx'].sum() - exNxt['putGammaEx'].sum())

        exFri = df.loc[df['ExpirationDate'] != nextMonthlyExp]
        totalGammaExFri.append(exFri['callGammaEx'].sum() - exFri['putGammaEx'].sum())

    totalGamma = np.array(totalGamma) / 10**9
    totalGammaExNext = np.array(totalGammaExNext) / 10**9
    totalGammaExFri = np.array(totalGammaExFri) / 10**9

    # Find Gamma Flip Point
    zeroCrossIdx = np.where(np.diff(np.sign(totalGamma)))[0]

    negGamma = totalGamma[zeroCrossIdx]
    posGamma = totalGamma[zeroCrossIdx+1]
    negStrike = levels[zeroCrossIdx]
    posStrike = levels[zeroCrossIdx+1]

    # Writing and sharing this code is only possible with your support! 
    # If you find it useful, consider supporting us at perfiliev.com/support :)
    zeroGamma = posStrike - ((posStrike - negStrike) * posGamma/(posGamma-negGamma))
    try:
        zeroGamma = zeroGamma[0]
    except:
        zeroGamma = fromStrike

    exporGammaExposureProfileInfo(batch_date, todayDate, spotPrice, zeroGamma, levels, totalGamma, totalGammaExNext, totalGammaExFri)
    
if __name__ == "__main__":
    batch_date = sys.argv[1]
    
    run(batch_date)