from pathlib import Path
from numpy import result_type
import talib
import os
import arrow
import pysftp
import logging
from io import StringIO
import matplotlib.pyplot as plt
import urllib
from ymlai87416_common.data import crypto, google_api, yahoo, coingecko
from datetime import datetime, timedelta
from pymongo import MongoClient
import pandas as pd
import yaml
import pytz
import mysql.connector
import summary_config
import sys

# A daily batch to generate report for my current financial position

# * Create a summary on stop loss position and how bad you need
# * If hedge is needed, tell you how many QQQ put option or 2800 put option you need to buy

# All the stock data is read from google sheets, we do IB API if we have a good HSI or MHI bot in paper trading account for IB
# All the cryto data is read from google sheets because they scatter.

# Here are the secret to be passed
# Both config.yaml and service_account.json is passed as config map


def __get_crypto_df():
    result = pd.DataFrame(columns = ['Symbol', 'Position', 'Price', 'Total USD', 'ATR', 'Suggested stop'])
    return result

def __get_stock_us_df():
    result = pd.DataFrame(columns = ['Symbol','Price', 'Position', 'Total USD', 'Unrealized profit',
     'ATR', 'Suggested stop', 'Beta', 'PE', 'Pct.'])
    return result

def __get_stock_hk_df():
    result = pd.DataFrame(columns = ['Symbol','Price', 'Position', 'Total HKD', 'Unrealized profit',
     'ATR', 'Suggested stop', 'Beta', 'PE', 'Pct.'])
    return result

# Here is the procedure
def __get_crypto_data():
    # Read the google spreadsheet, get my crypto assets and then
    values = google_api.read_spreadsheet(
        summary_config.crypto_spreadsheet_id, 
        summary_config.crypto_spreadsheet_range,
        {"google_service_key": summary_config.google_service_key})

    crypto_df = __get_crypto_df()

    #get history data to calculate the current price and ATR
    #start_date = datetime.today().date() + timedelta(days=-30)
    #end_date = datetime.today().date()
    for row in values:
        symbol = row[0] #row 1 is gecko symbol
        position = float(row[3])
        olhc = coingecko.get_olhc(row[1], 30)
        if not olhc is None:
            price = olhc["Close"].iloc[-1]
            atr_df = talib.ATR(olhc["High"], olhc["Low"], olhc["Close"], timeperiod=14)
            atr = atr_df[-1]
            total_price = price * position

            if position > 0: 
                highest_price = olhc["High"].max()
                suggested_stop = highest_price - atr* 3
            else:
                lowest_price = olhc["Low"].min()
                suggested_stop = lowest_price + atr* 3

        else:
            price = 0
            atr = 0
            total_price = 0
            suggested_stop = 0
        

        crypto_df = crypto_df.append({"Symbol": symbol, "Position": position, "Price": price, 
            "Total USD": total_price, "ATR": atr, "Suggested stop": suggested_stop}, ignore_index=True)

    return crypto_df

def __get_stock_business_date(region: str):
    result_date = None
    if region == "US":
        _now = datetime.now(pytz.timezone('America/New_York'))
        # new york trade start at 9:30am
        if _now.hour * 60 + _now.minute < 9*60 + 30:
            result_date = datetime(_now.year, _now.month, _now.day) - timedelta(days=1)
        else:
            result_date = datetime(_now.year, _now.month, _now.day)
    elif region == "HK": 
        _now = datetime.now(pytz.timezone('Asia/Hong_Kong'))
        # HK trade start at 9:30am
        if _now.hour * 60 + _now.minute < 9*60 + 30:
            result_date = datetime(_now.year, _now.month, _now.day) - timedelta(days=1)
        else:
            result_date = datetime(_now.year, _now.month, _now.day)

    return result_date

