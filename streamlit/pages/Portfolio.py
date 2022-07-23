# streamlit login page tutorial at
# https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso

import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta
import urllib
import config as config
import matplotlib.pyplot as plt
import pandas as pd

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

def __generate_pie_chart(df):
    '''
    generate a string on the graph:
    https://stackoverflow.com/questions/5453375/matplotlib-svg-as-string-and-not-a-file
    '''
    fig, axs = plt.subplots() 
    plot = df.plot.pie(y='Weighting', ax=axs, autopct='%1.1f%%')
    axs.get_legend().remove()
    st.pyplot(fig)

def __generate_crypto_pie(portfolio):

    # create a new df 
    df = pd.DataFrame(columns = [
        "Symbol", "Weighting"
    ])

    for index, row in portfolio.iterrows():
        symbol = row["Symbol"]
        weight = row["Total USD"]
        df = df.append({"Symbol": symbol, "Weighting": weight}, ignore_index=True)

    df.set_index('Symbol', inplace=True)
    
    return __generate_pie_chart(df)

def __generate_stock_us_pie(portfolio):
    '''
    generate a string on the graph:
    https://stackoverflow.com/questions/5453375/matplotlib-svg-as-string-and-not-a-file
    '''
    # create a new df 
    df = pd.DataFrame(columns = [
        "Symbol", "Weighting"
    ])

    for index, row in portfolio.iterrows():
        symbol = row["Symbol"]
        weight = row["Total USD"]
        df = df.append({"Symbol": symbol, "Weighting": weight}, ignore_index=True)

    df.set_index('Symbol', inplace=True)

    return __generate_pie_chart(df)

def __generate_stock_hk_pie(portfolio):
    '''
    generate a string on the graph:
    https://stackoverflow.com/questions/5453375/matplotlib-svg-as-string-and-not-a-file
    '''
    # create a new df 
    df = pd.DataFrame(columns = [
        "Symbol", "Weighting"
    ])

    for index, row in portfolio.iterrows():
        symbol = row["Symbol"]
        weight = row["Total HKD"]
        df = df.append({"Symbol": symbol, "Weighting": weight}, ignore_index=True)

    df.set_index('Symbol', inplace=True)

    return __generate_pie_chart(df)


def patch_df(df):
    for index, row  in df.iterrows():
        if row["Beta"] == "N/A":
            df.at[index, "Beta"] = float('nan')
        if row["PE"] == "N/A":
            df.at[index, "PE"] = float('nan')

def main():
    st.markdown("## Portfolio")
    st.sidebar.markdown("Portfolio")
    if check_password():
        date = st.date_input(label="date")
        client = MongoClient("mongodb+srv://" +  urllib.parse.quote_plus(config.MONGO_USER) 
            + ":" + urllib.parse.quote_plus(config.MONGO_PASSWORD) + "@" + config.MONGO_URL + "/?retryWrites=true&w=majority")

        db = client["finReport"]
        my_time = datetime.min.time()
        my_datetime = datetime.combine(date, my_time)

        result = db.reports.find({"batch_date": my_datetime})

        for r in result:
            st.write("### Asset report " + str(r["batch_date"]))
            st.write("Creation time: " + str(r["creation_time"]))
            
            df_hk = pd.read_json(r["stock.hk"])
            df_us = pd.read_json(r["stock.us"])
            df_crypto = pd.read_json(r["crypto"])

            st.write("#### US stock " )
            patch_df(df_us)
            st.write(df_us)
            total_usd=  df_us["Total USD"].sum()
            
            st.write("Total USD: " + str(total_usd))
            st.write(r["stock.us.hedge"])

            __generate_stock_us_pie(df_us)

            st.write("#### HK stock " )
            patch_df(df_hk)
            st.write(df_hk)
            total_hkd=  df_hk["Total HKD"].sum()
            st.write("Total HKD: " + str(total_hkd))
            st.write(r["stock.hk.hedge"])

            __generate_stock_hk_pie(df_hk)
            
            st.write("#### Crypto " )
            #patch_df(df_crypto)
            df_crypto = df_crypto[df_crypto["Position"]> 0]
            st.write(df_crypto)

            total_usd=  df_crypto["Total USD"].sum()
            st.write("Total USD: " + str(total_usd))
            __generate_crypto_pie(df_crypto)

main()