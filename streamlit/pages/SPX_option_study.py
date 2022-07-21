import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
import urllib
import config as config
import matplotlib.pyplot as plt

st.set_page_config(page_title="SPX option study", page_icon="📈")

st.markdown("## SPX option study")
st.sidebar.markdown("SPX option study")

date = st.date_input(label="date")

# Now download 

client = MongoClient("mongodb+srv://" +  urllib.parse.quote_plus(config.MONGO_USER) 
    + ":" + urllib.parse.quote_plus(config.MONGO_PASSWORD) + "@" + config.MONGO_URL + "/?retryWrites=true&w=majority")

db = client[config.MONGO_DB_NAME]

def plot_net_gamma(data):
    st.write("Batch "  + data["batchDate"] + " SPX: Net Gamma")
    strikes= data["strikes"]
    totalGamma = data["totalGamma"]
    spotPrice = data["spotPrice"]
    fromStrike = spotPrice - 5*40
    toStrike = spotPrice + 5*40

    fig, ax = plt.subplots()
    ax.grid()
    ax.bar(strikes,totalGamma, width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure")
    ax.set_xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(sum(totalGamma))) + " Bn per 1% SPX Move"
    ax.set_title(chartTitle, fontweight="bold", fontsize=20)
    ax.set_xlabel('Strike', fontweight="bold")
    ax.set_ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    ax.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot: " + str("{:,.0f}".format(spotPrice)))
    ax.legend()
    
    st.pyplot(fig)
    
def plot_callput_gamma(data):
    st.write("Batch "  + data["batchDate"] + " SPX: Call Put Gamma")

    strikes= data["strikes"]
    callGammaEx = data["callGamma"]
    putGammaEx = data["putGamma"]
    spotPrice = data["spotPrice"]
    fromStrike = spotPrice - 5*40
    toStrike = spotPrice + 5*40

    totalGamma = sum(callGammaEx) + sum(putGammaEx)
    fig, ax = plt.subplots()
    ax.grid()
    ax.bar(strikes, callGammaEx, width=6, linewidth=0.1, edgecolor='k', label="Call Gamma")
    ax.bar(strikes, putGammaEx, width=6, linewidth=0.1, edgecolor='k', label="Put Gamma")
    ax.set_xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(totalGamma)) + " Bn per 1% SPX Move"
    ax.set_title(chartTitle, fontweight="bold", fontsize=20)
    ax.set_xlabel('Strike', fontweight="bold")
    ax.set_ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    ax.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot:" + str("{:,.0f}".format(spotPrice)))
    ax.legend()
    
    st.pyplot(fig)

def plot_daily_net_gamma(data):
    st.write("Batch "  + data["batchDate"] + " SPX: Dialy Net Gamma " + data["date"])
    
    strikes= data["strikes"]
    totalGamma = data["totalGamma"]
    spotPrice = data["spotPrice"]
    today = data["date"]
    fromStrike = spotPrice - 5*40
    toStrike = spotPrice + 5*40
    fig, ax = plt.subplots()
    ax.grid()
    ax.bar(strikes, totalGamma, width=6, linewidth=0.1, edgecolor='k', label="Gamma Exposure")
    ax.set_xlim([fromStrike, toStrike])
    chartTitle = "Total Gamma: $" + str("{:.2f}".format(sum(totalGamma))) + " Bn per 1% SPX Move " + today
    ax.set_title(chartTitle, fontweight="bold", fontsize=20)
    ax.set_xlabel('Strike', fontweight="bold")
    ax.set_ylabel('Spot Gamma Exposure ($ billions/1% move)', fontweight="bold")
    ax.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot: " + str("{:,.0f}".format(spotPrice)))
    ax.legend()

    st.pyplot(fig)

def plot_gamma_exposure(data):
    st.write("Batch "  + data["batchDate"] + " SPX: Gamma Exposure" + data["date"])

    levels= data["levels"]
    totalGamma = data["totalGamma"]
    totalGammaExNext = data["totalGammaExNext"]
    totalGammaExFri = data["totalGammaExFri"]
    spotPrice = data["spotPrice"]
    today = data["date"]
    fromStrike = spotPrice - 5*40
    toStrike = spotPrice + 5*40
    zeroGamma = data["zeroGamma"]

    fig, ax = plt.subplots()
    ax.grid()
    ax.plot(levels, totalGamma, label="All Expiries")
    ax.plot(levels, totalGammaExNext, label="Ex-Next Expiry")
    ax.plot(levels, totalGammaExFri, label="Ex-Next Monthly Expiry")
    chartTitle = "Gamma Exposure Profile, SPX, " + today
    ax.set_title(chartTitle, fontweight="bold", fontsize=20)
    ax.set_xlabel('Index Price', fontweight="bold")
    ax.set_ylabel('Gamma Exposure ($ billions/1% move)', fontweight="bold")
    ax.axvline(x=spotPrice, color='r', lw=1, label="SPX Spot: " + str("{:,.0f}".format(spotPrice)))
    ax.axvline(x=zeroGamma, color='g', lw=1, label="Gamma Flip: " + str("{:,.0f}".format(zeroGamma)))
    ax.axhline(y=0, color='grey', lw=1)
    ax.set_xlim([fromStrike, toStrike])
    trans = ax.get_xaxis_transform()
    ax.fill_between([fromStrike, zeroGamma], min(totalGamma), max(totalGamma), facecolor='red', alpha=0.1, transform=trans)
    ax.fill_between([zeroGamma, toStrike], min(totalGamma), max(totalGamma), facecolor='green', alpha=0.1, transform=trans)
    ax.legend()
    
    st.pyplot(fig)


def read_item(date):
    date_str = date.strftime('%Y%m%d')
    collection = db[date_str]
    limit = 2
    cnt = [limit, limit, limit, limit]

    for x in collection.find({}, { }).sort([('type', 1), ('batchDate', -1)]):
        graph_type = x["type"]
        if graph_type == "net gamma" and cnt[0] > 0:
            plot_net_gamma(x)
            cnt[0] -=1
        elif graph_type == "call put gamma" and cnt[1] > 0:
            plot_callput_gamma(x)
            cnt[1] -=1
        elif graph_type == "net gamma daily" and cnt[2] > 0:
            plot_daily_net_gamma(x)
            cnt[2] -=1
        elif graph_type == "gamma exposure" and cnt[3] > 0:
            plot_gamma_exposure(x)
            cnt[3] -=1

read_item(date)