def __get_stock_data_hk():
    stock_df = __get_stock_hk_df()
    
    end_date = __get_stock_business_date("HK")
    start_date = datetime.today().date() + timedelta(days=-30)
    
    # get portfolio from google sheet, filter by US
    values = google_api.read_spreadsheet(
        summary_config.stock_spreadsheet_id,
        summary_config.stock_spreadsheet_range, 
        {"google_service_key": summary_config.google_service_key})

    for row in values:
        region = row[0]
        if not region == "HK":
            continue

        symbol = row[1].strip().replace(' ', '.')
        position = float(row[2])
        enter_price = float(row[3])
        logging.info("Processing stock symbol: " + symbol)

        _info = yahoo.get_info_hk(symbol)
        _history = yahoo.get_olhc_hk(symbol, start_date, end_date)

        if ("beta" in _info) and (not _info["beta"] is None) :
            beta = _info["beta"]
        else:
            beta = "N/A"
        
        if "trailingPE" in _info and (not _info["trailingPE"] is None) : 
            pe = _info["trailingPE"]
        else:
            pe = "N/A"

        if "currentPrice" in _info and (not _info["currentPrice"] is None) : 
            market_price = _info["currentPrice"]
        else:
            market_price = 0
        
        total = position * market_price
        unrealized_profit = position * (market_price - enter_price)

        # now get the latest 14 day price
        atr_df = talib.ATR(_history["High"], _history["Low"], _history["Close"], timeperiod=14)
        #print(atr_df)
        atr = atr_df[-1]
        if position > 0: 
            highest_price = _history["High"].max()
            suggested_stop = highest_price - atr* 3
        else:
            lowest_price = _history["Low"].min()
            suggested_stop = lowest_price + atr* 3


        stock_df = stock_df.append({"Symbol": symbol, "Price": market_price, "Position": position, "Total HKD": total, 
            'Unrealized profit': unrealized_profit, "ATR": atr, 'Suggested stop': suggested_stop, "Beta": beta, "PE": pe} , ignore_index=True)

    stock_total = stock_df['Total HKD'].sum()

    for index, row  in stock_df.iterrows():
        #print("d", row["Total USD"], stock_total, float(row["Total HKD"]) / stock_total)
        stock_df.loc[index, "Pct."]  = float(row["Total HKD"]) / stock_total

    return stock_df

def __get_stock_data_us():
    
    stock_df = __get_stock_us_df()
    
    end_date = __get_stock_business_date("US")
    start_date = datetime.today().date() + timedelta(days=-30)

    # get portfolio from google sheet, filter by US
    values = google_api.read_spreadsheet(
        summary_config.stock_spreadsheet_id,
        summary_config.stock_spreadsheet_range, 
        {"google_service_key": summary_config.google_service_key})

    for row in values:
        region = row[0]
        if not region == "US":
            continue

        symbol = row[1].strip().replace(' ', '-')  # required by yahoo finance
        position = float(row[2])
        enter_price = float(row[3])
        logging.info("Processing stock symbol: " + symbol)

        _info = yahoo.get_info_us(symbol)
        _history = yahoo.get_olhc_us(symbol, start_date, end_date)

        if ("beta" in _info) and (not _info["beta"] is None) : 
            beta = _info["beta"]
        else:
            beta = "N/A"
        
        if ("trailingPE" in _info) and (not _info["trailingPE"] is None) :
            pe = _info["trailingPE"]
        else:
            pe = "N/A"

        if ("currentPrice" in _info) and (not _info["currentPrice"] is None):
            market_price = _info["currentPrice"]
        else:
            market_price = _history["Close"][-1]
        
        total = position * market_price
        unrealized_profit = position * (market_price - enter_price)

        # now get the latest 14 day price
        atr_df = talib.ATR(_history["High"], _history["Low"], _history["Close"], timeperiod=14)
        #print(atr_df)
        atr = atr_df[-1]
        if position > 0: 
            highest_price = _history["High"].max()
            suggested_stop = highest_price - atr* 3
        else:
            lowest_price = _history["Low"].min()
            suggested_stop = lowest_price + atr* 3

        stock_df = stock_df.append({"Symbol": symbol, "Price": market_price, "Position": position, "Total USD": total, 
            'Unrealized profit': unrealized_profit, "ATR": atr, 'Suggested stop': suggested_stop, "Beta": beta, "PE": pe} , ignore_index=True)

    stock_total = stock_df['Total USD'].sum()

    for index, row  in stock_df.iterrows():
        #print("d", row["Total USD"], stock_total, float(row["Total HKD"]) / stock_total)
        stock_df.loc[index, "Pct."] = float(row["Total USD"]) / stock_total

    return stock_df

