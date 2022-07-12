import yfinance as yf
import util
import datetime
import pickle
import sys
import os

#msft = yf.Ticker("MSFT")
# get stock info
#print(msft.info)

#hsbc = yf.Ticker("0005.HK")

#print(hsbc.info)
def get_yahoo_ticker(exchange, symbol):
    if(exchange["abbrev"] == "HKEX"):
        return symbol+".HK"
    else:
        return symbol

def fetch_data(exchange, symbol, price_start_date, price_end_date):
    """
    return series info and also price data from start_date to now
    """
    try:
        ticker = util.get_yahoo_ticker(exchange["abbrev"], symbol)
       
        start_date_str = util.format_date(price_start_date)
        end_date_str = util.format_date(price_end_date)

        print(start_date_str + " " + end_date_str)

        info = yf.Ticker(ticker).info
        data = yf.download(ticker, start=start_date_str, end=end_date_str)

        return info, data, True
    except Exception as err:
        print("Failed download data from Yahoo: {}".format(err))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return None, None, False


def save_object(info, data):
    with open('info.pickle', 'wb') as handle:
        pickle.dump(info, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('data.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_object():
    with open('info.pickle', 'rb') as handle:
        info = pickle.load(handle)

    with open('data.pickle', 'rb') as handle:
        data = pickle.load(handle)

    return info, data, True

def main():
    exchange = {"abbrev": "HKEX"}
    info, data, success = fetch_data(exchange, "0005", datetime.datetime(2010, 1, 1))
    if not success:
        print("Cannot load from yahoo")
        return

    save_object(info, data)
    info2, data2, success = load_object()
    if not success:
        print("Failed to load from pickle")
        return

    print(info2)
    print(data2)

if __name__ == '__main__':
    hkex = {"abbrev": "HKEX"}
    info, data, success = fetch_data(hkex, '00700', datetime.datetime(2022,7,1), datetime.datetime(2022,7,6))
    print(data)