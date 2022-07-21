from attr import dataclass
import config as config
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
# rank the data according to following
# month: 1/2
# price: 5/10
# order by iv, iv diff, oi, oi diff
# show top 10, 20, 50

import mysql.connector

mydb = mysql.connector.connect(
  host=config.DB_HOST,
  user=config.DB_USER,
  password=config.DB_PASSWORD,
  database=config.DB_NAME
)



# query
sql_query = """select s.ticker, s.name, cast(p.close_price as float) as close,
cast(m.strike_price as float) strike, date_format(m.expiry, "%Y-%m") as expiry, m.type, 
cast(p2.iv as float) as iv, p2.open_interest from option_meta_data m 
inner join symbol s on (s.exchange_id=1 and s.ticker=m.underlying_asset_ticker)
inner join daily_price p on (s.id = p.symbol_id and p.price_date = s.last_price_date)
left join symbol s2 on (s2.id = m.symbol_id)
left join daily_price p2 on (p2.symbol_id = s2.id)
where
m.expiry between '{query_date}' and '{end_date}' and
m.strike_price between p.close_price * {lower_price} and p.close_price * {upper_price} and
p2.open_interest >= 20 and
p2.price_date='{query_date}' and
p2.volume > 0
order by p2.{order_by} desc
limit {records_cnt}
"""


def query_result(query_date, price_range, expiry_range, order_by, cnt):
    mycursor = mydb.cursor(dictionary=True)

    upper_price = 1+price_range/100
    lower_price = 1-price_range/100

    if order_by == 'IV':
        order= 'iv'
    else:
        order='open_interest'

    end_date = query_date+timedelta(days=expiry_range*31)

    sql = sql_query.format(query_date = query_date, end_date= end_date, lower_price = lower_price, upper_price=upper_price,
        order_by = order, records_cnt=cnt)
    mycursor.execute(sql)
    data = mycursor.fetchall()
    #print(data)

    df = pd.DataFrame.from_dict(data)
    #df.columns = mycursor.keys()

    st.write(df)


st.markdown("## 香港期權排序")
st.sidebar.markdown("香港期權排序")


form= st.form("my_form")
date = form.date_input(label="date")

c1, c2 = form.columns(2)

order_by= c1.selectbox("Sort by", ["IV", "Open Interest"], key='order_by')
price_range= c2.selectbox("Price range", [5,10, 15], key='price_range')

c3, c4 = form.columns(2)
expiry_range = c3.selectbox("Expiry range", [1, 2], key='expiry_range')

cnt = c4.selectbox("Recods", [10, 20, 50, 100])

submitted = form.form_submit_button("Submit")
if submitted:
    query_result(date, price_range, expiry_range, order_by, cnt)