def __sftp_data(file_local_path):
    # Accept any host key (still wrong see below)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    file_remote_dir = summary_config.archive_sftp
    sftp = pysftp.Connection(summary_config.synology_sftp_url, 
        port=summary_config.synology_sftp_port,
        username=summary_config.synology_username, 
        password=summary_config.synology_password, private_key=".ppk",
        cnopts=cnopts)
    sftp.chdir(file_remote_dir)
    sftp.put(file_local_path)

def __generate_pie_chart(df):
    '''
    generate a string on the graph:
    https://stackoverflow.com/questions/5453375/matplotlib-svg-as-string-and-not-a-file
    '''
    fig, axs = plt.subplots(figsize=(8, 5)) 
    plot = df.plot.pie(y='Weighting', ax=axs, autopct='%1.1f%%')

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)  # rewind the data

    svg_dta = imgdata.read()  # this is svg data 
    #print("debug svg: ", svg_dta)
    return svg_dta

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

def __convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def __write_to_notification(path):
    mydb = mysql.connector.connect(
            host=summary_config.database_host,
            user=summary_config.database_user,
            password=summary_config.database_password,
            database=summary_config.database_name,
        )
        
    mycursor = mydb.cursor()

    blob = __convertToBinaryData(path)

    sql = """INSERT INTO message (content, attachment, created_date, status, category, attachment_name) 
        VALUES (%s, %s, %s, %s, %s, %s)"""

    report_name = "report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".html"

    val = ("Report ready", blob, datetime.now(), 0, "STOCK", report_name)
    mycursor.execute(sql, val)

    mydb.commit()
    mycursor.close()
    mydb.close()

def __get_hedge_us(stock_us):
    '''
    Find out my position beta and how much NASDAQ I need to short or long
    '''
    # hedge using QQQ, which have beta = 1
    equiv_portfolio = 0
    for _, row in stock_us.iterrows():
        try:
            equiv_portfolio += row["Total USD"] * row["Beta"]
        except:
            pass

    start_date = datetime.today().date() + timedelta(days=-7)
    end_date = datetime.today().date()
    _history = yahoo.get_olhc_hk("QQQ", start_date, end_date)
    _qqq_latest = _history["Close"][-1]
    #now simply divide by the price of QQQ and we got the answer
    no_qqq = equiv_portfolio / _qqq_latest

    return "Equivalent to QQQ share= %.2f" % (no_qqq) 


def __get_hedge_hk(stock_hk):
    '''
    Find out my position beta and how much NASDAQ I need to short or long
    '''
    # hedge using 2800, which have beta = 1
    equiv_portfolio = 0
    for _, row in stock_hk.iterrows():
        try:
            equiv_portfolio += row["Total HKD"] * row["Beta"]
        except:
            pass

    start_date = datetime.today().date() + timedelta(days=-7)
    end_date = datetime.today().date()
    _history = yahoo.get_olhc_hk("2800.HK", start_date, end_date)
    _2800_latest = _history["Close"][-1]
    #now simply divide by the price of QQQ and we got the answer
    no_2800 = equiv_portfolio / _2800_latest

    return "Equivalent to 2800.hk share= %.2f" % (no_2800) 

def __create_summary_table(summary_df):
    _column_name = list(summary_df.columns.values)

    _result = "<table style='border-collapse: collapse; '>"
    _header = "<theader>"
    for col in _column_name:
        _header = _header + "<th style='border:1px solid black; padding: 0px 10px;'>" + col + "</th>"
    _header = _header + "</theader>"
    
    _result = _result + _header

    for _, row  in summary_df.iterrows():

        _suggest_stop_color = None

        if "Price" in _column_name and "Suggested stop" in _column_name:
            if row["Price"] <= row["Suggested stop"]:
                _suggest_stop_color = "#FF0000"
            elif row["Price"] <= row["Suggested stop"] * 1.1:
                _suggest_stop_color = "#FF7b00"
            else:
                _suggest_stop_color = "#000000"

        _row = "<tr>"
        for col in _column_name:
            _value = row[col] if type(row[col]) == str else str(round(row[col], 2))
            if col == "Suggested stop":
                _row  = _row  + f"<td style='border:1px solid black;'><p style='color:{_suggest_stop_color}'>" + _value + "</p></td>"
            else:
                _row  = _row  + "<td style='border:1px solid black;'>" + _value + "</td>"
        _row = _row + "</tr>"
        _result = _result + _row

    _result = _result + "</table>"

    return _result


