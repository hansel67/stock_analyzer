import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yfinance as yf
import pandas as pd
import numpy as np
import scipy.stats as stats
from arch import arch_model
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

def fetch_stock_data(ticker):
    end_date = pd.to_datetime('now')
    start_date = end_date - pd.DateOffset(years=10)
    data = yf.download(ticker, start=start_date, end=end_date)

    # Drop missing values

    data.dropna(inplace=True)
    return data

def plot_stock_data(data, ticker, frame):

    # Stock Closing Prices Plot and Distribution Analysis Plot
    fig, [[ax1, ax2], [ax3, ax4]] = plt.subplots(2, 2, figsize=(10, 7))

    # Plotting Stock Closing Prices
    ax1.plot(data.index, data['Close'].values)
    ax1.set_title(ticker+' Closing Prices')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')

    # Plotting Distribution Analysis
    data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
    mean_log_return = data['Log_Returns'].mean()
    std_log_return = data['Log_Returns'].std()
    data.dropna(inplace = True)

    #GARCH Model
    garch_model = arch_model(data['Log_Returns'])
    garch_fit = garch_model.fit()
    data['Volatility'] = garch_fit.conditional_volatility

    ax3.plot(data['Volatility'], label='Conditional Volatility', color='blue')
    ax3.set_title('GARCH Model - Conditional Volatility')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Volatility')

    # Histogram of Actual Log Returns
    ax4.hist(data['Log_Returns'], bins=30, density=True, alpha=0.6, color='g')

    # Normal Distribution Curve
    xmin, xmax = ax4.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mean_log_return, std_log_return)
    ax4.plot(x, p, 'k', linewidth=2)
    title = f'Log Returns Distribution: μ = {mean_log_return:.6f},  σ = {std_log_return:.6f}'
    ax4.set_title(title)
    ax4.set_xlabel('Log Returns')
    ax4.set_ylabel('Density')

    # Feature Engineering
    X = data[['Close', 'Volatility']].values[:-1]
    y = data['Close'].values[1:]

    # Data Normalization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Splitting data for training and testing
    train_ratio = 0.8
    split_index = int(len(X_scaled) * train_ratio)
    X_train, X_test = X_scaled[:split_index], X_scaled[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    # Model Building - Using Random Forest for demonstration
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Model Evaluation
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    # Actual vs Predicted Prices
    ax2.plot(y_test, label='Actual Price', color='blue')
    ax2.plot(predictions, label='Predicted Price', color='red')
    ml_title = f'Random Forest: MSE = {mse:.6f},  r² = {r2:.6f}'
    ax2.set_title(ml_title)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Price')

    # Spacing graphs
    fig.tight_layout(pad = 2)

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    canvas.draw()

def analyze():
    for widget in frame.winfo_children():
        widget.destroy()

    ticker = entry.get().upper()
    data = fetch_stock_data(ticker)
    plot_stock_data(data, ticker, frame)

# Termintates program upon closing window
def on_closing():
    print("Closing application")
    root.destroy()  # Destroy the window
    sys.exit()      # Exit the program

# Set up the main window
root = tk.Tk()
root.title("Stock Data Analyzer")
root.state('zoomed')
root.protocol("WM_DELETE_WINDOW", on_closing)

# Entry widget for ticker symbol
entry = tk.Entry(root)
entry.pack()

# Analyze button
analyze_button = tk.Button(root, text="Analyze", command=analyze)
analyze_button.pack()

# Frame for the plots
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
