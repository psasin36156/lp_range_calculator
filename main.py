import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def get_sol_price():
    """Fetch current SOL price from Binance API"""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except Exception as e:
        # Try backup API if Binance fails
        try:
            url = "https://api.kraken.com/0/public/Ticker?pair=SOLUSD"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return float(data['result']['SOLUSD']['c'][0])
        except Exception as e2:
            st.error(f"Error fetching SOL price: {e2}")
            return None

def get_eth_price():
    """Fetch current ETH price from Binance API"""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except Exception as e:
        # Try backup API if Binance fails
        try:
            url = "https://api.kraken.com/0/public/Ticker?pair=ETHUSD"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return float(data['result']['XETHZUSD']['c'][0])
        except Exception as e2:
            st.error(f"Error fetching ETH price: {e2}")
            return None
        
    
def calculate_lower_bound_price(input_strike_price, market_long_put_price, current_sol_price):
    break_even_price = input_strike_price - market_long_put_price
    return (4*break_even_price)-(3*current_sol_price) 

def calculate_upper_bound_price(input_strike_price, market_long_put_price, current_sol_price):
    return ((current_sol_price+market_long_put_price+market_long_put_price)*2)-current_sol_price

def cal_lower_bound_percentage(lower_bound_price, current_sol_price):
    return ((lower_bound_price-current_sol_price)/current_sol_price)*100

def cal_upper_bound_percentage(upper_bound_price, current_sol_price):
    return ((upper_bound_price-current_sol_price)/current_sol_price)*100

def cal_equity_chart(strike_price, option_price, current_price, new_price):
    lower_bound = calculate_lower_bound_price(strike_price, option_price, current_price)
    upper_bound = calculate_upper_bound_price(strike_price, option_price, current_price)
    if new_price <= strike_price and new_price <= current_price:
        option_pnl = (strike_price - new_price - option_price) * 2
        if new_price <= lower_bound:
            sol_pnl = (new_price-current_price)
            avg_price = (lower_bound + current_price)/2
            usd_pnl = new_price-avg_price
            ratio = 1
        else:
            ratio = abs(((new_price - current_price)/(lower_bound - current_price)))
            sol_pnl = (new_price-current_price)
            usd_pnl = (((new_price + current_price)/2)-current_price)*ratio
    elif new_price <= strike_price and new_price >= current_price:
        option_pnl = (strike_price - new_price - option_price) * 2
        ratio = abs(((new_price - current_price)/(upper_bound - current_price)))
        usd_pnl = 0
        sol_pnl = (((new_price + current_price)/2)-current_price)*ratio
    elif new_price >= strike_price and new_price <= current_price:
        option_pnl = -(option_price * 2)
        ratio = abs(((new_price - current_price)/(lower_bound - current_price)))
        usd_pnl = (((new_price + current_price)/2)-current_price)*ratio
        sol_pnl = (new_price-current_price)
    elif new_price >= strike_price and new_price >= current_price:
        option_pnl = -(option_price * 2)
        if new_price >= upper_bound:
            usd_pnl = 0
            sol_pnl = ((upper_bound + current_price)/2)-current_price
            ratio = 1
        else:
            ratio = abs(((new_price - current_price)/(upper_bound - current_price)))
            sol_pnl = (((new_price + current_price)/2)-current_price)*ratio
            usd_pnl = 0
    return (option_pnl + sol_pnl + usd_pnl)/(current_price*2)

def create_equity_chart(strike_price, option_price, current_price):
    # Generate price range for x-axis
    lower_bound = calculate_lower_bound_price(strike_price, option_price, current_price)
    upper_bound = calculate_upper_bound_price(strike_price, option_price, current_price)
    price_range = np.linspace(lower_bound * 0.75, upper_bound * 1.25, 300)
    equity_values = [cal_equity_chart(strike_price, option_price, current_price, price) for price in price_range]
    
    # Create DataFrame for the chart
    df = pd.DataFrame({
        'Price': price_range,
        'Equity': equity_values
    })

    max_loss = df['Equity'].min()
    
    # Create the plot using plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Price'], y=df['Equity'] * 100, name='PNL %'))
    
    # Add vertical lines for important price levels
    fig.add_vline(x=current_price, line_dash="dash", annotation_text="Current Price" , line_color='green' , )
    fig.add_vline(x=strike_price, line_dash="dash", annotation_text="Strike Price" , line_color='blue')
    fig.add_vline(x=lower_bound, line_dash="dash", annotation_text="Lower Bound" , line_color='red')
    fig.add_vline(x=upper_bound, line_dash="dash", annotation_text="Upper Bound" , line_color='red')
    

    # Update layout
    fig.update_layout(
        title='Equity Chart',
        xaxis_title='Price($)',
        yaxis_title='PNL (%)',
        hovermode='x unified',
        xaxis_range=[lower_bound * 0.75, upper_bound * 1.25]
    )
    
    return fig,max_loss

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# Streamlit UI

