# ---------------------------------------------------------
# RSI Backtesting Tool
#
# Language: Python
# Description: This is the entry point of the RSI Backtesting Tool. It
#              initializes and launches the application by creating
#              an instance of the `BacktestApp` class from `app_ui.py`.
# Assistance: This structure and modularization were inspired by
#             ChatGPT, an AI language model by OpenAI.

# Import necessary libraries and modules for the application:
# - tkinter for GUI elements
# - matplotlib for data visualization
# - subcode.Configuration for custom configurations
import tkinter as tk
import subcode.Configuration  # Import the configuration module
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from subcode.Preparation import get_historical_data, calculate_rsi, generate_signals, backtest_strategy, calculate_performance_metrics

# Main Application Class
class BacktestApp(tk.Tk):
    def __init__(self):
        super().__init__() # Initialize the tkinter parent class
        self.title("RSI Backtesting Tool") # Set the window title
        self.geometry("1200x900") # Set the window size
        self.create_widgets()  # Call the method to create widgets for the application
        # Initialize placeholders for dynamic widgets
        self.canvas = None # Placeholder for graphical canvas
        self.metrics_frame = None # Placeholder for the metrics display frame

    def create_widgets(self):
        # Create and configure the main frame that holds all subcomponents
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True) # Fill both dimensions and allow resizing

        # Input Frame (for user input, located at the top left)
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.grid(row=0, column=0, sticky='nw', padx=10, pady=10) # Set the parameter

        # Summary Frame (for displaying summary metrics, located at the top right)
        self.summary_frame = tk.Frame(self.main_frame)
        self.summary_frame.grid(row=0, column=1, sticky='ne', padx=10, pady=10) # Set the parameter

        # Results Frame (for displaying graphical results, spans the bottom of the window)
        self.results_frame = tk.Frame(self.main_frame)
        self.results_frame.grid(row=1, column=0, columnspan=2, sticky='nsew') # Set the parameter

        # Configure row and column weights for proper resizing behavior
        self.main_frame.rowconfigure(1, weight=1) # Set the parameter
        self.main_frame.columnconfigure(0, weight=1) # Input/summary frames grow horizontally
        self.main_frame.columnconfigure(1, weight=1)

        # Define a consistent font for input widgets (8-point Helvetica)
        input_font = ("Helvetica", 8)

        # Input Widgets
        # Label and dropdown for selecting a company
        self.company_label = ttk.Label(self.input_frame, text="Select Company:", font=input_font)
        self.company_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Dropdown list for companies, sourced from the configuration file
        self.company_var = tk.StringVar()
        self.company_var.set(next(iter(subcode.Configuration.COMPANIES.keys())))  # Default to the first company
        self.ticker_map = subcode.Configuration.COMPANIES  # Map for ticker lookups
        self.company_dropdown = ttk.OptionMenu(
            self.input_frame, self.company_var, self.company_var.get(), *subcode.Configuration.COMPANIES.keys())
        self.company_dropdown.config(width=25)  # Set dropdown width
        self.company_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Entry for starting capital
        self.capital_label = ttk.Label(self.input_frame, text="Starting Capital ($):", font=input_font)
        self.capital_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.capital_entry = ttk.Entry(self.input_frame, font=input_font)
        self.capital_entry.insert(0, "10000")  # Default value: $10,000
        self.capital_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)


        # Entry for trading fee percentage
        self.fee_label = ttk.Label(self.input_frame, text="Fee per Trade (%):", font=input_font)
        self.fee_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.fee_entry = ttk.Entry(self.input_frame, font=input_font)
        self.fee_entry.insert(0, "0.1")  # Default value: 0.1% fee
        self.fee_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Entry for RSI overbought level
        self.overbought_label = ttk.Label(self.input_frame, text="RSI Overbought Level:", font=input_font)
        self.overbought_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.overbought_entry = ttk.Entry(self.input_frame, font=input_font)
        self.overbought_entry.insert(0, "70")  # Default value: 70
        self.overbought_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # Entry for RSI oversold level
        self.oversold_label = ttk.Label(self.input_frame, text="RSI Oversold Level:", font=input_font)
        self.oversold_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.oversold_entry = ttk.Entry(self.input_frame, font=input_font)
        self.oversold_entry.insert(0, "30")  # Default value: 30
        self.oversold_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        # Button to run the backtest
        self.run_button = ttk.Button(self.input_frame, text="Run Backtest", command=self.run_backtest)
        self.run_button.grid(row=5, column=0, columnspan=2, pady=10)  # Spans both columns

        # Button to exit the application
        self.exit_button = ttk.Button(self.input_frame, text="Exit", command=self.exit_application)
        self.exit_button.grid(row=6, column=0, columnspan=2, pady=10) # Place the button in the grid layout

    def exit_application(self):
        self.quit()  # Gracefully close the application
        self.destroy()  # Destroy all widgets and exit
    
    def run_backtest(self):
        # Validate user inputs
        try:
            company_name = self.company_var.get() # Retrieve the selected company name from the dropdown
            ticker = self.ticker_map[company_name] # Map the selected company name to its stock ticker
            initial_capital = float(self.capital_entry.get()) # Get the starting capital from the input field and convert to a float
            if initial_capital <= 0:
                raise ValueError("Starting capital must be positive.") # Ensure positive capital
            fee_percentage = float(self.fee_entry.get()) / 100   # Get the trading fee as percentage and convert to decimal
            if fee_percentage < 0:
                raise ValueError("Fee percentage cannot be negative.") # Ensure fee is non-negative
            # Get the RSI overbought treshold and validate its range
            rsi_overbought = float(self.overbought_entry.get())
            if not (0 < rsi_overbought < 100):
                raise ValueError("RSI Overbought level must be between 0 and 100.")
            # Get the RSI oversold threshold and validate its range
            rsi_oversold = float(self.oversold_entry.get())
            if not (0 < rsi_oversold < 100):
                raise ValueError("RSI Oversold level must be between 0 and 100.")
            # Ensure that the oversold level is less than the overbought level
            if rsi_oversold >= rsi_overbought:
                raise ValueError("RSI Oversold level must be less than RSI Overbought level.")
        except ValueError as e:
            # Display an error message if input validation fails
            messagebox.showerror("Input Error", str(e))
            return

        # Use the configuration values for start and end dates
        start_date = subcode.Configuration.START_DATE # Fetch the start date from the configuration
        end_date = subcode.Configuration.END_DATE # Fetch the end date from the configuration
        data = get_historical_data(ticker, start_date, end_date) # Retrieve historical stock data for the selected ticker and date range
        # Check if the data is empthy (no historical data)
        if data.empty:
            messagebox.showinfo("No Data", "No data available for the selected parameters.")
            return
        data = calculate_rsi(data)
        data = generate_signals(data, rsi_overbought, rsi_oversold)
        data = backtest_strategy(data, initial_capital, fee_percentage) # Perform backtesting of the strategy

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

        self.metrics_frame = tk.Frame(self.summary_frame) # Create a new frame to hold the metrics table
        self.metrics_frame.pack(anchor='ne') # Align the frame to the top-right of the parent frame

        label_font = ("Helvetica", 8) # Set font for the table text

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
            # Display Metric name
            metric_label = tk.Label(self.metrics_frame, text=metric + ":", font=label_font)
            metric_label.grid(row=row, column=0, sticky='w', padx=5, pady=2)

            # Generate the key for metrics dictionary
            key = metric.lower().replace(" ", "_").replace(".", "")

            # Fetch and display RSI-Strategy value
            rsi_value = metrics.get(key, "")
            rsi_label = tk.Label(self.metrics_frame, text=rsi_value, font=label_font)
            rsi_label.grid(row=row, column=1, sticky='e', padx=5, pady=2)

            # Fetch and display Buy-n-Hold value
            bh_value = metrics.get("bh_" + key, "")
            bh_label = tk.Label(self.metrics_frame, text=bh_value, font=label_font)
            bh_label.grid(row=row, column=2, sticky='e', padx=5, pady=2)

    def plot_results(self, data, company_name, rsi_overbought, rsi_oversold):
        # Clear previous plots if any exist
        if self.canvas:
            self.canvas.get_tk_widget().destroy() # Remove the previous widget

        # Create a figure with 3 subplots arranged vertically
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

        # Plot 1: Stock Price with Buy/Sell signals
        ax1.plot(data.index, data['Close'], label=f"{company_name} Price") # Plot the stock's closing price

        # Extract the rows where trades occured
        trades = data[data['Trades'] != 0]
        # Plot Buy signals (indicated with green upward arrows)
        ax1.plot(trades.loc[trades['Trades'] == 1].index,
                 trades['Close'][trades['Trades'] == 1], '^', markersize=10, color='g', label='Buy')
        # Plot Sell signals (indicated with red downward arrows)
        ax1.plot(trades.loc[trades['Trades'] == -1].index,
                 trades['Close'][trades['Trades'] == -1], 'v', markersize=10, color='r', label='Sell')

        # Customize the plot's title, labels, legend, and grid
        ax1.set_title(f"{company_name} Price with Buy/Sell Signals")
        ax1.set_ylabel('Price ($)')
        ax1.legend() # Add a legend for Buy/Sell markers
        ax1.grid(True, which='both', linestyle='--', linewidth=0.5) # Display grid lines for better readability

        # Plot 2: RSI with Overbought/Oversold thresholds
        ax2.plot(data.index, data['RSI'], label='RSI') # Plot the RSI values
        # Add horizontal lines for the overbought and oversold thresholds
        ax2.axhline(y=rsi_overbought, color='r', linestyle='--', label=f'Overbought ({rsi_overbought})')
        ax2.axhline(y=rsi_oversold, color='g', linestyle='--', label=f'Oversold ({rsi_oversold})')
        # Customize the plot's title, labels, legend, and grid
        ax2.set_title('Relative Strength Index (RSI)')
        ax2.set_ylabel('RSI')
        ax2.legend()  # Add a legend for the RSI thresholds
        ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Plot 3: Portfolio Value over time
        ax3.plot(data.index, data['Portfolio Value'], label='RSI-Strategy Portfolio Value') # RSI strategy portfolio
        ax3.plot(data.index, data['Buy and Hold Portfolio Value'], label='Buy-n-Hold Portfolio Value', linestyle='--') # Buy-and-Hold strategy portfolio
        # Customize the plot's title labels, legend, and grid
        ax3.set_title('Portfolio Value Over Time')
        ax3.set_xlabel('Date') # x-axis shared by all subplots
        ax3.set_ylabel('Portfolio Value ($)')
        ax3.legend() # Add a legend for portfolio value comparison
        ax3.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Make sure the borders of the plot are visible
        for ax in [ax1, ax2, ax3]:
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)

        # Adjust the layout to prevent overlap of subplots
        plt.tight_layout()

        # Embed the Matplotlib figure in the Tkinter GUI
        self.canvas = FigureCanvasTkAgg(fig, master=self.results_frame) # Attach the figure to the results frame
        self.canvas.draw() # Render the canvas
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True) # Pack the canvas in the GUI

# Run the application
if __name__ == '__main__':
    app = BacktestApp()
    app.mainloop()
