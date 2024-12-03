import tkinter as tk
import subcode.Configuration  # Import the configuration module
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
            # Retrieve the selected company name from the dropdown
            company_name = self.company_var.get()
            
            # Map the selected company name to its stock ticker
            ticker = self.ticker_map[company_name]

            # Get the starting capital from the input field and convert to a float
            initial_capital = float(self.capital_entry.get())
            if initial_capital <= 0:
                raise ValueError("Starting capital must be positive.") # Ensure positive capital
            fee_percentage = float(self.fee_entry.get()) / 100  # Get the trading fee as percentage and convert to decimal
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
