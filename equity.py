strike_price = 180
option_price = 40
current_price = 150

def calculate_lower_bound_price(input_strike_price, market_long_put_price, current_sol_price):
    break_even_price = input_strike_price - market_long_put_price
    return (4*break_even_price)-(3*current_sol_price) 

def calculate_upper_bound_price(input_strike_price, market_long_put_price, current_sol_price):
    return ((current_sol_price+market_long_put_price+market_long_put_price)*2)-current_sol_price

def cal_pnl(strike_price, option_price, current_price, new_price):
    lower_bound = calculate_lower_bound_price(strike_price, option_price, current_price)
    upper_bound = calculate_upper_bound_price(strike_price, option_price, current_price)
    if new_price <= strike_price: #bearish case 
        option_pnl = (strike_price - new_price - option_price) * 2
        if new_price <= lower_bound: # lower than range case
            sol_pnl = (new_price-current_price)
            avg_price = (lower_bound + current_price)/2
            usd_pnl = new_price-avg_price
            ratio = 1
        else: # stay in range case
            if new_price >= current_price:
                lower_bound = upper_bound
                ratio = abs(((new_price - current_price)/(lower_bound - current_price)))
                usd_pnl = 0
                sol_pnl = (((new_price + current_price)/2)-current_price)*ratio
            else:
                ratio = abs(((new_price - current_price)/(lower_bound - current_price)))
                sol_pnl = (new_price-current_price)
                usd_pnl = (((new_price + current_price)/2)-current_price)*ratio
        print(f'option_pnl: {option_pnl}, sol_pnl: {sol_pnl}, ratio_usd: {ratio}, usd_pnl: {usd_pnl} , new_price: {new_price}')
        return (option_pnl + sol_pnl + usd_pnl)/(current_price*2)
    else: # bullish case
        option_pnl = -(option_price * 2)
        if new_price >= upper_bound: # upper than range case
            sol_pnl = ((upper_bound + current_price)/2)-current_price
            ratio = 1
        else: # stay in range case
            ratio = abs(((new_price - current_price)/(upper_bound - current_price)))
            sol_pnl = (((new_price + current_price)/2)-current_price)*ratio
        print(f'option_pnl: {option_pnl}, sol_pnl: {sol_pnl}, ratio_usd: {ratio}')
        return (option_pnl + sol_pnl)/(current_price*2)

import matplotlib.pyplot as plt
import numpy as np

# Generate price range for x-axis
lower_bound = calculate_lower_bound_price(strike_price, option_price, current_price)
upper_bound = calculate_upper_bound_price(strike_price, option_price, current_price)

price_range = np.linspace(lower_bound*0.5, upper_bound*1.2, 1000)

# Calculate PnL for each price point
pnl_values = [cal_pnl(strike_price, option_price, current_price,price) for price in price_range]

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(price_range, pnl_values, 'b-', label='PnL')
plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)

# Add vertical lines with annotations
vertical_lines = [
    (current_price, 'green', 'Current Price'),
    (strike_price - option_price, 'orange', 'Break-even'),
    (lower_bound, 'purple', 'Lower Bound'),
    (upper_bound, 'brown', 'Upper Bound'),
    (strike_price, 'red', 'Strike Price')
]

for value, color, label in vertical_lines:
    plt.axvline(x=value, color=color, linestyle='--', alpha=0.5, label=f'{label} ({value:.2f})')
    # Add annotation below x-axis
    plt.annotate(f'{value:.2f}', 
                xy=(value, plt.ylim()[0]),  # Place at bottom of plot
                xytext=(0, -20),  # 20 points below
                textcoords='offset points',
                ha='center',
                va='top',
                rotation=45)

# Add labels and title
plt.xlabel('Price')
plt.ylabel('PnL Ratio')
plt.title('PnL vs Price')
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)

# Show the plot
plt.show()
