from attr import dataclass
import config as config
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

import mysql.connector

mydb = mysql.connector.connect(
  host=config.DB_HOST,
  user=config.DB_USER,
  password=config.DB_PASSWORD,
  database=config.DB_NAME
)


sql_query="""select d1.ticker, d1.name, 
cast(d1.close_price as float) as close, d1.opt_ticker, 
cast(d1.strike_price as float) as strike, 
cast(d1.iv as float) as to_iv, 
cast(d2.iv as float) as from_iv,
cast(d1.iv-d2.iv as float) as iv_diff, d1.open_interest-d2.open_interest from 
(select s2.id, s.ticker, s.name, p.close_price, s2.ticker as opt_ticker, m.strike_price,p2.iv, p2.open_interest from option_meta_data m 
inner join symbol s on (s.exchange_id=1 and s.ticker=m.underlying_asset_ticker)
inner join daily_price p on (s.id = p.symbol_id and p.price_date = '{to_date}')
left join symbol s2 on (s2.id = m.symbol_id)
left join daily_price p2 on (p2.symbol_id = s2.id)
where
m.expiry between '{expiry_from}' and '{expiry_to}' and
m.strike_price between p.close_price * {lower_price} and p.close_price * {upper_price} and
p2.price_date='{to_date}' and
p2.volume > 0 and
p2.open_interest >= 20) as d1
inner join
(select s2.id, s.ticker, s.name, p.close_price, s2.ticker as opt_ticker, m.strike_price, p2.iv, p2.open_interest  from option_meta_data m 
inner join symbol s on (s.exchange_id=1 and s.ticker=m.underlying_asset_ticker)
inner join daily_price p on (s.id = p.symbol_id and p.price_date ='{from_date}')
left join symbol s2 on (s2.id = m.symbol_id)
left join daily_price p2 on (p2.symbol_id = s2.id)
where
m.expiry between '{expiry_from}' and '{expiry_to}' and
m.strike_price between p.close_price * {lower_price} and p.close_price * {upper_price} and
p2.price_date='{from_date}' ) as d2 on (d1.id = d2.id)
order by {order_by} desc 
limit {record_count}
"""

def query_result(from_date, to_date, price_range, expiry_range, order_by, cnt):
    mycursor = mydb.cursor(dictionary=True)

    upper_price = 1+price_range/100
    lower_price = 1-price_range/100

    if order_by == 'IV':
        order= 'd1.iv'
    else:
        order='d1.iv-d2.iv'

    expiry_from = to_date
    expiry_to = to_date+timedelta(days=expiry_range*31)

    sql = sql_query.format(from_date = from_date, to_date = to_date, expiry_from=expiry_from, 
        expiry_to=expiry_to, lower_price = lower_price, upper_price=upper_price,
        order_by = order,  record_count=cnt)
    mycursor.execute(sql)
    data = mycursor.fetchall()
    #print(data)

    df = pd.DataFrame.from_dict(data)
    #df.columns = mycursor.keys()

    st.write(df)

st.markdown("## 香港期權變化")
st.sidebar.markdown("香港期權變化")


form= st.form("my_form")
c5, c6 = form.columns(2)
from_date = c5.date_input(label="from_date")
to_date = c6.date_input(label="to_date")

c1, c2 = form.columns(2)

order_by= c1.selectbox("Sort by", ["IV diff", "IV"], key='order_by')
price_range= c2.selectbox("Price range", [5,10, 15], key='price_range')

c3, c4 = form.columns(2)
expiry_range = c3.selectbox("Expiry range", [1, 2], key='expiry_range')

cnt = c4.selectbox("Recods", [10, 20, 50, 100])


submitted = form.form_submit_button("Submit")
if submitted:
    
    
    query_result(from_date, to_date, price_range, expiry_range, order_by, cnt)





