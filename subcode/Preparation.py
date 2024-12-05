# ---------------------------------------------------------
# RSI Backtesting Tool
#
# Language: Python
# Description: This is the entry point of the RSI Backtesting Tool. It
#              initializes and launches the application by creating
#              an instance of the `BacktestApp` class from `app_ui.py`.
# Assistance: This structure and modularization were inspired by
#             ChatGPT, an AI language model by OpenAI.
import yfinance as yf
import pandas as pd
import numpy as np


# Function to fetch historical data
def get_historical_data(ticker, start_date, end_date):
    """
    Fetches historical price data for a given ticker.
    """
    # Download daily historical price data for the specified ticker and date range
    data = yf.download(tickers=ticker, start=start_date, end=end_date, interval='1d', progress=False)
    data.dropna(inplace=True) # Remove rows with missing values to ensure data consistency
    # Flatten MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0) # Extract the first level of the columns
    return data

# Function to calculate RSI
def calculate_rsi(data, period=14):
    """
    Calculates the Relative Strength Index (RSI).
    """
    delta = data['Close'].diff() # Compute daily price changes
    # Identify gains and losses from the price differences
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    # Calculate the rolling average of gains and losses over the specified period
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss # Compute the Relative Strength
    # Calculate RSI using the standard formula
    data['RSI'] = 100 - (100 / (1 + rs))
    data['RSI'] = data['RSI'].fillna(50)  # Neutral RSI for initial periods
    return data

# Function to generate trading signals based on RSI
def generate_signals(data, rsi_overbought, rsi_oversold):
    """
    Generates trading signals based on RSI levels.
    """
    data['Signal'] = 0 # Initialize new column with default value 0

    # Buy when RSI crosses above oversold level
    buy_signals = (data['RSI'] > rsi_oversold) & (data['RSI'].shift(1) <= rsi_oversold) # Generate Buy signals when RSI crosses above oversold level
    data.loc[buy_signals, 'Signal'] = 1 # Assign Buy signals (1) to the signal column

    # Sell when RSI crosses below overbought level
    sell_signals = (data['RSI'] < rsi_overbought) & (data['RSI'].shift(1) >= rsi_overbought) # Generate Sell signals when RSI crosses below overbought level
    data.loc[sell_signals, 'Signal'] = -1 # Assign Sell signals (-1) to the signal column

    return data

