import streamlit as st
from streamlit_option_menu import option_menu

st.title("Final project Python Candlestick Graph")

add_multiselect = st.multiselect("Chose the following available coins",
    ("Bitcoin" , "Ethereum", "Tether", "USD Coin", "Binance Coin")
)

go_button = st.button("Go")


if add_multiselect == "Bitcoin":
    st.write("Display Bitcoin information or candlestick chart here")
    # You can add more detailed information or a candlestick chart for Bitcoin
elif add_multiselect == "Ethereum":
    st.write("Display Ethereum information or candlestick chart here")
    # You can add more detailed information or a candlestick chart for Ethereum

elif add_multiselect == "Tether":
    st.write("Display Tether information or candlestick chart here")

elif add_multiselect == "USD Coin":
    st.write("Display USD Coin information or candlestick chart here")

elif add_multiselect == "Binance Coin":
    st.write("Display Binance Coin information or candlestick chart here")

else:
    print("Please chose an appropiate Coin")

#  Home button
if st.button("Home"):
    st.write("You clicked on the Home button!")


