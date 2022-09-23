import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
import urllib
import config as config
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates

client = MongoClient("mongodb+srv://" +  urllib.parse.quote_plus(config.MONGO_USER) 
    + ":" + urllib.parse.quote_plus(config.MONGO_PASSWORD) + "@" + config.MONGO_URL + "/?retryWrites=true&w=majority")
db = client[config.MONGO_ADAM_DB_NAME]


def process_data(data):
    result = []

    for c in data:
        cdict = {
            "name": c["name"],
            "price": pd.DataFrame.from_dict(c["price"]),
            "predict": pd.DataFrame.from_dict(c["predict"])
        }

        result.append(cdict)

    return result

def process_data_2(data) :
    result = []

    for s in data:
        _dict = {}
        _dict["sector"] = s["sector"]
        _dict["data"] = process_data(s["data"])
        result.append(_dict)
        
    return result


def read_info(date):
    date_str = date.strftime('%Y%m%d')
    collection = db["adam"]

    #data = collection.find_one("batch_date", date_str)
    for data in collection.find({"batch_date": date_str}):

        # convert back to pre-pandas
        result = {}
        result["crypto"] = process_data(data["crypto"])
        result["commodity"] = process_data(data["commodity"])
        result["currency"] = process_data(data["currency"])
        result["stock"] = process_data_2(data["stock"])

    return result

def plot_graph(data, predict):
    # Creating Subplots
    fig, ax = plt.subplots()
    ohlc = data.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
    
    #ohlc['Date'] = pd.to_datetime(ohlc.index)
    ohlc['Date'] = ohlc['Date'].apply(mpl_dates.date2num)
    ohlc = ohlc.astype(float)
    ohlc2 = predict.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
    
    #ohlc2['Date'] = pd.to_datetime(ohlc2.index)
    ohlc2['Date'] = ohlc2['Date'].apply(mpl_dates.date2num)
    ohlc2 = ohlc2.astype(float)

    #print("XXXX")
    #print(ohlc)

    candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=1)
    candlestick_ohlc(ax, ohlc2.values, width=0.6, colorup='lightgreen', colordown='lightcoral', alpha=0.5)

    # Setting labels & titles
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    #fig.suptitle('Apple adam')

    # Formatting Date
    date_format = mpl_dates.DateFormatter('%d-%m-%Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    fig.tight_layout()

    st.pyplot(fig)

st.set_page_config(page_title="Adam", page_icon="📈")

date = st.date_input(label="date")


st.markdown("## Adam !!! VISUALIZE !!!" )

data = read_info(date)

st.markdown("""
    ### Currency:
    
    Refer this page for the most trade foreign currency pair

    """)

for obj in data["currency"]:
    st.markdown("#### " + obj["name"])

    plot_graph(obj["price"], obj["predict"])


st.markdown("""
    ### Commodity:
    
    Refer this page for the most traded commodity

    """)

for obj in data["commodity"]:
    st.markdown("#### " + obj["name"])

    plot_graph(obj["price"], obj["predict"])

st.markdown("""
### Stock:

Stock, only selected industry with top 5 and have at most 3 in each industry

""")

for obj in data["stock"]:
    for obj2 in obj["data"]:
        st.markdown("#### " + obj["sector"] + " - " + obj2["name"])
        plot_graph(obj2["price"], obj2["predict"])

st.markdown("""
### Crypto:

Refer this page for the most trade foreign currency pair

""")

for obj in data["crypto"]:
    st.markdown("#### " + obj["name"])

    plot_graph(obj["price"], obj["predict"])

