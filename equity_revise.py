strike_price = 120
option_price = 10.79
current_price = 123

def calculate_lower_bound_price(input_strike_price, market_long_put_price, current_sol_price):
    break_even_price = input_strike_price - market_long_put_price
    return (4*break_even_price)-(3*current_sol_price) 

def calculate_upper_bound_price(input_strike_price, market_long_put_price, current_sol_price):
    return ((current_sol_price+market_long_put_price+market_long_put_price)*2)-current_sol_price

def cal_equity_chart(strike_price, option_price, current_price, new_price):
    lower_bound = calculate_lower_bound_price(strike_price, option_price, current_price)
    upper_bound = calculate_upper_bound_price(strike_price, option_price, current_price)
    if new_price <= strike_price and new_price <= current_price : # under strike and under current case
        option_pnl = (strike_price - new_price - option_price) * 2
        if new_price <= lower_bound: # lower than range case stay under strike price
            sol_pnl = (new_price-current_price)
            avg_price = (lower_bound + current_price)/2
            usd_pnl = new_price-avg_price
            ratio = 1
        else: # understrike and under current but in range case
            ratio = abs(((new_price - current_price)/(lower_bound - current_price)))
            sol_pnl = (new_price-current_price)
            usd_pnl = (((new_price + current_price)/2)-current_price)*ratio
    elif new_price <= strike_price and new_price >= current_price: # stay in range case , understrike and over current
        option_pnl = (strike_price - new_price - option_price) * 2
        ratio = abs(((new_price - current_price)/(upper_bound - current_price)))
        usd_pnl = 0
        sol_pnl = (((new_price + current_price)/2)-current_price)*ratio
    elif new_price >= strike_price and new_price <= current_price: # stay in range case , overstrike and under current
        option_pnl = -(option_price * 2)
        ratio = abs(((new_price - current_price)/(lower_bound - current_price)))
        usd_pnl = (((new_price + current_price)/2)-current_price)*ratio
        sol_pnl = (new_price-current_price)
    elif new_price >= strike_price and new_price >= current_price: # overstrike and over current case
        option_pnl = -(option_price * 2)
        if new_price >= upper_bound: # upper than range case
            usd_pnl = 0
            sol_pnl = ((upper_bound + current_price)/2)-current_price
            ratio = 1
        else: # stay in range case
            ratio = abs(((new_price - current_price)/(upper_bound - current_price)))
            sol_pnl = (((new_price + current_price)/2)-current_price)*ratio
            usd_pnl = 0
    # print(f'option_pnl: {option_pnl}, sol_pnl: {sol_pnl}, usd_pnl: {usd_pnl}, ratio: {ratio} , new_price: {new_price}')
    return (option_pnl + sol_pnl + usd_pnl)/(current_price*2)


