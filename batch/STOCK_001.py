from http.client import REQUEST_URI_TOO_LONG
import sys
import util
import datetime
import config
import mysql.connector
import csv
import yfinance as yf
import pickle
import pandas as pd
import os

sql_create_symbol_tmp_table = """create table symbol_tmp (
	exchange_id bigint NULL,
	ticker varchar(32) NOT NULL,
	instrument varchar(64) NOT NULL,
	name varchar(255) NULL,
	sector varchar(255) NULL,
	lot	int NULL,
	currency varchar(32) NULL,
    last_price_date datetime NULL
)
"""

sql_select_vendor = "select * from data_vendor where name='{name}'"

sql_create_price_tmp_table = """create table daily_price_tmp (
	data_vendor_id bigint NOT NULL,
    exchange_id bigint NULL,
	ticker varchar(32) NOT NULL,
    series_id bigint NULL,
	price_date datetime NOT NULL,
	open_price decimal(19,4) NULL,
	high_price decimal(19,4) NULL,
	low_price decimal(19,4) NULL,
	close_price decimal(19,4) NULL,
	adj_close_price decimal(19,4) NULL,
	volume bigint NULL
)
"""

sql_insert_series_tmp2 = """insert into symbol_tmp
(exchange_id, ticker, instrument, name, sector, lot, currency)
values
({exchange_id}, '{ticker}', '{instrument}', '{name}', '{sector}', {lot}, '{currency}')
"""

sql_insert_series_tmp = """insert into symbol_tmp
(exchange_id, ticker, instrument, name, sector, lot, currency, last_price_date)
values
(%s, %s, %s, %s, %s, %s, %s, %s)
"""

sql_insert_timepoint_tmp = """insert into daily_price_tmp
(data_vendor_id, exchange_id, ticker, price_date, open_price, high_price, low_price, close_price,
    adj_close_price, volume)
values
({data_vendor_id}, {exchange_id}, '{ticker}', '{price_date}', 
    {open_price}, {high_price}, {low_price}, {close_price}, {adj_close_price}, {volume})
"""

sql_insert_timepoint_tmp2 = """insert into daily_price_tmp
(data_vendor_id, exchange_id, ticker, price_date, open_price, high_price, low_price, close_price,
    adj_close_price, volume)
values
(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

sql_not_yet_process = """select t1.*, e.id as exchange_id from STOCK_001_input t1 
    left join exchange e on (t1.exchange = e.abbrev)
    where processed_time is NULL
"""

sql_insert_log_message = """insert into log_message 
values
('{category}', '{message}', '{create_date}')
"""

sql_merge_series = """insert into symbol
(version, exchange_id, ticker, instrument, name, sector, lot, 
    currency, created_date, last_updated_date, last_price_date)
select 1, exchange_id, ticker, instrument, name, sector, lot, currency,
    now(), now(), last_price_date from symbol_tmp
ON DUPLICATE KEY UPDATE
  last_updated_date  = VALUES(last_updated_date),
  version = version+1,
  instrument = VALUES(instrument),
  name = VALUES(name),
  sector = VALUES(sector),
  lot = VALUES(lot),
  currency = VALUES(currency)
"""

sql_populate_price_tmp_series_id = """update daily_price_tmp t
left join symbol s on (t.exchange_id = s.exchange_id and t.ticker = s.ticker)
set t.series_id = s.id
"""

sql_merge_price = """insert into daily_price
(version, data_vendor_id, symbol_id, price_date, created_date, last_updated_date,
    open_price, high_price, low_price, close_price, adj_close_price, volume)
select 1, data_vendor_id, series_id, price_date, now(), now(),
    open_price, high_price, low_price, close_price, adj_close_price, volume
    from daily_price_tmp
ON DUPLICATE KEY UPDATE
  version = version+1,
  last_updated_date  = VALUES(last_updated_date),
  data_vendor_id = VALUES(data_vendor_id),
  open_price = VALUES(open_price),
  high_price = VALUES(high_price), 
  low_price = VALUES(low_price), 
  close_price = VALUES(close_price), 
  adj_close_price = VALUES(adj_close_price), 
  volume = VALUES(volume)
