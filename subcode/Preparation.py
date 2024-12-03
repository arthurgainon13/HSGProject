
import yfinance as yf
import pandas as pd
import numpy as np


# Function to fetch historical data
def get_historical_data(ticker, start_date, end_date):
    """
    Fetches historical price data for a given ticker.
    """
    data = yf.download(tickers=ticker, start=start_date, end=end_date, interval='1d', progress=False)
    data.dropna(inplace=True)
    # Flatten MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

# Function to calculate RSI
def calculate_rsi(data, period=14):
    """
    Calculates the Relative Strength Index (RSI).
    """
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['RSI'] = data['RSI'].fillna(50)  # Neutral RSI for initial periods
    return data

# Function to generate trading signals based on RSI
def generate_signals(data, rsi_overbought, rsi_oversold):
    """
    Generates trading signals based on RSI levels.
    """
    data['Signal'] = 0

    # Buy when RSI crosses above oversold level
    buy_signals = (data['RSI'] > rsi_oversold) & (data['RSI'].shift(1) <= rsi_oversold)
    data.loc[buy_signals, 'Signal'] = 1

    # Sell when RSI crosses below overbought level
    sell_signals = (data['RSI'] < rsi_overbought) & (data['RSI'].shift(1) >= rsi_overbought)
    data.loc[sell_signals, 'Signal'] = -1

    return data

# Function to backtest the strategy
def backtest_strategy(data, initial_capital, fee_percentage):
    """
    Backtests the trading strategy.
    """
    data = data.copy()
    cash = initial_capital
    holdings = 0
    total_fees = 0
    portfolio_values = []
    positions = []
    trades = []
    daily_returns = []
    prev_portfolio_value = initial_capital

    for i in range(len(data)):
        price = data['Close'].iloc[i]
        if isinstance(price, pd.Series):
            price = price.iloc[0]
        price = float(price)
        signal = data['Signal'].iloc[i]
        trade = 0  # 1 for buy, -1 for sell, 0 for hold
        if signal == 1 and holdings == 0:
            # Buy
            shares = int(cash // price)
            if shares > 0:
                fee = shares * price * fee_percentage
                cash -= shares * price + fee
                holdings += shares
                total_fees += fee
                positions.append(1)
                trade = 1
            else:
                positions.append(positions[-1] if positions else 0)
        elif signal == -1 and holdings > 0:
            # Sell
            fee = holdings * price * fee_percentage
            cash += holdings * price - fee
            holdings = 0
            total_fees += fee
            positions.append(0)
            trade = -1
        else:
            # Maintain current position
            positions.append(positions[-1] if positions else 0)
        portfolio_value = cash + holdings * price
        portfolio_values.append(portfolio_value)
        trades.append(trade)
        # Calculate daily return
        daily_return = (portfolio_value - prev_portfolio_value) / prev_portfolio_value if prev_portfolio_value != 0 else 0
        daily_returns.append(daily_return)
        prev_portfolio_value = portfolio_value

    data['Portfolio Value'] = portfolio_values
    data['Total Fees'] = total_fees
    data['Positions'] = positions
    data['Trades'] = trades  # Record trades for plotting
    data['Strategy Daily Return'] = daily_returns
    return data

# Function to calculate performance metrics
def calculate_performance_metrics(data, initial_capital):
    data = data.copy()
    total_return = (data['Portfolio Value'].iloc[-1] / initial_capital) - 1
    cumulative_max = data['Portfolio Value'].expanding(min_periods=1).max()
    drawdown = (data['Portfolio Value'] - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()
    total_fees = data['Total Fees'].iloc[-1]
    final_portfolio_value = data['Portfolio Value'].iloc[-1]

    # Calculate strategy volatility and Sharpe Ratio
    strategy_daily_returns = data['Strategy Daily Return']
    strategy_volatility = strategy_daily_returns.std() * np.sqrt(252)  # Annualized volatility
    risk_free_rate = 0.01  # Assume 1% annual risk-free rate
    strategy_sharpe_ratio = (strategy_daily_returns.mean() * 252 - risk_free_rate) / strategy_volatility if strategy_volatility != 0 else 0

    # Number of trades
    num_trades = data['Trades'].abs().sum()

    # Buy and Hold Metrics
    data['Buy and Hold Position'] = 1  # Always holding
    data['Buy and Hold Portfolio Value'] = initial_capital * (data['Close'] / data['Close'].iloc[0])
    bh_total_return = (data['Buy and Hold Portfolio Value'].iloc[-1] / initial_capital) - 1
    bh_cumulative_max = data['Buy and Hold Portfolio Value'].expanding(min_periods=1).max()
    bh_drawdown = (data['Buy and Hold Portfolio Value'] - bh_cumulative_max) / bh_cumulative_max
    bh_max_drawdown = bh_drawdown.min()
    data['Buy and Hold Daily Return'] = data['Close'].pct_change().fillna(0)
    bh_volatility = data['Buy and Hold Daily Return'].std() * np.sqrt(252)  # Annualized volatility
    bh_sharpe_ratio = (data['Buy and Hold Daily Return'].mean() * 252 - risk_free_rate) / bh_volatility if bh_volatility != 0 else 0
    bh_final_portfolio_value = data['Buy and Hold Portfolio Value'].iloc[-1]

    # Prepare metrics dictionary
    metrics = {
        'portfolio_value': f"${final_portfolio_value:,.2f}",
        'total_return': f"{total_return:.2%}",
        'max_drawdown': f"{max_drawdown:.2%}",
        'volatility': f"{strategy_volatility:.2%}",
        'sharpe_ratio': f"{strategy_sharpe_ratio:.2f}",
        'fees_paid': f"${total_fees:,.2f}",
        'number_of_trades': int(num_trades),
        'bh_portfolio_value': f"${bh_final_portfolio_value:,.2f}",
        'bh_total_return': f"{bh_total_return:.2%}",
        'bh_max_drawdown': f"{bh_max_drawdown:.2%}",
        'bh_volatility': f"{bh_volatility:.2%}",
        'bh_sharpe_ratio': f"{bh_sharpe_ratio:.2f}",
        'bh_number_of_trades': "N/A",  # Not applicable for buy and hold
        'bh_fees_paid': "N/A",         # Not applicable for buy and hold
    }
    return data, metrics

