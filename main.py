import streamlit as st
import requests

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
    return ((current_sol_price+market_long_put_price)*2)-current_sol_price

def cal_lower_bound_percentage(lower_bound_price, current_sol_price):
    return ((lower_bound_price-current_sol_price)/current_sol_price)*100

def cal_upper_bound_percentage(upper_bound_price, current_sol_price):
    return ((upper_bound_price-current_sol_price)/current_sol_price)*100

# Streamlit UI
st.title("LP position range calculator")

# Display current SOL price
current_sol_price = get_sol_price()
current_eth_price = get_eth_price()

if current_sol_price:
    st.metric(f"Current SOL Price (LP 1 SOL:{current_sol_price:.2f}$)", f"${current_sol_price:.2f}")

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

# Add a separator
st.markdown("---")

if current_eth_price:
    st.metric(f"Current ETH Price (LP 1 ETH:{current_eth_price:.2f}$)", f"${current_eth_price:.2f}")

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


