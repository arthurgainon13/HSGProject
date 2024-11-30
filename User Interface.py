# ---------------------------------------------------------
# RSI Backtesting Tool - User Interface
#
# Language: Python
# Author: Samuel
# Date Created: November 28, 2024
# Description: This module defines the `BacktestApp` class, which is
#              responsible for the graphical user interface (GUI) of
#              the RSI Backtesting Tool. It handles user interactions
#              and integrates with the backtesting logic provided in
#              `backtest.py`.
# Assistance: GUI design structure and some comments were
#             inspired by ChatGPT, an AI language model by OpenAI.
# ---------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app_functions import get_historical_data, calculate_rsi, generate_signals, backtest_strategy, calculate_performance_metrics
from config import DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_COMPANIES


  class BacktestApp(tk.Tk):
      def __init__(self):
        super().__init__()
        self.title("RSI Backtesting Tool")
        self.geometry("1200x900")
        self.create_widgets()
        # Initialize placeholders for dynamic widgets
        self.canvas = None
        self.metrics_frame = None

    def create_widgets(self):
        # Main Frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Frame (Top Left)
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.grid(row=0, column=0, sticky='nw', padx=10, pady=10)

        # Summary Frame (Top Right)
        self.summary_frame = tk.Frame(self.main_frame)
        self.summary_frame.grid(row=0, column=1, sticky='ne', padx=10, pady=10)

        # Results Frame (Bottom, spans both columns)
        self.results_frame = tk.Frame(self.main_frame)
        self.results_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')

        # Configure row and column weights
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # Font for labels and entries (8pt)
        input_font = ("Helvetica", 8)

        # Input Widgets
        self.company_label = ttk.Label(self.input_frame, text="Select Company:", font=input_font)
        self.company_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Dropdown list of top companies (Removed Berkshire Hathaway)
        self.company_var = tk.StringVar()
        self.company_var.set('Apple Inc. (AAPL)')  # Default value
        companies = {
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
        self.ticker_map = companies  # Mapping for later use
        self.company_dropdown = ttk.OptionMenu(
            self.input_frame, self.company_var, self.company_var.get(), *companies.keys())
        self.company_dropdown.config(width=25)
        self.company_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Starting Capital
        self.capital_label = ttk.Label(self.input_frame, text="Starting Capital ($):", font=input_font)
        self.capital_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.capital_entry = ttk.Entry(self.input_frame, font=input_font)
        self.capital_entry.insert(0, "10000")
        self.capital_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Fee per Trade (%)
        self.fee_label = ttk.Label(self.input_frame, text="Fee per Trade (%):", font=input_font)
        self.fee_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.fee_entry = ttk.Entry(self.input_frame, font=input_font)
        self.fee_entry.insert(0, "0.1")  # Default fee is 0.1%
        self.fee_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # RSI Overbought Level
        self.overbought_label = ttk.Label(self.input_frame, text="RSI Overbought Level:", font=input_font)
        self.overbought_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.overbought_entry = ttk.Entry(self.input_frame, font=input_font)
        self.overbought_entry.insert(0, "70")
        self.overbought_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # RSI Oversold Level
        self.oversold_label = ttk.Label(self.input_frame, text="RSI Oversold Level:", font=input_font)
        self.oversold_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.oversold_entry = ttk.Entry(self.input_frame, font=input_font)
        self.oversold_entry.insert(0, "30")
        self.oversold_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        # Run Button
        self.run_button = ttk.Button(self.input_frame, text="Run Backtest", command=self.run_backtest)
        self.run_button.grid(row=5, column=0, columnspan=2, pady=10)

    def run_backtest(self):
        # Validate user inputs
        try:
            company_name = self.company_var.get()
            ticker = self.ticker_map[company_name]
            initial_capital = float(self.capital_entry.get())
            if initial_capital <= 0:
                raise ValueError("Starting capital must be positive.")
            fee_percentage = float(self.fee_entry.get()) / 100  # Convert to decimal
            if fee_percentage < 0:
                raise ValueError("Fee percentage cannot be negative.")
            rsi_overbought = float(self.overbought_entry.get())
            if not (0 < rsi_overbought < 100):
                raise ValueError("RSI Overbought level must be between 0 and 100.")
            rsi_oversold = float(self.oversold_entry.get())
            if not (0 < rsi_oversold < 100):
                raise ValueError("RSI Oversold level must be between 0 and 100.")
            if rsi_oversold >= rsi_overbought:
                raise ValueError("RSI Oversold level must be less than RSI Overbought level.")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        # Fetch and process data
        start_date = '2020-01-01'
        end_date = '2023-12-31'
        data = get_historical_data(ticker, start_date, end_date)
        if data.empty:
            messagebox.showinfo("No Data", "No data available for the selected parameters.")
            return
        data = calculate_rsi(data)
        data = generate_signals(data, rsi_overbought, rsi_oversold)
        data = backtest_strategy(data, initial_capital, fee_percentage)

        # Calculate performance metrics and update data with Buy and Hold values
        data, metrics = calculate_performance_metrics(data, initial_capital)

        # Display performance metrics
        self.display_metrics(metrics)

        # Plot results
        self.plot_results(data, company_name, rsi_overbought, rsi_oversold)

    def display_metrics(self, metrics):
        # Clear previous metrics if any
        if self.metrics_frame:
            self.metrics_frame.destroy()

        self.metrics_frame = tk.Frame(self.summary_frame)
        self.metrics_frame.pack(anchor='ne')

        label_font = ("Helvetica", 8)

        # Create a table with 7 rows and 3 columns
        headers = ["", "RSI-Strategy", "Buy-n-Hold"]
        metrics_labels = [
            "Portfolio Value",
            "Total Return",
            "Max. Drawdown",
            "Volatility",
            "Sharpe Ratio",
            "Fees Paid",
            "Number of Trades"
        ]

        # Create header row
        for col, header in enumerate(headers):
            header_label = tk.Label(self.metrics_frame, text=header, font=("Helvetica", 8, "bold"))
            header_label.grid(row=0, column=col, padx=5, pady=2)

        # Fill in the metrics
        for row, metric in enumerate(metrics_labels, start=1):
            # Metric name
            metric_label = tk.Label(self.metrics_frame, text=metric + ":", font=label_font)
            metric_label.grid(row=row, column=0, sticky='w', padx=5, pady=2)

            # Generate the key for metrics dictionary
            key = metric.lower().replace(" ", "_").replace(".", "")

            # RSI-Strategy value
            rsi_value = metrics.get(key, "")
            rsi_label = tk.Label(self.metrics_frame, text=rsi_value, font=label_font)
            rsi_label.grid(row=row, column=1, sticky='e', padx=5, pady=2)

            # Buy-n-Hold value
            bh_value = metrics.get("bh_" + key, "")
            bh_label = tk.Label(self.metrics_frame, text=bh_value, font=label_font)
            bh_label.grid(row=row, column=2, sticky='e', padx=5, pady=2)

    def plot_results(self, data, company_name, rsi_overbought, rsi_oversold):
        # Clear previous plots if any
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Create the figure and axes
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

        # Plot Stock Price
        ax1.plot(data.index, data['Close'], label=f"{company_name} Price")

        # Plot Buy/Sell Points when trades are executed
        trades = data[data['Trades'] != 0]
        ax1.plot(trades.loc[trades['Trades'] == 1].index,
                 trades['Close'][trades['Trades'] == 1], '^', markersize=10, color='g', label='Buy')
        ax1.plot(trades.loc[trades['Trades'] == -1].index,
                 trades['Close'][trades['Trades'] == -1], 'v', markersize=10, color='r', label='Sell')

        ax1.set_title(f"{company_name} Price with Buy/Sell Signals")
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Plot RSI
        ax2.plot(data.index, data['RSI'], label='RSI')
        ax2.axhline(y=rsi_overbought, color='r', linestyle='--', label=f'Overbought ({rsi_overbought})')
        ax2.axhline(y=rsi_oversold, color='g', linestyle='--', label=f'Oversold ({rsi_oversold})')
        ax2.set_title('Relative Strength Index (RSI)')
        ax2.set_ylabel('RSI')
        ax2.legend()
        ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Plot Portfolio Value
        ax3.plot(data.index, data['Portfolio Value'], label='RSI-Strategy Portfolio Value')
        ax3.plot(data.index, data['Buy and Hold Portfolio Value'], label='Buy-n-Hold Portfolio Value', linestyle='--')
        ax3.set_title('Portfolio Value Over Time')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Portfolio Value ($)')
        ax3.legend()
        ax3.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Make sure the borders of the plot are visible
        for ax in [ax1, ax2, ax3]:
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)

        plt.tight_layout()

        # Embed the figure in Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.results_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
