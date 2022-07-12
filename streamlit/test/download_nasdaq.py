
import requests
from datetime import datetime
import pandas as pd
import math
import logging

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)

# download option price using the API
# limit (default = 60), offset (default = 60)
# from date and to date format are YYYY-MM-DD
price_api = "https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass=stocks&limit={limit}&offset={offset}&fromdate={from_date}&todate={to_date}&excode=oprac&callput=callput&money=at&type=all"
price_api2 = "https://api.nasdaq.com/api/quote/{symbol}/option-chain?assetclass=stocks&limit={limit}&offset={offset}&excode=oprac&callput=callput&money=at&type=all"

# download option geek using the API
# date in the format of YYYY-MM-DD
greek_api = "https://api.nasdaq.com/api/quote/{symbol}/option-chain/greeks?assetclass=stocks&date={date}"
greek_api2 = "https://api.nasdaq.com/api/quote/{symbol}/option-chain/greeks?assetclass=stocks"

date_format = "%Y-%m-%d"
option_date_list = []
greek_date_list = []

def get_option_date_list():
    return option_date_list

def get_greek_date_list():
    return greek_date_list

def set_option_date_list(data):
    option_date_list.clear()
    for rec in data["filter"]:
        if rec["label"] == "All": 
            continue;
        date = datetime.strptime(rec["label"],"%B %Y") 
        dates = rec["value"].split("|")
        start_date = datetime.strptime(dates[0],"%Y-%m-%d") 
        end_date = datetime.strptime(dates[1],"%Y-%m-%d") 
        option_date_list.append([date, start_date, end_date])

def set_greek_date_list(data):
    for rec in data["data"]["filters"]:
        date = datetime.strptime(rec["value"],"%Y-%m-%d") 
        greek_date_list.append(date)

def try_float(str, default= 0):
    try:
        return float(str)
    except:
        return default

def download_option_price(symbol, start_date, end_date, limit=60, offset=0):
    url = ""
    if start_date is None or end_date is None :
        url = price_api2.format(symbol = symbol, limit = limit, offset = offset) 
    else:
        start_date_str = start_date.strftime(date_format)
        end_date_str = end_date.strftime(date_format)
        url = price_api.format(symbol = symbol, limit = limit, offset = offset, start_date = start_date_str, end_date = end_date_str)

    logging.info('Download option price from url: ' + url)
    headers = {"Connection": "close", 
            "Accept-Language":"en-US,en;q=0.9",
            "Accept-Encoding":"gzip, deflate, br",
            "User-Agent":"Java-http-client/"}
    r = requests.get(url, timeout=5, headers=headers)
    
    res = r.json()

    set_option_date_list(res["data"]["filterlist"]["fromdate"])

    logging.info('Successful set option date.')

    no_of_record = res["data"]["totalRecord"]
    df_column = ["Exp. Date", "Call Last", "Call Change", "Call Bid", "Call Ask", "Call Volume", "Call Open Int."
        , "Strike", "Put Last", "Put Change", "Put Bid", "Put Ask", "Put Volume", "Put Open Int."]

    rec_date_format = "%b %d"

    data = []

    if start_date == None:
        start_date = option_date_list[0][1]
        end_date = option_date_list[0][2]

    #print("DD")
    # print(res)
    for rec in res["data"]["table"]["rows"]:
        try:
            if rec["expiryDate"] is None:
                continue
            expiry_date = datetime.strptime(rec["expiryDate"],rec_date_format)
            expiry_date = expiry_date.replace(year=start_date.year)
            call_last = try_float(rec["c_Last"])
            call_change = try_float(rec["c_Change"])
            call_bid = try_float(rec["c_Bid"])
            call_ask = try_float(rec["c_Ask"])
            call_volume = try_float(rec["c_Volume"])
            call_open_int = try_float(rec["c_Openinterest"])
            strike = try_float(rec["strike"])
            put_last = try_float(rec["p_Last"])
            put_change = try_float(rec["p_Change"])
            put_bid = try_float(rec["p_Bid"])
            put_ask = try_float(rec["p_Ask"])
            put_volume = try_float(rec["p_Volume"])
            put_open_int = try_float(rec["p_Openinterest"])
            data.append([expiry_date, call_last, call_change, call_bid, call_ask, call_volume, call_open_int,
                strike, put_last, put_change, put_bid, put_ask, put_volume, put_open_int])
        except Exception as err:
            logging.error(str(rec), err)

    df_record = pd.DataFrame(data, columns=df_column)

    logging.info('Successful convert json to pandas frame.')

    return no_of_record, df_record

