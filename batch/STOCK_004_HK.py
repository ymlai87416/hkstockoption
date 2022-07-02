import sys
import util
import datetime
import config
import mysql.connector
import requests
import csv
import pandas as pd
import os

sql_create_tmp_table = """create table iv_timepoint_tmp(
    series_name varchar(255) NOT NULL,
    series_id bigint NULL,
	time_point_date datetime NOT NULL,
	`value` decimal(19,4) NULL
)
"""

sql_read_hk_stock_iv = "select distinct ticker from hk_option_list"

sql_insert_into_tmp_table2 = """
insert into iv_timepoint_tmp values
({series_id}, {timepoint_date}, {value}, {created_date}, {last_updated_date})
"""

sql_insert_into_tmp_table = """
insert into iv_timepoint_tmp
(series_name, time_point_date, `value`) 
values (%s, %s, %s)
"""


sql_fill_series_id_temp_table = """update iv_timepoint_tmp t 
inner join time_series ts on (t.series_name = ts.series_name)
set t.series_id = ts.id
"""

sql_insert_new_series_to_main = """insert into time_series 
(version, series_name, category, created_date, last_updated_date)
select 1, a.series_name, 'HK STOCK IV', now(), now() from 
    (select distinct series_name from iv_timepoint_tmp t where t.series_id is NULL) a
"""

sql_merge_into_main_table = """insert into time_point( 
version, series_id, time_point_date, value, created_date, last_updated_date
)
select 1, series_id, time_point_date, value, now(), now() 
    from iv_timepoint_tmp
ON DUPLICATE KEY UPDATE
  last_updated_date  = VALUES(last_updated_date),
  value = VALUES(value),
  version = version+1
"""

sql_drop_tmp_table = "drop table iv_timepoint_tmp"

sql_insert_log_message = """insert into log_message 
values
('{category}', '{message}', '{create_date}')
"""

log_header = "HK STOCK IV"

df_url = "http://www.hkex.com.hk/eng/sorc/options/statistics_hv_iv.aspx?action=csv&type=3&ucode={symbol}";

def get_datafile_url(symbol):
    """
    symbol: pass int 5 digit ticker. e.g. 00001
    """
    return df_url.format(symbol)

def get_series_name(symbol, series_name):
    """
    series_name can be iv, hv_10, hv_30, hv_60, hv_90
    """
    return symbol + " " + series_name

def download_data(symbol):
    try:
        csv_url = df_url.format(symbol = symbol)
        with requests.Session() as s:
            download = s.get(csv_url)

            decoded_content = download.content.decode('utf-8')

            df, success = readfile(decoded_content.splitlines())

        return df, success
    except Exception as err:
        print("Failed to download data from HKEx: {}".format(err))
        return None, False

def readfile(linesep):
    #f = open("../db/job/4 hk stock option iv/statistics_hv_iv.csv", "r", encoding='UTF-8')
    #linesep = f.readlines()
    state = 0
    header = "Trading date, IV (%), HV10 (%), HV30 (%), HV60 (%), HV90 (%)"
    
    df = pd.DataFrame(columns=["Trading date", "IV (%)", "HV10 (%)", "HV30 (%)", "HV60 (%)", "HV90 (%)"])
    data_list = []
    cnt = 0
    
    for line in linesep:
        line = line.strip()
        cnt += 1

        if state == 0:
            if line == header:
                state = 1
                continue

        if state == 1:
            dd = line.split(",")
            #print("x" + dd[0])
            t_date = datetime.datetime.strptime(dd[0], '%d/%m/%Y')
            data = {"Trading date": t_date ,"IV (%)" : dd[1], "HV10 (%)": dd[2],
                "HV30 (%)": dd[3],"HV60 (%)": dd[4],"HV90 (%)": dd[5]}
            data_list.append(data)

    df = df.append(data_list, ignore_index=True)

    return df, True


def read_hk_iv_series(cursor):
    sql = sql_read_hk_stock_iv
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result, True
    except Exception as err:
        print("Failed to read stock option summary table: {}".format(err))
        return None, False

def create_tmp_table(cursor):
    sql = sql_create_tmp_table
    try:
        cursor.execute(sql)
        return True
    except mysql.connector.Error as err:
        print("Failed creating temp table: {}".format(err))
        return False

def insert_into_tmp_table(cursor, ticker, df):
    try:
        data = [] 
        for _, row in df.iterrows():
            series_name_iv =get_series_name(ticker, "IV")
            series_name_hv10 =get_series_name(ticker, "HV10")
            series_name_hv30 =get_series_name(ticker, "HV30")
            series_name_hv60 =get_series_name(ticker, "HV60")
            series_name_hv90 =get_series_name(ticker, "HV90")
            date_str = util.format_date(row["Trading date"])

            data.append((series_name_iv, date_str, row["IV (%)"]))
            data.append((series_name_hv10, date_str, row["HV10 (%)"]))
            data.append((series_name_hv30, date_str, row["HV30 (%)"]))
            data.append((series_name_hv60, date_str, row["HV60 (%)"]))
            data.append((series_name_hv90, date_str, row["HV90 (%)"]))

        cursor.executemany(sql_insert_into_tmp_table, data)

        return True
    except Exception as err:
        print("Failed inserting record to temp table: {}".format(err))
        return False

def merge_data_main_table(cursor):
    try:
        sql = sql_fill_series_id_temp_table
        cursor.execute(sql)

        sql = sql_insert_new_series_to_main
        cursor.execute(sql)

        sql = sql_fill_series_id_temp_table
        cursor.execute(sql)

        sql = sql_merge_into_main_table
        cursor.execute(sql)

        return True
    except Exception as err:
        print("Failed to merge data from tmp table to main table: {}".format(err))
        print("Error SQL: " + sql)
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
        curtime = datetime.datetime.now()
        sql = sql_insert_log_message.format(
            category = log_header, message = message, 
            create_date = util.format_datetime(curtime)
            )
        cursor.execute(sql)
        return True
    except Exception as err:
        print("Failed recording message: {}".format(err))
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

        success = create_tmp_table(cursor)
        if not success:
            sys.exit(1)

        iv_series_list, success = read_hk_iv_series(cursor)
        if not success:
            sys.exit(1)

        queue = []

        for iv_series in iv_series_list:
            queue.append((iv_series["ticker"], 0))
        
        cc = 0

        while queue:
            (symbol, retry) = queue.pop(0)
            cc += 1

            #if cc > 5:
            #    break

            data, success = download_data(symbol)
            #print("xx" + str(symbol))
            #print(data)

            if success: 
                success = insert_into_tmp_table(cursor, symbol, data)

                if not success:
                    message = f"Failed to insert data: {symbol}"
                    log_message(cursor, message)
                    print(message)
                else:
                    print(f"success: {symbol}")
                mydb.commit()
            else:
                if retry < 3: 
                    queue.append((symbol, retry+1))
                else:
                    message = f"Failed to download data for symbol: {symbol}"
                    log_message(cursor, message)
                    print(message)

        success = merge_data_main_table(cursor)
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

    run_job()