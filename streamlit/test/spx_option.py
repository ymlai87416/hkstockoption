import pandas as pd
import numpy as np
import scipy
from scipy.stats import norm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import json
import requests
import pytz
pd.options.display.float_format = '{:,.4f}'.format

# Inputs and Parameters
filename = "/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'spx_quotedata.csv'
jsonUrl = "https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json"

def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")

    return dt

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
    lastTradeDate = datetime.strptime(data["data"]["last_trade_time"],'%Y-%m-%dT%H:%M:%S')
    if todayDate > lastTradeDate:
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

def showNetGammaExposure(strikes, dfAgg, spotPrice, fromStrike, toStrike):
    # Chart 1: Absolute Gamma Exposure
    plt.grid()
    plt.bar(strikes, dfAgg['TotalGamma'].to_numpy(), width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure")
    plt.xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(dfAgg['TotalGamma'].sum())) + " Bn per 1% SPX Move"
    plt.title(chartTitle, fontweight="bold", fontsize=20)
    plt.xlabel('Strike', fontweight="bold")
    plt.ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    plt.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot: " + str("{:,.0f}".format(spotPrice)))
    plt.legend()
    plt.show()

def showCallPutGammaExposure(strikes, dfAgg, spotPrice, fromStrike, toStrike):
    # Chart 2: Absolute Gamma Exposure by Calls and Puts
    plt.grid()
    plt.bar(strikes, dfAgg['CallGEX'].to_numpy() / 10**9, width=6, linewidth=0.1, edgecolor='k', label="Call Gamma")
    plt.bar(strikes, dfAgg['PutGEX'].to_numpy() / 10**9, width=6, linewidth=0.1, edgecolor='k', label="Put Gamma")
    plt.xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(dfAgg['TotalGamma'].sum())) + " Bn per 1% SPX Move"
    plt.title(chartTitle, fontweight="bold", fontsize=20)
    plt.xlabel('Strike', fontweight="bold")
    plt.ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    plt.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot:" + str("{:,.0f}".format(spotPrice)))
    plt.legend()
    plt.show()

def showDailyNetGammaExposure(todayDate, strikes, dfAggToday, spotPrice, fromStrike, toStrike):
    plt.grid()
    plt.bar(strikes, dfAggToday['TotalGamma'].to_numpy(), width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure")
    plt.xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(dfAggToday['TotalGamma'].sum())) + " Bn per 1% SPX Move" + todayDate.strftime('%d %b %Y')
    plt.title(chartTitle, fontweight="bold", fontsize=20)
    plt.xlabel('Strike', fontweight="bold")
    plt.ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    plt.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot: " + str("{:,.0f}".format(spotPrice)))
    plt.legend()
    plt.show()

def showGammaExposureProfile(todayDate, spotPrice, zeroGamma, fromStrike, toStrike, levels, totalGamma, totalGammaExNext, totalGammaExFri):
    # Chart 3: Gamma Exposure Profile
    fig, ax = plt.subplots()
    plt.grid()
    plt.plot(levels, totalGamma, label="All Expiries")
    plt.plot(levels, totalGammaExNext, label="Ex-Next Expiry")
    plt.plot(levels, totalGammaExFri, label="Ex-Next Monthly Expiry")
    chartTitle = "Gamma Exposure Profile, SPX, " + todayDate.strftime('%d %b %Y')
    plt.title(chartTitle, fontweight="bold", fontsize=20)
    plt.xlabel('Index Price', fontweight="bold")
    plt.ylabel('Gamma Exposure ($ billions/1% move)', fontweight="bold")
    plt.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot: " + str("{:,.0f}".format(spotPrice)))
    plt.axvline(x=zeroGamma, color='g', lw=1, label="Gamma Flip: " + str("{:,.0f}".format(zeroGamma)))
    plt.axhline(y=0, color='grey', lw=1)
    plt.xlim([fromStrike, toStrike])
    trans = ax.get_xaxis_transform()
    plt.fill_between([fromStrike, zeroGamma], min(totalGamma), max(totalGamma), facecolor='red', alpha=0.1, transform=trans)
    plt.fill_between([zeroGamma, toStrike], min(totalGamma), max(totalGamma), facecolor='green', alpha=0.1, transform=trans)
    plt.legend()
    plt.show()

