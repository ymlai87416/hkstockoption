import yfinance as yf
import util
import datetime
import pickle

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

def fetch_data(exchange, symbol, price_start_date):
    """
    return series info and also price data from start_date to now
    """
    try:
        ticker = get_yahoo_ticker(exchange, symbol)
        start_date_str = util.format_date(price_start_date)
        end_date_str = util.format_date(datetime.datetime.now())
        info = yf.Ticker(ticker).info
        data = yf.download(ticker, start=start_date_str, end=end_date_str)

        return info, data, True
    except Exception as err:
        print("Failed download data from Yahoo: {}".format(err))
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
    
    main()