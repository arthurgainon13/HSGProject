# ---------------------------------------------------------
# RSI Backtesting Tool - Main Application
#
# Language: Python
# Author: Samuel
# Date Created: November 28, 2024
# Description: This is the entry point of the RSI Backtesting Tool. It
#              initializes and launches the application by creating
#              an instance of the `BacktestApp` class from `app_ui.py`.
# Assistance: This structure and modularization were inspired by
#             ChatGPT, an AI language model by OpenAI.


from subcode.Main import BacktestApp

if __name__ == '__main__':
    app = BacktestApp()
    app.mainloop()