st.title("LP position range calculator")

# Display current SOL price
current_sol_price = get_sol_price()
current_eth_price = get_eth_price()

if current_sol_price:
    st.metric(f"Current SOL Price", f"${current_sol_price:.2f}")

# Input widgets
col1, col2 = st.columns(2)
with col1:
    strike_price = st.number_input("SOL Strike Price ($)", min_value=0.0, value=150.0, step=0.1)
with col2:
    put_price = st.number_input("SOL Market Long Put Price ($)", min_value=0.0, value=22.68, step=0.01)

# Calculate button
if st.button("Calculate Range", key="calculate_sol"):
    if current_sol_price:
        lower_bound = calculate_lower_bound_price(strike_price, put_price, current_sol_price)
        upper_bound = calculate_upper_bound_price(strike_price, put_price, current_sol_price)
        lower_bound_percentage = cal_lower_bound_percentage(lower_bound, current_sol_price)
        upper_bound_percentage = cal_upper_bound_percentage(upper_bound, current_sol_price)
        
        # Display results
        st.subheader("Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lower Bound Price", f"${lower_bound:.2f}", delta=f"{lower_bound_percentage:.2f}%")
        with col2:
            st.metric("Upper Bound Price (break-even with long_put_premium )", f"${upper_bound:.2f}", delta=f"{upper_bound_percentage:.2f}%")

        # Add equity chart
        fig,max_loss = create_equity_chart(strike_price, put_price, current_sol_price)
        st.code(f"LP 1 SOL : {current_sol_price:.2f} USD (TOTAL {current_sol_price*2:.2f} $USD)\nLong Put 2 SOL at Strike Price : {strike_price} (TOTAL {put_price*2:.2f} $USD)\nMax loss : {max_loss*100:.2f}% \nTotal initial investment : {current_sol_price*2+put_price*2:.2f} $USD")
        st.plotly_chart(fig, use_container_width=True)

# Add a separator
st.markdown("---")

if current_eth_price:
    st.metric(f"Current ETH Price", f"${current_eth_price:.2f}")

# Input widgets
col1, col2 = st.columns(2)
with col1:
    strike_price = st.number_input("ETH Strike Price ($)", 
                                  min_value=0,
                                  value=2300,
                                  step=10)
with col2:
    put_price = st.number_input("ETH Market Long Put Price ($)", 
                               min_value=0,
                               value=129,
                               step=1)

# Calculate button
if st.button("Calculate Range", key="calculate_eth"):
    if current_eth_price:
        lower_bound = calculate_lower_bound_price(strike_price, put_price, current_eth_price)
        upper_bound = calculate_upper_bound_price(strike_price, put_price, current_eth_price)
        lower_bound_percentage = cal_lower_bound_percentage(lower_bound, current_eth_price)
        upper_bound_percentage = cal_upper_bound_percentage(upper_bound, current_eth_price)
        
        # Display results
        st.subheader("Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lower Bound Price", f"${lower_bound:.2f}", delta=f"{lower_bound_percentage:.2f}%")
        with col2:
            st.metric("Upper Bound Price (break-even with long_put_premium )", f"${upper_bound:.2f}", delta=f"{upper_bound_percentage:.2f}%")

        # Add equity chart
        fig,max_loss = create_equity_chart(strike_price, put_price, current_eth_price)
        st.code(f"LP 1 ETH : {current_eth_price:.2f} USD (TOTAL {current_eth_price*2:.2f} $USD)\nLong Put 2 ETH at Strike Price : {strike_price} (TOTAL {put_price*2:.2f} $USD)\nMax loss : {max_loss*100:.2f}% \nTotal initial investment : {current_eth_price*2+put_price*2:.2f} $USD")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
# Footer with contacts and profile image
st.markdown("""
<div style='text-align: center'>
    <img src='https://img2.pic.in.th/pic/fe3t_ALn_400x400.th.jpg' 
         style='width: 80px; height: 80px; border-radius: 10px; margin-bottom: 10px;'>
    <h4>Made by 💖 by sapiensp</h4>
    <p>
        🐦 Twitter: <a href='https://twitter.com/0xsapiensp'>0xsapiensp</a> &nbsp;&nbsp;|&nbsp;&nbsp;
        📱 Telegram: <a href='https://t.me/sapiensp'>@sapiensp</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Add some space at the bottom``
st.markdown("<br>", unsafe_allow_html=True)


