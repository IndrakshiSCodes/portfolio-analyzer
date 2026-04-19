# folio. — Stock Portfolio Analyzer

A Python-based portfolio analysis tool built with Streamlit. Analyze NSE/BSE/global stocks, track performance against NIFTY 50, and assess risk metrics.

## Features
- Live stock data via Yahoo Finance
- Portfolio vs NIFTY 50 benchmark comparison
- Key metrics: Total Return, CAGR, Sharpe Ratio, Max Drawdown
- Individual stock breakdown with weights
- Drawdown chart + correlation heatmap

## Tech Stack
`Python` · `Streamlit` · `yfinance` · `pandas` · `numpy` · `plotly` · `seaborn`

## Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Usage
- Enter NSE tickers with `.NS` suffix e.g. `RELIANCE.NS, TCS.NS`
- For US stocks just use ticker e.g. `AAPL, MSFT`
- Set date range and investment amount
- Toggle NIFTY 50 comparison on/off
