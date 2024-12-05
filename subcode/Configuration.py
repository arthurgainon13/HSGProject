# ---------------------------------------------------------
# RSI Backtesting Tool
#
# Language: Python
# Description: This is the configuration part of the code. 
# There you can adapat your analysed companies as well as Dates of analysis
# Assistance: This structure and modularization were inspired by
#             ChatGPT, an AI language model by OpenAI.
# ---------------------------------------------------------


# List of top companies and their tickers
COMPANIES = {
    'Apple Inc. (AAPL)': 'AAPL',
    'Microsoft Corporation (MSFT)': 'MSFT',
    'Amazon.com, Inc. (AMZN)': 'AMZN',
    'Alphabet Inc. Class A (GOOGL)': 'GOOGL',
    'Alphabet Inc. Class C (GOOG)': 'GOOG',
    'Meta Platforms, Inc. (META)': 'META',  # Formerly Facebook (FB)
    'Tesla, Inc. (TSLA)': 'TSLA',
    'NVIDIA Corporation (NVDA)': 'NVDA',
    'JPMorgan Chase & Co. (JPM)': 'JPM'
}

# Default start and end dates for fetching historical data
START_DATE = '2020-01-01'
END_DATE = '2023-12-31'
