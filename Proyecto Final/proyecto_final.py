import requests
import pandas as pd
import numpy as np 
import plotly.graph_objects as go
import streamlit as st
import custom_menu
import indicadores


# Request OHLC data from Kraken API
url_ohlc = "https://api.kraken.com/0/public/OHLC"
req_params = {
    "pair": "XBTUSD",
    "interval": 60,
}
result = requests.get(url_ohlc, params=req_params).json()["result"]

# Convert data to Pandas DataFrame
ohlc = pd.DataFrame(result[list(result.keys())[0]], columns=["datetime", "open", "high", "low", "close", "vwap", "volume", "count"])
ohlc = ohlc.astype({'open': float, 'high': float, 'low': float, 'close': float, 'vwap': float, 'volume': float})
ohlc.index = pd.to_datetime(ohlc["datetime"], unit='s')



# Assuming ohlc is the DataFrame containing the OHLC data

# Create a candlestick chart using the fetched OHLC data
fig = go.Figure(data=[go.Candlestick(
    x=ohlc.index,
    open=ohlc['open'],
    high=ohlc['high'],
    low=ohlc['low'],
    close=ohlc['close']
)])

st.title('Bitcoin (XBT/USD) Candlestick Chart')

# Create a candlestick chart using the fetched OHLC data
fig = go.Figure(data=[go.Candlestick(
    x=ohlc.index,
    open=ohlc['open'],
    high=ohlc['high'],
    low=ohlc['low'],
    close=ohlc['close']
)])


# Stocastic oscillator
def gradient_descent(
    gradient, start, learn_rate, n_iter=50, tolerance=1e-06
):
    vector = start
    for _ in range(n_iter):
        diff = -learn_rate * gradient(vector)
        if np.all(np.abs(diff) <= tolerance):
            break
        vector += diff
    return vector

# Example gradient function (replace this with your actual gradient function)
def gradient_function(x):
    return 2 * x

# Example usage of gradient descent (change parameters as needed)
start = 10  # Example start point
learn_rate = 0.1  # Example learning rate
optimized_value = gradient_descent(gradient_function, start, learn_rate)
st.write("Optimized value:", optimized_value)

# Now, let's add the gradient descent result to the graph
fig.add_trace(go.Scatter(x=[ohlc.index[0], ohlc.index[-1]], y=[start, optimized_value], mode='lines', name='Gradient Descent'))

# Display the candlestick chart with the gradient descent line
st.plotly_chart(fig)



