# ---------------------------------------------------------
# RSI Backtesting Tool
#
# Language: Python
# Description: This is the entry point of the RSI Backtesting Tool. It
#              initializes and launches the application by creating
#              an instance of the `BacktestApp` class from `app_ui.py`.
# Assistance: This structure and modularization were inspired by
#             ChatGPT, an AI language model by OpenAI.
# ---------------------------------------------------------

from subcode.App import BacktestApp

if __name__ == '__main__':
    app = BacktestApp()
    app.mainloop()

