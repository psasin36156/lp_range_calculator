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
    
input_stike_price = 150
input_market_long_put_price = 22.68

def calculate_lower_bound_price(input_strike_price, market_long_put_price):
    current_sol_price = get_sol_price()
    break_even_price = input_strike_price - market_long_put_price
    """Calculate lower bound price for a long put position"""
    return (4*break_even_price)-(3*current_sol_price) 

def cal_percentage(lower_bound_price, current_sol_price):
    return ((lower_bound_price-current_sol_price)/current_sol_price)*100

# Streamlit UI
st.title("DLMM LP lower bound price calculator")

# Display current SOL price
current_sol_price = get_sol_price()
if current_sol_price:
    st.metric("Current SOL Price", f"${current_sol_price:.2f} (real time)")

# Input widgets
col1, col2 = st.columns(2)
with col1:
    strike_price = st.number_input("Strike Price ($)", min_value=0.0, value=150.0, step=0.1)
with col2:
    put_price = st.number_input("Market Long Put Price ($)", min_value=0.0, value=22.68, step=0.01)

# Calculate button
if st.button("Calculate Range"):
    if current_sol_price:
        lower_bound = calculate_lower_bound_price(strike_price, put_price)
        percentage = cal_percentage(lower_bound, current_sol_price)
        
        # Display results
        st.subheader("Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lower Bound Price", f"${lower_bound:.2f}")
        with col2:
            st.metric("Percentage from Current Price", f"{percentage:.2f}%")
        
        # Additional information
        st.info(f"Break-even Price: ${strike_price - put_price:.2f}")

# Add a separator
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

# Add some space at the bottom
st.markdown("<br>", unsafe_allow_html=True)


