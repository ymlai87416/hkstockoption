# Fetch option data from HKEx

import mysql.connector
import config
import datetime
import util
import sys
import requests
from io import BytesIO, StringIO
from zipfile import ZipFile
from urllib.request import urlopen
import pandas as pd
import os
import calendar

df_url = "https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/dqe{date}.zip"

sql_get_data_vendor = """select * from data_vendor 
where name='{name}'
"""

sql_create_tmp_table = """create table hk_stock_option_tmp(
    stock_name varchar(255) NULL,
    expire_date datetime NOT NULL,
    type varchar(1) NOT NULL,
    strike_price decimal(19,4) NULL,
    underlying_asset_ticker varchar(32) NOT NULL,
    series_id bigint NULL,
    price_date datetime NOT NULL,
    open_price decimal(19,4) NULL,
	high_price decimal(19,4) NULL,
	low_price decimal(19,4) NULL,
	close_price decimal(19,4) NULL,
    volume bigint NULL,
	iv decimal(19,4) NULL,
	open_interest bigint NULL
)
"""

sql_insert_into_tmp_table2 = """insert into hk_stock_option_tmp(
    stock_name, expire_date, type, strike_price, underlying_asset_ticker,
    price_date, open_price, high_price, low_price, close_price,
    volume, iv, open_interest
)
values(
    {symbol_id}, {expire_date}, {type}, {strike_price}, 
    {underlying_asset_ticker}, {price_date},
    {open_price}, {high_price}, {low_price}, {close_price},
    {volume}, {iv}, {open_interest}
)
"""

sql_insert_into_tmp_table = """insert into hk_stock_option_tmp(
    stock_name, expire_date, type, strike_price, underlying_asset_ticker,
    price_date, open_price, high_price, low_price, close_price,
    volume, iv, open_interest
)
values(
    %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s
)
"""


sql_populate_series_id_tmp_table = """update hk_stock_option_tmp t
left join symbol s on (s.exchange_id = {exchange_id} and s.ticker = concat(t.stock_name,  DATE_FORMAT(t.expire_date , '%y%m%d'), t.type,  format(t.strike_price, 2)))
set t.series_id = s.id 
"""

sql_insert_into_table_new_series = """insert into symbol
(version, exchange_id, ticker, instrument, underlying_asset_ticker, name, sector, lot, currency, created_date, last_updated_date)
select 1, {hkex_id}, 
    concat(t.stock_name,  DATE_FORMAT(t.expire_date , '%y%m%d'), t.type,  format(t.strike_price, 2)),
    'HK STOCK OPTION', underlying_asset_ticker,
    concat(t.stock_name,  DATE_FORMAT(t.expire_date , '%y%m%d'), t.type,  format(t.strike_price, 2)), 
    NULL, 1, 'HKD', now(), now()
    from hk_stock_option_tmp t
where t.series_id is NULL
"""

sql_merge_tmp_to_daily_price = """insert into daily_price
(version, data_vendor_id, symbol_id, price_date, created_date, last_updated_date, 
    open_price, high_price, low_price, close_price, volume, iv, open_interest)
select 1, {hkex_id}, t.series_id, t.price_date, now(), now(), 
    t.open_price, t.high_price, t.low_price, t.close_price, t.volume, t.iv, t.open_interest
from hk_stock_option_tmp t
ON DUPLICATE KEY UPDATE
  version = version+1,
  last_updated_date  = VALUES(last_updated_date),
  open_price = VALUES(open_price),
  high_price = VALUES(high_price),
  low_price = VALUES(low_price),
  close_price = VALUES(close_price),
  iv = VALUES(iv),
  open_interest = VALUES(open_interest),
  volume = VALUES(volume)
"""

sql_insert_log_message = """insert into log_message 
values
('{category}', '{message}', '{create_date}')
"""

sql_drop_tmp_table = "drop table hk_stock_option_tmp"

sql_truncate_hk_option = "truncate hk_option_list"

sql_insert_hk_option = """insert into hk_option_list (hkats_code, ticker, name)
values (%s, %s, %s)
"""

log_header = "HK_STOCK_OPTION"

def get_expiry_date(expiry_date):
    ed = datetime.datetime.strptime(expiry_date, '%b%y')
    last_day = calendar.monthrange(ed.year, ed.month)[1]
    return datetime.datetime(ed.year, ed.month, last_day)