"""

sql_mark_processed = "update STOCK_001_input set processed_time = now() where exchange = %s and ticker = %s"

sql_drop_series_tmp_table = "drop table symbol_tmp"
sql_drop_price_tmp_table = "drop table daily_price_tmp"

log_header = "STOCK_INIT"

def get_not_yet_processed(cursor): 
    sql = sql_not_yet_process
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print("Failed to get unprocessed records: {}".format(err))
        return None, False


def create_tmp_table(cursor):
    try:
        cursor.execute(sql_create_symbol_tmp_table)
        cursor.execute(sql_create_price_tmp_table)
        return True
    except Exception as err:
        print("Failed to create temp table: {}".format(err))
        return False

def insert_series_into_tmp(cursor, row, info, last_price_date):
    try:
        last_price_date_str = datetime.datetime.strftime(last_price_date, '%Y-%m-%d')

        data = (row["exchange_id"], row["ticker"], row["instrument"], 
            info["longName"], info.get("sector", ""), 0, info["currency"], last_price_date_str)

        sql = sql_insert_series_tmp
        cursor.execute(sql, data)
        return True
    except Exception as err:
        print("Failed to insert series to temp table: {}".format(err))
        return False

def insert_price_into_tmp(cursor, data_vendor, row, prices):
    try:
        data = []
        sql  = sql_insert_timepoint_tmp2

        for index, price in prices.iterrows():
            
            data.append((data_vendor["id"], row["exchange_id"], row["ticker"],
                util.format_date(index), 
                float(price["Open"]), float(price["High"]), float(price["Low"]), 
                float(price["Close"]), float(price["Adj Close"]), int(price["Volume"])))

            if len(data) > 500:
                cursor.executemany(sql, data)
                data = []

        if len(data) > 0:
            cursor.executemany(sql, data)
        
        return True
    except Exception as err:
        print("Failed to insert price to temp table: {}".format(err))
        return False

def merge_series_into_tmp(cursor):
    try:
        cursor.execute(sql_merge_series)
        return True
    except Exception as err:
        print("Failed to merge temp table to series table: {}".format(err))
        return False

def merge_price_into_tmp(cursor):
    try:
        cursor.execute(sql_populate_price_tmp_series_id)
        cursor.execute(sql_merge_price)
        return True
    except Exception as err:
        print("Failed to merge temp table to price table: {}".format(err))
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

def fetch_data(exchange, symbol, price_start_date):
    """
    return series info and also price data from start_date to now
    """
    try:
        ticker = util.get_yahoo_ticker(exchange, symbol)
        start_date_str = util.format_date(price_start_date)
        end_date_str = util.format_date(datetime.datetime.now())
        info = yf.Ticker(ticker).info
        data = yf.download(ticker, start=start_date_str, end=end_date_str)

        return info, data, True
    except Exception as err:
        print("Failed download data from Yahoo: {}".format(err))
        return None, None, False

def fetch_data_test(exchange, symbol, price_start_date):
    with open('info.pickle', 'rb') as handle:
        info = pickle.load(handle)

    with open('data.pickle', 'rb') as handle:
        data = pickle.load(handle)

    return info, data, True


def drop_table(cursor):
    try:
        sql = sql_drop_series_tmp_table
        cursor.execute(sql)

        sql = sql_drop_price_tmp_table
        cursor.execute(sql)

        return True
    except Exception as err:
        print("Failed recording message: {}".format(err))
        return False

def get_vendor(cursor, vendor_name):
    sql = sql_select_vendor.format(name = vendor_name)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0], True
    except Exception as err:
        print("Failed to get data vendor: {}".format(err))
        return None, False

def mark_record_processed(cursor, row):
    sql = sql_mark_processed
    try:
        cursor.execute(sql, (row["exchange"], row["ticker"]))
        return True
    except Exception as err:
        print("Failed to mark record processed: {}".format(err))
        return False

def run_job():

    mydb = None
    cursor = None

    try: 
        mydb = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        cursor = mydb.cursor(dictionary=True)

        rows, success = get_not_yet_processed(cursor)
        if not success:
            sys.exit(1)

        data_vendor, success = get_vendor(cursor, "Yahoo")
        if not success:
            sys.exit(1)

        success = create_tmp_table(cursor)
        if not success:
            sys.exit(1)

        queue = []

        for row in rows:
            queue.append((row, 0))

        while queue:
            u = queue.pop(0)
            row = u[0]
            retry = u[1]
            exchange_name = row["exchange"]
            ticker = row["ticker"]
            info, prices, success = fetch_data(row["exchange"], row["ticker"], row["start_date"])

            if success: 
                last_price_date = prices.index.max()
                success = insert_series_into_tmp(cursor, row, info, last_price_date)
                if not success:
                    message = f"Failed to insert symbol to tmp table: {exchange_name}-{ticker}"
                    log_message(cursor, message)
                    print(message)
                    continue

                success = insert_price_into_tmp(cursor, data_vendor, row, prices)
                if not success:
                    message = f"Failed to insert price into tmp table: {exchange_name}-{ticker}"
                    log_message(cursor, message)
                    print(message)

                mark_record_processed(cursor, row)
                mydb.commit()

            else:
                if retry < 3:
                    print("Failed to load data from Yahoo. Retry: " + retry)
                    queue.append((row, retry+1))
                else:
                    print("Failed to load data from Yahoo.")

        success = merge_series_into_tmp(cursor)
        if not success:
            sys.exit(1)

        success = merge_price_into_tmp(cursor)
        if not success:
            sys.exit(1)

        mydb.commit()

        drop_table(cursor)
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
    
    run_job()