import requests
import pandas as pd
import numpy as np 
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu
    
st.title("Final project Python Candlestick Graph")

add_multiselect = st.multiselect(
    "Choose the following available coins",
    ("Bitcoin" , "Ethereum", "Tether", "USD Coin", "Binance Coin")
)

go_button = st.button("Go")


if "Bitcoin" in add_multiselect:
    st.write("Display Bitcoin information or candlestick chart here")
    # Puedes agregar información detallada o un gráfico de velas para Bitcoin
elif "Ethereum" in add_multiselect:
    st.write("Display Ethereum information or candlestick chart here")
    # Puedes agregar información detallada o un gráfico de velas para Ethereum

elif "Tether" in add_multiselect:
    st.write("Display Ethereum information or candlestick chart here")

elif "USD Coin" in add_multiselect:
    st.write("Display Ethereum information or candlestick chart here")

elif "Binance Coin" in add_multiselect:
    st.write("Display Ethereum information or candlestick chart here")

else:
    st.write("Please choose an appropriate Coin")

# Dictionary to map the selected cryptocurrency to its corresponding pair:
pair_mapping = {
    "Bitcoin": "XBTUSD",
    "Ethereum": "ETHUSD",
    "Tether": "USDTUSD",
    "USD Coin": "USDCUSD",
    "Binance Coin": "BNBUSD",
}

# Request OHLC data from Kraken API
url_ohlc = "https://api.kraken.com/0/public/OHLC"
selected_pair = pair_mapping.get(add_multiselect[0])

if selected_pair:
    req_params = {
        "pair": selected_pair,
        "interval": 60,
    }
    response = requests.get(url_ohlc, params=req_params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        if result and list(result.keys()) and len(result[list(result.keys())[0]]) > 0:
            # Convertir datos a DataFrame de Pandas
            ohlc = pd.DataFrame(result[list(result.keys())[0]], columns=["datetime", "open", "high", "low", "close", "vwap", "volume", "count"])
            ohlc = ohlc.astype({'open': float, 'high': float, 'low': float, 'close': float, 'vwap': float, 'volume': float})
            ohlc.index = pd.to_datetime(ohlc["datetime"], unit='s')
        else:
            st.warning("No valid data available for the selected cryptocurrency pair.")
    else:
        st.warning("Error in API response. Please try again.")
else:
    st.warning("Please choose an appropriate Coin")

# Assuming ohlc is the DataFrame containing the OHLC data

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

# Create a candlestick chart using the fetched OHLC data
fig = go.Figure()

if add_multiselect:
    # Visualización de un gráfico de velas para la criptomoneda seleccionada
    fig.add_trace(go.Candlestick(
        x=ohlc.index,
        open=ohlc['open'],
        high=ohlc['high'],
        low=ohlc['low'],
        close=ohlc['close']
    ))

    # Personalizar la tabla
    fig.update_layout(
        title=f'Candlestick Chart for {add_multiselect[0]}',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark'
    )

    # Visualizar la tabla
    st.plotly_chart(fig)

    # Show the info  
    st.subheader("Kraken OHLC Data")
    st.write(ohlc)

    st.title(f'{add_multiselect[0]} Candlestick Chart')

    # Create a candlestick chart using the fetched OHLC data
    fig = go.Figure(data=[go.Candlestick(
        x=ohlc.index,
        open=ohlc['open'],
        high=ohlc['high'],
        low=ohlc['low'],
        close=ohlc['close']
    )])

    # Now, let's add the gradient descent result to the graph
    fig.add_trace(go.Scatter(x=[ohlc.index[0], ohlc.index[-1]], y=[start, optimized_value], mode='lines', name='Gradient Descent'))

    # Display the candlestick chart with the gradient descent line
    st.plotly_chart(fig)

    # Home button
    if st.button("Home"):
        st.write("You clicked on the Home button!")