def download_greek_api(symbol, date):

    url = ""
    if date is None:
        url = greek_api2.format(symbol = symbol)
    else:
        date_str =  date.strftime(date_format)
        url = greek_api.format(symbol = symbol, date = date_str)

    logging.info('Download option greek from url: ' + url)

    headers = {"Connection": "close", 
            "Accept-Language":"en-US,en;q=0.9",
            "Accept-Encoding":"gzip, deflate, br",
            "User-Agent":"Java-http-client/"}
    r = requests.get(url, timeout=5, headers=headers)
    res = r.json()

    df_column = [ "Exp. Date", "Call DELTA", "Call GAMMA", "Call RHO", "Call THETA", "Call VEGA", "Call IV", 
        "STRIKE", "Put DELTA", "Put GAMMA", "Put RHO", "Put THETA", "Put VEGA", "Put IV"]
    set_greek_date_list(res)
    if date is None:
        date = greek_date_list[0]

    data = []
    for rec in res["data"]["table"]["rows"]: 
        call_delta = try_float(rec["cDelta"])
        call_gamma = try_float(rec["cGamma"])
        call_rho = try_float(rec["cRho"])
        call_theta = try_float(rec["cTheta"])
        call_vega = try_float(rec["cVega"])
        call_iv = try_float(rec["cIV"])
        strike = try_float(rec["strike"])
        put_delta = try_float(rec["pDelta"])
        put_gamma = try_float(rec["pGamma"])
        put_rho = try_float(rec["pRho"])
        put_theta = try_float(rec["pTheta"])
        put_vega = try_float(rec["pVega"])
        put_iv = try_float(rec["pIV"])
        data.append( [date, call_delta, call_gamma, call_rho, call_theta, call_vega, call_iv,
            strike, put_delta, put_gamma, put_rho, put_theta, put_vega, put_iv] )
    df_record = pd.DataFrame(data, columns=df_column)

    return df_record

def merge_data(symbol, df_option, df_greek):
    """
    Output format will include the following fields
    df.columns = ['ExpirationDate','Calls','CallLastSale','CallNet','CallBid','CallAsk','CallVol',
              'CallIV','CallDelta','CallGamma','CallOpenInt','StrikePrice','Puts','PutLastSale',
              'PutNet','PutBid','PutAsk','PutVol','PutIV','PutDelta','PutGamma','PutOpenInt']
    """
    data = []
    df_column = ['ExpirationDate','Calls','CallLastSale','CallNet','CallBid','CallAsk','CallVol',
              'CallIV','CallDelta','CallGamma','CallOpenInt','StrikePrice','Puts','PutLastSale',
              'PutNet','PutBid','PutAsk','PutVol','PutIV','PutDelta','PutGamma','PutOpenInt']

    for index, row in df_option.iterrows():
        #print("DD")
        #print(row)
        exp_date = row["Exp. Date"]
        strike_price = row["Strike"]
        row_greek = df_greek[((df_greek.STRIKE == strike_price) & (df_greek["Exp. Date"] == exp_date)) ].iloc[0]
        call_iv = row_greek["Call IV"]
        call_delta = row_greek["Call DELTA"]
        call_gamma = row_greek["Call GAMMA"]
        put_iv = row_greek["Put IV"]
        put_delta = row_greek["Put DELTA"]
        put_gamma = row_greek["Put GAMMA"]

        call_option_name = get_option_name(symbol, exp_date, "C", strike_price)
        put_option_name = get_option_name(symbol, exp_date, "P", strike_price)

        data.append( [exp_date, call_option_name, row["Call Last"], row["Call Change"],
            row["Call Bid"], row["Call Ask"], row["Call Volume"], call_iv, call_delta, call_gamma
            , row["Call Open Int."], strike_price, put_option_name, row["Put Last"]
            , row["Put Change"], row["Put Bid"], row["Put Ask"], row["Put Volume"], put_iv, put_delta, put_gamma, row["Put Open Int."]] )

    df_final = pd.DataFrame(data, columns=df_column)

    return df_final

def get_option_name(symbol, exp_date, type, strike_price):
    #SPXW220708C03885000 
    #amd---220729c00081000
    date_str = exp_date.strftime("%y%m%d")
    price_decimal, price_int  =math.modf(strike_price) 
    price_decimal = int(price_decimal * 1000)
    price_int = int(price_int)

    name = '{}{}{}{:0>5d}{:0>3d}'.format(symbol, date_str, type, price_int, price_decimal)
    return name

def main():
    symbol = "AMD"
    # get all the option record for this month
    offset = 0
    df_final = None
    while True:
        n_rect, df = download_option_price(symbol, None, None, limit=60, offset=offset)
        if df_final is None:
            df_final = df
        else:
            df_final = pd.concat([df_final, df])

        print("Progress {}/{}".format(len(df_final), n_rect))
        if offset + 60 < n_rect:
            offset+=60
        else:
            break

    print("Download stock option price for current month finished")
    print(df_final.head())

    df_final.to_csv("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/data/" + "option_price.csv")

    # now we have all the distinct the date and get all option greek
    dates = df_final["Exp. Date"].unique()
    #df_greek_dict = {}
    df_greek_final = None
    for d in dates:
        d = pd.to_datetime(d)
        df_greek = download_greek_api(symbol, d)
        #df_greek_dict[d] = df_greek
        if df_greek_final is None:
            df_greek_final = df_greek
        else:
            df_greek_final = pd.concat([df_greek_final, df_greek])
        
    print("Downloaded option greek data")
    print(df_greek_final.head())

    df_greek_final.to_csv("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/data/" + "option_greek.csv")

    df_result = merge_data(symbol, df_final, df_greek_final) 
    
    print("Successfully merge option price with greek data")
    print(df_result.head())

    df_result.to_csv("/Users/yiuminglai/GitProjects/hkstockoption/streamlit/test/data/" + "job_input.csv")

    return df_result

if __name__ == "__main__":
    main()