def writeToFile(fp, content):
    f = open(fp, "w", encoding='UTF-8')
    f.write(content)
    f.close()

def exportNetGammaExposureInfo(spotPrice, strikes, totalGamma):
    result = dict()
    result["type"] = "net gamma"
    result["batchDate"] = datetime.now().strftime('%Y%m%d %H%M')
    result["spotPrice"] = spotPrice
    result["strikes"] = strikes.tolist()
    result["totalGamma"] = totalGamma.tolist()
    json_object = json.dumps(result, indent = 2) 
    #print(json_object)
    fp = "/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'netGamma.json'
    writeToFile(fp, json_object)

def exportDailyNetGammaExposureInfo(date, spotPrice, strikes, totalGamma):
    result = dict()
    result["type"] = "net gamma daily"
    result["batchDate"] = datetime.now().strftime('%Y%m%d %H%M')
    result["date"] = date.strftime('%Y%m%d')
    result["spotPrice"] = spotPrice
    result["strikes"] = strikes.tolist()
    result["totalGamma"] = totalGamma.tolist()
    json_object = json.dumps(result, indent = 2) 
    #print(json_object)
    fp = "/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'netDailyGamma.json'
    writeToFile(fp, json_object)

def exporCallPutGammaExposureInfo(spotPrice, strikes, callGamma, putGamma):
    result = dict()
    result["type"] = "call put gamma"
    result["batchDate"] = datetime.now().strftime('%Y%m%d %H%M')
    result["spotPrice"] = spotPrice
    result["strikes"] = strikes.tolist()
    result["callGamma"] = callGamma.tolist()
    result["putGamma"] = putGamma.tolist()
    json_object = json.dumps(result, indent = 2) 
    #print(json_object)
    fp = "/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'callPutGamma.json'
    writeToFile(fp, json_object)

def exporGammaExposureProfileInfo(todayDate, spotPrice, zeroGamma, levels, 
    totalGamma, totalGammaExNext, totalGammaExFri):
    result = dict()
    result["type"] = "gamma exposure"
    result["batchDate"] = datetime.now().strftime('%Y%m%d %H%M')
    result["date"] = todayDate.strftime('%Y%m%d')
    result["spotPrice"] = spotPrice
    result["zeroGamma"] = zeroGamma
    result["levels"] = levels.tolist()
    result["totalGamma"] = totalGamma.tolist()
    result["totalGammaExNext"] = totalGammaExNext.tolist()
    result["totalGammaExFri"] = totalGammaExFri.tolist()
    json_object = json.dumps(result, indent = 2) 
    #print(json_object)
    fp = "/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'gammaExposure.json'
    writeToFile(fp, json_object)

def run():
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

    exportNetGammaExposureInfo(spotPrice, strikes, dfAgg['TotalGamma'].to_numpy())
    showNetGammaExposure(strikes, dfAgg, spotPrice, fromStrike, toStrike)
    exporCallPutGammaExposureInfo(spotPrice, strikes, dfAgg['CallGEX'].to_numpy() / 10**9, dfAgg['PutGEX'].to_numpy() / 10**9)
    showCallPutGammaExposure(strikes, dfAgg, spotPrice, fromStrike, toStrike)

    # Chart 1.5: Absolute Gamma Exposure
    dfAggToday = df[df.today].groupby(['StrikePrice']).sum()
    strikes = dfAggToday.index.values
    exportDailyNetGammaExposureInfo(todayDate, spotPrice, strikes, dfAggToday['TotalGamma'].to_numpy() )
    showDailyNetGammaExposure(todayDate, strikes, dfAggToday, spotPrice, fromStrike, toStrike)


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

    exporGammaExposureProfileInfo(todayDate, spotPrice, zeroGamma, levels, totalGamma, totalGammaExNext, totalGammaExFri)
    showGammaExposureProfile(todayDate, spotPrice, zeroGamma, fromStrike, toStrike, levels, totalGamma, totalGammaExNext, totalGammaExFri)

if __name__ == "__main__":
    run()