def download_data(batch_date):
    """
    This is to read the download file
    return a summary and a map with (symbol (2823), price_table)
    """
    batch_date_str = batch_date.strftime("%y%m%d")
    #resp = urlopen(df_url.format(date=batch_date_str))
    #zipfile = ZipFile(BytesIO(resp.read()))
    resp = requests.get(df_url.format(date=batch_date_str), stream=True)
    zipfile = ZipFile(BytesIO(resp.content))
    return readfile(zipfile.open("dqe"+batch_date_str + ".csv").readlines())

def readfile(linesep):
    #f = open("../db/job/3 hk stock option daily/dqe220628.csv", "r", encoding='UTF-8')

    summary_df = pd.DataFrame(columns=["HKATS CODE","UNDERLYING STOCK","TICKER","TOTAL-TRADING","CALLSL-TRADING","PUTSL-TRADING",
        "TOTAL-OI","CALLS-OI","PUTS-OI","IV%"])
    dict_df = {}

    # read file - the summary
    #read until this line: ,,,"SUMMARY TRADING VOLUME",,,"SUMMARY OPEN INTEREST"

    summary_header = '"HKATS CODE","UNDERLYING STOCK",,"TOTAL","CALLS","PUTS","TOTAL","CALLS","PUTS","IV%*"'
    contract_header = '"CONTRACT",,,"OPENING PRICE#","DAILY HIGH#","DAILY LOW#","SETTLEMENT PRICE","CHANGE IN SETTLEMENT","IV%","VOLUME","OPEN INTEREST","CHANGE IN OI"'
    cnt = 0

    #linesep = f.readlines()
    state = 0
    empty_line = 0
    data_list = []
    for line in linesep:
        line = line.decode('utf8')
        line = line.strip()
        cnt += 1

        if state == 0:
            if line == summary_header:
                #print("state 1 at " + str(cnt))
                state = 1
                data_list = []
                continue
            elif line == contract_header:
                #print("state 2 at " + str(cnt))
                state = 2
                data_list = []
                continue
        
        if state == 1:
            if(line == ""):
                summary_df = summary_df.append(data_list, ignore_index=True)
                state = 0
            else:
                dd = line.split(",")
                data = {"HKATS CODE": dd[0] ,"UNDERLYING STOCK" : dd[1], "TICKER": dd[2],
                    "TOTAL-TRADING": dd[3],"CALLS-TRADING": dd[4],"PUTS-TRADING": dd[5],
                    "TOTAL-OI": dd[6],"CALLS-OI": dd[7],"PUTS-OI": dd[8],"IV%": dd[9]}
                data_list.append(data)
                
        if state == 2:
            if line == "":
                empty_line +=1
            else:
                empty_line = 0

            if empty_line == 2:
                #print("finish")
                call_put = call_put.append(data_list, ignore_index=True)
                dict_df[symbol] = call_put
                state = 0

            elif line.startswith('"CLASS'):
                symbol = line.split(" ")[1]
                #print("x" + line)

                call_put = pd.DataFrame(columns=["CONTRACT-EXPIRY","CONTRACT-STRIKE","CONTRACT-TYPE",
                    "OPENING PRICE","DAILY HIGH","DAILY LOW", "SETTLEMENT PRICE","CHANGE IN SETTLEMENT","IV%",
                    "VOLUME","OPEN INTEREST","CHANGE IN OI"])
            else:
                #print("y" + line)
                dd = line.split(",")
                if dd[0] == "":
                    continue

                data = {"CONTRACT-EXPIRY": dd[0],"CONTRACT-STRIKE": dd[1],"CONTRACT-TYPE": dd[2],
                    "OPENING PRICE": dd[3],"DAILY HIGH": dd[4],"DAILY LOW": dd[5], "SETTLEMENT PRICE": dd[6],
                    "CHANGE IN SETTLEMENT": dd[7],"IV%": dd[8],
                    "VOLUME": dd[9],"OPEN INTEREST": dd[10],"CHANGE IN OI": dd[11]}
                data_list.append(data)
    
    return summary_df, dict_df, True
            
def get_data_vendor(cursor, vendor):
    sql = sql_get_data_vendor.format(name = vendor)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print("Failed to get data vendor: {}".format(err))
        return None, False

def create_tmp_table(cursor):
    sql = sql_create_tmp_table
    try:
        cursor.execute(sql)
        return True
    except mysql.connector.Error as err:
        print("Failed creating temp table: {}".format(err))
        return False

