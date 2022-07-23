import random
import string

def get_batch_id():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

def format_date(date):
    return date.strftime("%Y-%m-%d")

def format_datetime(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

def get_yahoo_ticker(exchange, symbol):
    # include HKEX, NASDAQ, NYSE, CRYPTO
    if(exchange == "HKEX"):
        return (str(symbol)[1:])+".HK"
    else: 
        return str(symbol)