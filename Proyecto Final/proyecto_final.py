import requests
import pandas as pd
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

    # Add overbought and oversold indicators
    ohlc['Overbought'] = 80
    ohlc['Oversold'] = 20

    # Drop temporary columns used in calculations
    ohlc.drop(['low_min', 'high_max'], axis=1, inplace=True)

    return ohlc

# Function to calculate Moving Average
def calculate_moving_average(ohlc, window):
    ohlc['MA'] = ohlc['close'].rolling(window=window).mean()
    return ohlc

# Set up the layout with buttons and dropdown in a panel on the left
menu_container = st.sidebar.container()
menu_container.subheader("Welcome to the Candlestick Graph Viewer App!")

add_multiselect = menu_container.multiselect(
    "Choose the following available coins",
    ("Bitcoin", "Ethereum", "Tether", "USD Coin")
)

go_button = menu_container.button("Go")

# Dictionary to map the selected cryptocurrency to its corresponding pair:
pair_mapping = {
    "Bitcoin": "XXBTZUSD",
    "Ethereum": "XETHZUSD",
    "Tether": "USDTZUSD",
    "USD Coin": "USDCZUSD",
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
            # Calculate moving average with a window of 10
            ohlc_data[crypto] = calculate_moving_average(ohlc_data[crypto], window=10)

# Create separate Figure objects for Candlestick Chart, Stochastic Oscillator, and Moving Average
candlestick_fig = go.Figure()
stochastic_fig = go.Figure()
ma_fig = go.Figure()

# Visualization of a candlestick chart for the selected cryptocurrencies
for crypto, ohlc in ohlc_data.items():
    candlestick_fig.add_trace(go.Candlestick(
        x=ohlc.index,
        open=ohlc['open'],
        high=ohlc['high'],
        low=ohlc['low'],
        close=ohlc['close'],
        name=f"{crypto} - {ohlc.index[0].strftime('%Y-%m-%d')} to {ohlc.index[-1].strftime('%Y-%m-%d')}",
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

# Visualization of a Stochastic Oscillator for the selected cryptocurrencies
for crypto, ohlc in ohlc_data.items():
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['%K'], name=f"%K - {crypto}", line=dict(color='#ff9900', width=2)))
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['%D'], name=f"%D - {crypto}", line=dict(color='#000000', width=2)))
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['Overbought'], name="Overbought", line=dict(color='red', width=1), fill='tozeroy'))
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['Oversold'], name="Oversold", line=dict(color='green', width=1), fill='tozeroy'))

# Visualization of a Moving Average for the selected cryptocurrencies
for crypto, ohlc in ohlc_data.items():
    ma_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['MA'], name=f"MA - {crypto}", line=dict(color='#00cc00', width=2)))

# Customize the layout for Candlestick Chart
try:
    if add_multiselect and len(add_multiselect) >= 2:
        candlestick_fig.update_layout(
            title=f'Candlestick chart for {", ".join(add_multiselect)}',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_dark'
        )
    else:
        st.warning("Select at least 1 cryptocurrency to display the candlestick chart.")
except IndexError:
    st.warning("An error occurred while accessing the selected cryptocurrencies. Please try again.")

# Customize the layout for Stochastic Oscillator
stochastic_fig.update_layout(
    title=f'Stochastic Oscillator for {", ".join(add_multiselect)}',
    xaxis_title='Date',
    yaxis_title='Value',
    template='plotly_dark'
)

# Customize the layout for Moving Average
ma_fig.update_layout(
    title=f'Moving Average for {", ".join(add_multiselect)}',
    xaxis_title='Date',
    yaxis_title='Moving Average',
    template='plotly_dark'
)

# Display the charts
st.plotly_chart(candlestick_fig)
st.plotly_chart(stochastic_fig)
st.plotly_chart(ma_fig)

# Display other relevant information
for crypto, ohlc in ohlc_data.items():
    st.subheader(f'OHLC Data for {crypto}')
    st.write(ohlc)

# Home button
if menu_container.button("Home"):
    st.write("You clicked on the Home button!")
