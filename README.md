
# RSI Backtesting Tool

## Description
The RSI Backtesting Tool is a Python-based graphical user interface (GUI) application designed to simulate and evaluate a trading strategy based on the Relative Strength Index (RSI). The application provides users with the ability to:

- Select a company from a predefined list.
- Configure trading parameters such as starting capital, trading fees, and RSI thresholds.
- Backtest a trading strategy using historical market data.
- Compare the RSI-based strategy's performance with a simple "buy-and-hold" approach.

## Features
- Download historical stock data.
- Compute RSI indicator.
- Generate buy/sell signals.
- Backtest strategies and visualize results.

## Installation
Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
or if it doesn't work, try:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Usage
Run the application:
```bash
python main.py
```
or if it doesn't work, try:
```bash
python3 main.py
```

### Then when the Interface is opened:
1. Select a company from the dropdown menu.
2. Enter the desired parameters:
-   Starting Capital: Initial amount of money for trading.
-   Fee per Trade: Percentage fee charged for each transaction.
-   RSI Overbought Level: RSI value above which the stock is considered overbought (default: 70).
-   RSI Oversold Level: RSI value below which the stock is considered oversold (default: 30).
3. Click the "Run Backtest" button to start the simulation.
4. Review the performance metrics and visualizations in the results section.


## Dependencies
See `requirements.txt` for a list of required libraries.

