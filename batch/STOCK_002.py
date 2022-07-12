# STOCK_002, daily job to update price.

import mysql.connector
import config
import datetime
import util
import sys
import requests
import yfinance as yf
import os

sql_get_data_vendor = """select * from data_vendor 
where name='{name}'
"""

sql_create_tmp_table = """create table hkstock_tmp(
	symbol_id bigint NOT NULL,
	price_date datetime NOT NULL,
    open_price decimal(19,4) NULL,
	high_price decimal(19,4) NULL,
	low_price decimal(19,4) NULL,
	close_price decimal(19,4) NULL,
	adj_close_price decimal(19,4) NULL,
	volume bigint NULL
)
"""

sql_get_hk_stock = "select s.*, e.abbrev from symbol s left join exchange e on (s.exchange_id = e.id) where instrument = 'HK STOCK'"
sql_get_us_stock = "select s.*, e.abbrev from symbol s left join exchange e on (s.exchange_id = e.id) where instrument = 'US STOCK'"

sql_insert_into_tmp_table2 = """insert into hkstock_tmp
values (
    {symbol_id}, {price_date}, {open_price}, {high_price},
    {low_price}, {close_price}, {adj_close_price}, {volume}
)
"""

sql_insert_into_tmp_table = """insert into hkstock_tmp
values ( %s, %s, %s, %s, %s, %s, %s, %s )
"""

sql_detect_adj_close_diff = """
select t.symbol_id, s.ticker, max(abs(t.adj_close_price - p.adj_close_price)) as max_diff
 from hkstock_tmp t
left join daily_price p
    on (t.symbol_id = p.symbol_id and t.price_date = p.price_date)
left join symbol s on (t.symbol_id = s.id)
where abs(t.adj_close_price - p.adj_close_price) > {threshold}
group by t.symbol_id
"""

sql_insert_into_main_table = """INSERT INTO daily_price
  (version, data_vendor_id, symbol_id, price_date, created_date, last_updated_date, 
    open_price, high_price, low_price, close_price, adj_close_price, volume)
select 1, {vendor_id}, symbol_id, price_date, '{create_date}', '{last_updated_date}',
    open_price, high_price, low_price, close_price, adj_close_price, volume
from hkstock_tmp
ON DUPLICATE KEY UPDATE
  version = version +1,
  last_updated_date  = VALUES(last_updated_date),
  open_price = VALUES(open_price),
  high_price = VALUES(high_price),
  low_price = VALUES(low_price),
  close_price = VALUES(close_price),
  adj_close_price = VALUES(adj_close_price),
  volume = VALUES(volume)
"""

sql_insert_log_message = """insert into log_message 
values
('{category}', '{message}', '{create_date}')
"""

sql_drop_tmp_table = "drop table hkstock_tmp"

log_header = "STOCK_DAILY"

def read_hk_stock(cursor):
    sql = sql_get_hk_stock
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print("Failed to read HK stock: {}".format(err))
        return None, False

def read_us_stock(cursor):
    sql = sql_get_us_stock
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print("Failed to read US stock: {}".format(err))
        return None, False


def dowload_data(symbol, start_date, end_date):
    try:
        ticker = util.get_yahoo_ticker(symbol["abbrev"], symbol["ticker"])
        start_date_str = util.format_date(start_date)
        end_date_str = util.format_date(end_date)

        data = yf.download(ticker, start=start_date_str, end=end_date_str)

        return data, True
    except Exception as err:
        print("Failed to get data from Yahoo: {}".format(err))
        return None, False

def dowload_dataX(symbol, start_date, end_date):
    ticker = util.get_yahoo_ticker(symbol["abbrev"], symbol["ticker"])
    start_date_str = util.format_date(start_date)
    end_date_str = util.format_date(end_date)
    data = yf.download(ticker, start=start_date_str, end=end_date_str)

    return data, True

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
        print("Failed creating database: {}".format(err))
        return False

def insert_record_into_tmp_table(cursor, symbol_id, prices):
    try:
        data = []
        for index, price in prices.iterrows():
            data.append( (symbol_id, util.format_date(index),
                float(price["Open"]), float(price["High"]), float(price["Low"]), 
                float(price["Close"]), float(price["Adj Close"]), int(price["Volume"])
            ) )

        cursor.executemany(sql_insert_into_tmp_table, data)
        return True
    except Exception as err:
        print("Failed inserting record to temp table: {}".format(err))
        return False

def check_symbol_adj_close(cursor):
    try:
        sql = sql_detect_adj_close_diff.format(threshold=1)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print("Failed to detect adj close diff: {}".format(err))
        return None, False

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

def merge_into_price_date(cursor, vendor_id):
    try:
        curtime = util.format_datetime(datetime.datetime.now())
        sql = sql_insert_into_main_table.format(
            vendor_id = vendor_id, create_date=curtime, 
            last_updated_date =curtime
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
        print("Failed recording message: {}".format(err))
        return False

def run_job(region, batch_date_str):
    mydb = None
    cursor = None
    batch_date = datetime.datetime.strptime(batch_date_str, '%Y-%m-%d')

    try: 
        mydb = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        cursor = mydb.cursor(dictionary=True)
        
        if(region.upper() == 'HK'):
            stock_list, success = read_hk_stock(cursor)
        elif(region.upper() == 'US'):
            stock_list, success = read_us_stock(cursor)
        else: 
            success = False
        if not success:
            sys.exit(1)

        start_date = batch_date - datetime.timedelta(days=7)
        end_date = batch_date + datetime.timedelta(days=1)  # include today
        
        vendor_rows, success = get_data_vendor(cursor, "Yahoo")
        if not success:
            sys.exit(1)
        if vendor_rows == None or len(vendor_rows) == 0:
            print("No such vendor exists: Yahoo")
            sys.exit(1)

        vendor_id = vendor_rows[0]["id"]

        queue = []
        for symbol in stock_list:
            queue.append((symbol, 0))

        success = create_tmp_table(cursor)
        if not success:
            sys.exit(1)

        while queue:
            (symbol, retry) = queue.pop(0)
            data, success = dowload_data(symbol, start_date, end_date)
            #print("x")
            #print(data)

            if success: 
                success = insert_record_into_tmp_table(cursor, symbol["id"], data)
                if not success:
                    message = f"Failed to insert data: {symbol}"
                    log_message(cursor, message)
                    print(message)
                else:
                    print(f"Success: {symbol}")
            else:
                if retry < 3: 
                    queue.append((symbol, retry+1))
                else:
                    message = f"Failed to download data for symbol: {symbol}"
                    log_message(cursor, message)
                    print(message)
        
        mydb.commit()

        symbol_adj, success = check_symbol_adj_close(cursor)
        if not success:
            sys.exit(1)

        for row in symbol_adj:
            symbol = row["ticker"]
            max_diff = row["max_diff"]
            success = log_message(cursor, f"Please check HK symbol {symbol}, adj close not matched, max diff= {max_diff}")
            if not success:
                print("Failed to write log to db.")

        mydb.commit()

        success = merge_into_price_date(cursor, vendor_id)
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
    region = sys.argv[1]
    batch_date = sys.argv[2]
    
    run_job(region, batch_date)