def insert_record_into_tmp_table(cursor, batch_date, symbol_df, price_df):
    try:
        sql = sql_insert_into_tmp_table
        data = [] 

        name = symbol_df.iloc[0]['HKATS CODE']
        underlying  = symbol_df.iloc[0]['TICKER'].strip("()")
        batch_date_str = util.format_date(batch_date)

        for _, price in price_df.iterrows():
            expiry_date = get_expiry_date(price["CONTRACT-EXPIRY"])
            data.append((name, util.format_date(expiry_date),
                price["CONTRACT-TYPE"], price["CONTRACT-STRIKE"],
                underlying, batch_date_str, 
                float(price["OPENING PRICE"]), float(price["DAILY HIGH"]), 
                float(price["DAILY LOW"]), float(price["SETTLEMENT PRICE"]), 
                int(price["VOLUME"]), float(price["IV%"]), int(price["OPEN INTEREST"])))

        cursor.executemany(sql, data)
        return True
    except Exception as err:
        print("Failed inserting record to temp table: {}".format(err))
        return False

def merge_into_main_table(cursor, hkex_id):
    try:
        sql = sql_populate_series_id_tmp_table.format(exchange_id = hkex_id)
        cursor.execute(sql)

        sql = sql_insert_into_table_new_series.format(hkex_id = hkex_id)
        cursor.execute(sql)

        sql = sql_populate_series_id_tmp_table.format(exchange_id = hkex_id)
        cursor.execute(sql)

        sql = sql_merge_tmp_to_daily_price.format(hkex_id = hkex_id)
        cursor.execute(sql)

        return True
    except Exception as err:
        print("Failed inserting record to main table: {}".format(err))
        print("Error SQL: " + sql)
        return False

def insert_summary_table(cursor, summary_df):
    try:
        sql = sql_truncate_hk_option
        cursor.execute(sql)

        data = []
        for _, row in summary_df.iterrows():
            data.append((row["HKATS CODE"], row["TICKER"].strip("()"), row["UNDERLYING STOCK"]))
        print("x")
        print(data)
        sql = sql_insert_hk_option
        cursor.executemany(sql, data)

        return True

    except Exception as err:
        print("Failed to insert summary table: {}".format(err))
        return False

def log_message(cursor, log_header, message):
    try:
        curtime = util.format_datetime(datetime.datetime.now())
        sql = sql_insert_log_message.format(
            category = log_header, message = message, 
            create_date = curtime
            )
        cursor.execute(sql)
        return True
    except Exception as err:
        print("Failed recording message: {}".format(err))
        return False

def drop_table(cursor):
    try:
        sql = sql_drop_tmp_table
        cursor.execute(sql)
        return True
    except Exception as err:
        print("Failed to drop tmp table: {}".format(err))
        return False

def log_message(cursor, message):
    try:
        curtime = util.format_datetime(datetime.datetime.now())
        sql = sql_insert_log_message.format(
            category = log_header, message = message, 
            create_date = curtime
            )
        cursor.execute(sql)
        return True
    except Exception as err:
        print("Failed recording message: {}".format(err))
        return False

def run_job(batch_date):
    mydb = None
    cursor = None
    batch_date = datetime.datetime.strptime(batch_date, '%Y-%m-%d')

    try:
        mydb = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        cursor = mydb.cursor(dictionary=True)

        summary_df, price_map, success = download_data(batch_date)
        if not success:
            sys.exit(1)

        hkex, success = get_data_vendor(cursor, "HKEX")
        if not success:
            sys.exit(1)
        
        hkex_id = hkex[0]["id"]

        success = create_tmp_table(cursor)
        if not success:
            sys.exit(1)

        success = insert_summary_table(cursor, summary_df)
        if not success:
            sys.exit(1)

        mydb.commit()

        for symbol in price_map.keys():
            print("processing: " + symbol)
            #if(symbol > "AGG"):
            #    break
            data = price_map[symbol]
            symbol_df = summary_df.loc[summary_df['HKATS CODE'] == symbol].head(1)

            success = insert_record_into_tmp_table(cursor, batch_date, symbol_df, data)

            if not success:
                message = f"Failed to insert option price into tmp table: {symbol}"
                log_message(cursor, message)
                print(message)

            mydb.commit()

        success = merge_into_main_table(cursor, hkex_id)
        if not success:
            sys.exit(1)

        mydb.commit()

        success = drop_table(cursor)
        if not success:
            sys.exit(1)

    except Exception as err:
        print("Failed to execute batch job: {}".format(err))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        sys.exit(1)
    finally:
        if not cursor == None:
            cursor.close()
        if not mydb == None:
            mydb.close()
    
if __name__ == '__main__':
    batch_date = sys.argv[1]
    
    run_job(batch_date)