# Function to backtest the strategy
def backtest_strategy(data, initial_capital, fee_percentage):
    """
    Backtests the trading strategy.
    """
    data = data.copy() # Create a copy of the input data to avoid modifying the original DataFrame
    # Initialize variables for simulation
    cash = initial_capital
    holdings = 0
    total_fees = 0
    portfolio_values = []
    positions = []
    trades = []
    daily_returns = []
    prev_portfolio_value = initial_capital

    # Iterate through each row in the data
    for i in range(len(data)):
        price = data['Close'].iloc[i] # Get the closing price for the current day
        # Handle edge cases where price might be a Series
        if isinstance(price, pd.Series):
            price = price.iloc[0] # Extract the first value if Series
        price = float(price)
        signal = data['Signal'].iloc[i] # Get the trading signal for the current day
        trade = 0  # 1 for buy, -1 for sell, 0 for hold
        # If the signal is Buy and there are no current holdings
        if signal == 1 and holdings == 0:
            # Buy
            shares = int(cash // price) # Determine the number of shares
            if shares > 0:
                fee = shares * price * fee_percentage
                cash -= shares * price + fee
                holdings += shares # Update holdings
                total_fees += fee # Add fee to total fees
                positions.append(1) # Record the new position
                trade = 1 # Record the trade as a Buy
            else:
                positions.append(positions[-1] if positions else 0) # No change in position
        # If the signal is Sell and there are holdings to sell
        elif signal == -1 and holdings > 0:
            # Sell
            fee = holdings * price * fee_percentage # Calculate transaction fee
            cash += holdings * price - fee
            holdings = 0 # Reset holdings to zero
            total_fees += fee # Add fee to total fees
            positions.append(0) # Record the new position
            trade = -1 # Record the trade as a Sell
        # If no trade is executed, maintain the previous position
        else:
            # Maintain current position
            positions.append(positions[-1] if positions else 0)
        # Calculate the portfolio value
        portfolio_value = cash + holdings * price
        portfolio_values.append(portfolio_value)
        # Record the trade action (1 for buy, -1 for sell, 0 for hold)
        trades.append(trade)
        # Calculate daily return
        daily_return = (portfolio_value - prev_portfolio_value) / prev_portfolio_value if prev_portfolio_value != 0 else 0
        daily_returns.append(daily_return)
        # Update the previous portfolio value for the next iteration
        prev_portfolio_value = portfolio_value

    # Add the calculated metrics as new columns in the DataFrame
    data['Portfolio Value'] = portfolio_values
    data['Total Fees'] = total_fees
    data['Positions'] = positions # 1 for long, 0 for no position
    data['Trades'] = trades  # Record trades for plotting
    data['Strategy Daily Return'] = daily_returns # Daily returns of the strategy
    return data

# Function to calculate performance metrics
def calculate_performance_metrics(data, initial_capital):
    data = data.copy() # Create a copy to avoid modifying the original data
    total_return = (data['Portfolio Value'].iloc[-1] / initial_capital) - 1 # Calculate total return for the RSI strategy
    cumulative_max = data['Portfolio Value'].expanding(min_periods=1).max() # Calculate the maximum portfolio value over time
    drawdown = (data['Portfolio Value'] - cumulative_max) / cumulative_max # Calculate drawdown as the percentage below the cumulative max
    max_drawdown = drawdown.min() # Minimum drawdown is the maximum loss
    total_fees = data['Total Fees'].iloc[-1] # Get the total fees paid during the backtesting
    final_portfolio_value = data['Portfolio Value'].iloc[-1] # Get the final portfolio value

    # Calculate strategy volatility and Sharpe Ratio
    strategy_daily_returns = data['Strategy Daily Return']
    strategy_volatility = strategy_daily_returns.std() * np.sqrt(252)  # Annualized volatility
    risk_free_rate = 0.01  # Assume 1% annual risk-free rate
    strategy_sharpe_ratio = (strategy_daily_returns.mean() * 252 - risk_free_rate) / strategy_volatility if strategy_volatility != 0 else 0 # Calculate Sharpe Ratio: (Mean daily return - Risk-free rate) / Volatility. And avoid division by 0

    # Number of trades
    num_trades = data['Trades'].abs().sum() # Count number of trades

    # Buy and Hold Metrics
    data['Buy and Hold Position'] = 1  # Always holding
    data['Buy and Hold Portfolio Value'] = initial_capital * (data['Close'] / data['Close'].iloc[0])
    bh_total_return = (data['Buy and Hold Portfolio Value'].iloc[-1] / initial_capital) - 1 # Calculate total return for Buy and Hold
    bh_cumulative_max = data['Buy and Hold Portfolio Value'].expanding(min_periods=1).max() # Calculate maximum portfolio value for Buy and Hold
    bh_drawdown = (data['Buy and Hold Portfolio Value'] - bh_cumulative_max) / bh_cumulative_max # Calculate drawdown for Buy and Hold
    bh_max_drawdown = bh_drawdown.min()
    data['Buy and Hold Daily Return'] = data['Close'].pct_change().fillna(0)    # Calculate daily returns for Buy and Hold
    bh_volatility = data['Buy and Hold Daily Return'].std() * np.sqrt(252)  # Annualized volatility
    bh_sharpe_ratio = (data['Buy and Hold Daily Return'].mean() * 252 - risk_free_rate) / bh_volatility if bh_volatility != 0 else 0 # Calculate Sharpe Ratio for Buy and Hold
    bh_final_portfolio_value = data['Buy and Hold Portfolio Value'].iloc[-1] # Get the final portfolio value for Buy and Hold

    # Prepare metrics dictionary
    metrics = {
        # Metrics for RSI strategy
        'portfolio_value': f"${final_portfolio_value:,.2f}",
        'total_return': f"{total_return:.2%}",
        'max_drawdown': f"{max_drawdown:.2%}",
        'volatility': f"{strategy_volatility:.2%}",
        'sharpe_ratio': f"{strategy_sharpe_ratio:.2f}",
        'fees_paid': f"${total_fees:,.2f}",
        'number_of_trades': int(num_trades),
        # Metrics for Buy and Hold
        'bh_portfolio_value': f"${bh_final_portfolio_value:,.2f}",
        'bh_total_return': f"{bh_total_return:.2%}",
        'bh_max_drawdown': f"{bh_max_drawdown:.2%}",
        'bh_volatility': f"{bh_volatility:.2%}",
        'bh_sharpe_ratio': f"{bh_sharpe_ratio:.2f}",
        'bh_number_of_trades': "N/A",  # Not applicable for buy and hold
        'bh_fees_paid': "N/A",         # Not applicable for buy and hold
    }
    return data, metrics # Return updated DataFrame and metrics dictionary

