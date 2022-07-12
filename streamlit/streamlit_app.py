import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.markdown("# Welcome to My data analyze page!")

    st.sidebar.success("Select a function above.")

    st.markdown("""
    ## HK option compare diff
    Compare the difference on open interest of stock option to have an idea of the future direction.

    Not yet implemented.

    For details, please visit https://trade.ymlai87416.com/hkstockoption/#/option-details

    ## SPX option gamma
    Very funny insight from this page: https://perfiliev.co.uk/market-commentary/how-to-calculate-gamma-exposure-and-zero-gamma-level/?utm_source=pocket_mylist
    
    An hourly job is running to fetch SPX option data from CBOE 
    """)


if __name__ == "__main__":
    run()