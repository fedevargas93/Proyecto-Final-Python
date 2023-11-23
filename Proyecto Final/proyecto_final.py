import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Function to fetch OHLC data
def fetch_ohlc_data(pair):
    url_ohlc = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval=60"
    response = requests.get(url_ohlc)
    if response.status_code == 200:
        result = response.json().get("result", {})
        if result and list(result.keys()) and len(result[list(result.keys())[0]]) > 0:
            ohlc = pd.DataFrame(result[list(result.keys())[0]],
                                columns=["datetime", "open", "high", "low", "close", "vwap", "volume", "count"])
            ohlc = ohlc.astype(
                {'open': float, 'high': float, 'low': float, 'close': float, 'vwap': float, 'volume': float})
            ohlc.index = pd.to_datetime(ohlc["datetime"], unit='s')
            return ohlc
        else:
            st.warning("No valid data available for the selected cryptocurrency pair.")
            return None
    else:
        st.warning("Error in API response. Please try again.")
        return None

# Function to calculate Stochastic Oscillator values
def calculate_stochastic_oscillator(ohlc):
    # Calculate %K and %D
    ohlc['low_min'] = ohlc['low'].rolling(window=14).min()
    ohlc['high_max'] = ohlc['high'].rolling(window=14).max()

    ohlc['%K'] = (ohlc['close'] - ohlc['low_min']) / (ohlc['high_max'] - ohlc['low_min']) * 100
    ohlc['%D'] = ohlc['%K'].rolling(window=3).mean()

    # Drop temporary columns used in calculations
    ohlc.drop(['low_min', 'high_max'], axis=1, inplace=True)

    return ohlc

st.title("Final project Python Candlestick Graph")

add_multiselect = st.multiselect(
    "Choose the following available coins",
    ("Bitcoin", "Ethereum", "Tether", "USD Coin")
)

go_button = st.button("Go")

# Dictionary to map the selected cryptocurrency to its corresponding pair:
pair_mapping = {
    "Bitcoin": "XBTUSD",
    "Ethereum": "ETHUSD",
    "Tether": "USDTUSD",
    "USD Coin": "USDCUSD",
}

# Fetch OHLC data for selected cryptocurrencies
ohlc_data = {}
if go_button:
    for crypto in add_multiselect:
        selected_pair = pair_mapping.get(crypto)
        if selected_pair:
            ohlc_data[crypto] = fetch_ohlc_data(selected_pair)
            # Calculate stochastic oscillator values
            ohlc_data[crypto] = calculate_stochastic_oscillator(ohlc_data[crypto])

# Create separate Figure objects for Candlestick Chart and Stochastic Oscillator
candlestick_fig = go.Figure()
stochastic_fig = go.Figure()

# Visualization of a candlestick chart for the selected cryptocurrencies
for crypto, ohlc in ohlc_data.items():
    candlestick_fig.add_trace(go.Candlestick(
        x=ohlc.index,
        open=ohlc['open'],
        high=ohlc['high'],
        low=ohlc['low'],
        close=ohlc['close'],
        name=f"{crypto} - {ohlc.index[0].strftime('%Y-%m-%d')} to {ohlc.index[-1].strftime('%Y-%m-%d')}"
    ))
    # Check if %K and %D columns are present before adding traces
    if '%K' in ohlc.columns and '%D' in ohlc.columns:
        # Add stochastic oscillator traces to the separate figure
        stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['%K'], name=f"%K - {crypto}", line=dict(color='#ff9900', width=2)))
        stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['%D'], name=f"%D - {crypto}", line=dict(color='#000000', width=2)))

# Customize the layout for Candlestick Chart
candlestick_fig.update_layout(
    title=f'Candlestick chart for {add_multiselect[0]} and {add_multiselect[1]}',
    xaxis_title='Date',
    yaxis_title='Price',
    template='plotly_dark'
)

# Customize the layout for Stochastic Oscillator
stochastic_fig.update_layout(
    title=f'Stochastic Oscillator for {add_multiselect[0]} and {add_multiselect[1]}',
    xaxis_title='Date',
    yaxis_title='Value',
    template='plotly_dark'
)

# Display the charts
st.plotly_chart(candlestick_fig)
st.plotly_chart(stochastic_fig)

# Display other relevant information
for crypto, ohlc in ohlc_data.items():
    st.subheader(f'OHLC Data for {crypto}')
    st.write(ohlc)

# Home button
if st.button("Home"):
    st.write("You clicked on the Home button!")
