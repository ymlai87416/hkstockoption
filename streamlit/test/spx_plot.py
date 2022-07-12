import pandas as pd
import numpy as np
import scipy
from scipy.stats import norm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import json
import requests
pd.options.display.float_format = '{:,.4f}'.format

def showNetGammaExposure(strikes, totalGamma, spotPrice, fromStrike, toStrike):
    # Chart 1: Absolute Gamma Exposure
    plt.grid()
    plt.bar(strikes,totalGamma, width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure")
    plt.xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(sum(totalGamma))) + " Bn per 1% SPX Move"
    plt.title(chartTitle, fontweight="bold", fontsize=20)
    plt.xlabel('Strike', fontweight="bold")
    plt.ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    plt.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot: " + str("{:,.0f}".format(spotPrice)))
    plt.legend()
    plt.show()

def showCallPutGammaExposure(strikes, callGammaEx, putGammaEx, spotPrice, fromStrike, toStrike):
    # Chart 2: Absolute Gamma Exposure by Calls and Puts
    totalGamma = sum(callGammaEx) - sum(putGammaEx)
    plt.grid()
    plt.bar(strikes, callGammaEx, width=6, linewidth=0.1, edgecolor='k', label="Call Gamma")
    plt.bar(strikes, putGammaEx, width=6, linewidth=0.1, edgecolor='k', label="Put Gamma")
    plt.xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(totalGamma)) + " Bn per 1% SPX Move"
    plt.title(chartTitle, fontweight="bold", fontsize=20)
    plt.xlabel('Strike', fontweight="bold")
    plt.ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    plt.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot:" + str("{:,.0f}".format(spotPrice)))
    plt.legend()
    plt.show()

def showDailyNetGammaExposure(todayDate, strikes, totalGamma, spotPrice, fromStrike, toStrike):

    plt.grid()
    plt.bar(strikes, totalGamma, width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure")
    plt.xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(sum(totalGamma))) + " Bn per 1% SPX Move" + todayDate.strftime('%d %b %Y')
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


def run():
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'netGamma.json') as f: 
        netGamma = json.load(f)
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'callPutGamma.json') as f: 
        putCallGamma = json.load(f)
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'netDailyGamma.json') as f: 
        dailyNetGamma = json.load(f)
    with open("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/" + 'gammaExposure.json') as f: 
        gammaExposure = json.load(f)

    spotPrice = netGamma["spotPrice"]
    fromStrike = spotPrice - 5 * 40
    toStrike = spotPrice + 5 * 40
    showNetGammaExposure(netGamma["strikes"] , netGamma["totalGamma"], spotPrice, fromStrike, toStrike)

    spotPrice = putCallGamma["spotPrice"]
    fromStrike = spotPrice - 5 * 40
    toStrike = spotPrice + 5 * 40
    showCallPutGammaExposure(putCallGamma["strikes"] , putCallGamma["callGamma"] , putCallGamma["putGamma"], 
        spotPrice, fromStrike, toStrike)

    spotPrice = dailyNetGamma["spotPrice"]
    fromStrike = spotPrice - 5 * 40
    toStrike = spotPrice + 5 * 40
    date = datetime.strptime(dailyNetGamma["date"],'%Y%m%d') 
    showDailyNetGammaExposure(date, dailyNetGamma["strikes"], dailyNetGamma["totalGamma"], 
        spotPrice, fromStrike, toStrike)

    spotPrice = dailyNetGamma["spotPrice"]
    fromStrike = spotPrice - 5 * 40
    toStrike = spotPrice + 5 * 40
    date = datetime.strptime(gammaExposure["date"],'%Y%m%d') 
    showGammaExposureProfile(date, spotPrice, gammaExposure["zeroGamma"], 
        fromStrike, toStrike, gammaExposure["levels"], gammaExposure["totalGamma"], 
        gammaExposure["totalGammaExNext"], gammaExposure["totalGammaExFri"])

if __name__ == "__main__":
    run()