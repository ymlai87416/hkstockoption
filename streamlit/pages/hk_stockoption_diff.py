import config_debug as config
import streamlit as st

def read_open_interest(stock, date):
    # read from database
    sql = """
    """

    # order the data
    pass

def read_iv(stock):
    sql = """select * from time_series_point where time_series_id in 
        (select id from time_series where series_name= 'XXXXX')
    """
    pass

def show_iv(data):
    pass

def read_stock_price(stock):
    # read the stock price for last 3 months
    pass

def hk_stockoption_diff(stock, start_date, end_date):
    df_start = read_open_interest(stock, start_date)
    df_end = read_open_interest(stock, end_date)
    df_stock_price = read_stock_price(stock)
    df_iv = read_iv(stock)
    st.write(df_stock_price)
    st.write(df_iv)
    df_final = df_end - df_start
    st.write(df_final)

def read_avail_stock():
    pass

def hk_stock_option_page():
    st.markdown("香港期權分析")

    with st.form("my_form"):
        stock = st.text_input("股票", key='stock')
        d = st.date_range("時段", value= (), key='daterange')

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            hk_stockoption_diff(stock, d[0], d[1])


