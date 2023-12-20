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

    # Add indicators for overbought, expected, and oversold
    ohlc['Overbought'] = 80
    ohlc['Expected_Max'] = 80  # Upper limit for expected range
    ohlc['Expected_Min'] = 20  # Lower limit for expected range
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

# Single selection of cryptocurrencies based on a dropdown menu
selected_crypto = menu_container.selectbox(
    "Choose a cryptocurrency",
    ("Bitcoin", "Ethereum", "Tether", "USD Coin", "Doge Coin", "Solana", "XRP", "Cardano", "Avalanche")
)

go_button = menu_container.button("Go")


# Dictionary to map the selected cryptocurrency to its corresponding pair:
pair_mapping = {
    "Bitcoin": "XXBTZUSD",
    "Ethereum": "XETHZUSD",
    "Tether": "USDTZUSD",
    "USD Coin": "USDCUSD",
    "Doge Coin": "XDGUSD",
    "Solana": "SOLUSD",
    "XRP": "XRPUSD",
    "Cardano": "ADAUSD",
    "Avalanche": "AVAXUSD",
}

# Fetch OHLC data for the selected cryptocurrency
ohlc_data = {}
if go_button:
    selected_pair = pair_mapping.get(selected_crypto)
    if selected_pair:
        ohlc = fetch_ohlc_data(selected_pair)
        ohlc = calculate_stochastic_oscillator(ohlc)
        ohlc = calculate_moving_average(ohlc, window=10)
        ohlc_data[selected_crypto] = ohlc

# Create separate Figure objects for Candlestick Chart, Stochastic Oscillator, and Moving Average
candlestick_fig = go.Figure()
stochastic_fig = go.Figure()
ma_fig = go.Figure()


# Visualization of a candlestick chart for the selected cryptocurrency
if selected_crypto in ohlc_data:
    ohlc = ohlc_data[selected_crypto]
    candlestick_fig.add_trace(go.Candlestick(
        x=ohlc.index,
        open=ohlc['open'],
        high=ohlc['high'],
        low=ohlc['low'],
        close=ohlc['close'],
        name=f"{selected_crypto} - {ohlc.index[0].strftime('%Y-%m-%d')} to {ohlc.index[-1].strftime('%Y-%m-%d')}",
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

    # Customize the layout for Candlestick Chart with dynamic title
    candlestick_fig.update_layout(
        title=f'Candlestick chart for {selected_crypto}',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark'
    )


# Visualization of Stochastic Oscillator with new ranges
for crypto, ohlc in ohlc_data.items():
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['%K'], name=f"%K - {crypto}", line=dict(color='#ff9900', width=2)))
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['%D'], name=f"%D - {crypto}", line=dict(color='#000000', width=2)))

    # Overbought and Oversold lines
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['Overbought'], name="Overbought (80-100)", line=dict(color='red', width=1)))
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['Oversold'], name="Oversold (0-20)", line=dict(color='blue', width=1)))

    # Expected range shading
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['Expected_Max'], mode='lines', name="Expected Upper Bound", line=dict(color='green', width=1)))
    stochastic_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['Expected_Min'], mode='lines', fill='tonexty', name="Expected Lower Bound", line=dict(color='green', width=1)))


# Visualization of a Moving Average for the selected cryptocurrencies
for crypto, ohlc in ohlc_data.items():
    ma_fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc['MA'], name=f"MA - {crypto}", line=dict(color='#00cc00', width=2)))

# Customize the layout for Stochastic Oscillator
stochastic_fig.update_layout(
    title=f'Stochastic Oscillator for {selected_crypto}',
    xaxis_title='Date',
    yaxis_title='Value',
    template='plotly_dark'
)

# Customize the layout for Moving Average
ma_fig.update_layout(
    title=f'Moving Average for {selected_crypto}',
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