def __write_to_mongodb(data):
    mongodbUrl = "mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority".\
    format(urllib.parse.quote_plus(summary_config.mongo_user), 
        urllib.parse.quote_plus(summary_config.mongo_password), 
        summary_config.mongo_host)
    client = MongoClient(mongodbUrl)
    
    db = client[summary_config.mongo_db_name]
    #date_str = batchDate.strftime('%Y%m%d')
    collection = db["reports"]
    collection.delete_many({"batch_date": data["batch_date"]})
    print(data)
    collection.insert_one(data)

    client.close()

def generate_report(batch_date):
    batch_date = datetime.strptime(batch_date, '%Y%m%d')

    crypto = __get_crypto_data()
    stock_us = __get_stock_data_us()
    stock_hk = __get_stock_data_hk()

    #TODO: add HK region and do the final test
    crypto_total = crypto['Total USD'].sum()
    stock_total = stock_us['Total USD'].sum()
    stock_hk_total = stock_hk['Total HKD'].sum()

    crypto_pie_svg = __generate_crypto_pie(crypto)
    stock_pie_svg = __generate_stock_us_pie(stock_us)
    stock_hk_pie_svg = __generate_stock_hk_pie(stock_hk)

    hedge_us = __get_hedge_us(stock_us)
    hedge_hk = __get_hedge_hk(stock_hk)

    # summary table
    stock_us_html = __create_summary_table(stock_us)
    stock_hk_html = __create_summary_table(stock_hk)
    crypto_html = __create_summary_table(crypto)

    # Then generate report
    current_date = datetime.today().date()
    title_text = "Asset report: " + current_date.strftime("%Y%m%d")
    report_name = "asset_" + current_date.strftime("%Y%m%d") + ".html"

    result = dict()
    result["batch_date"] = batch_date
    result["creation_time"] = datetime.now()
    result["title_text"] = title_text
    result["stock.us"] = stock_us.to_json()
    result["stock.us.hedge"] = hedge_us
    result["stock.hk"] = stock_hk.to_json()
    result["stock.hk.hedge"] = hedge_hk
    result["crypto"] = crypto.to_json()

    # write to streamlit visualization
    __write_to_mongodb(result)

    # 2. Combine them together using a long f-string
    html = f'''
        <html>
            <head>
                <title>{title_text}</title>
            </head>
            <body>
                <h1>{title_text}</h1>
                <h2>US Stock information: </h2>
                {stock_us_html}

                <h2>Weighting</h2>
                {stock_pie_svg}

                <p>Total assets in stock: {stock_total}</p>
                <p>Hedge info: {hedge_us}</p>

                <h2>HK Stock information: </h2>
                {stock_hk_html}

                <h2>Weighting</h2>
                {stock_hk_pie_svg}

                <p>Total assets in stock: {stock_hk_total}</p>
                <p>Hedge info: {hedge_hk}</p>

                <h2>Cryto information</h2>
                {crypto_html}

                <h2>Weighting</h2>
                {crypto_pie_svg}

                <p>Total assets in crypto: {crypto_total}</p>
            </body>
        </html>
        '''

    report_path = os.path.join(summary_config.report_location, report_name)

    with open(report_path, 'w') as f:
        f.write(html)

    # Upload it to the server
    #__sftp_data(report_path, config)
    # Write a message to the bot for notification
    __write_to_notification(report_path)

    

if __name__ == '__main__':
    batch_date = sys.argv[1]
    generate_report(batch_date)
