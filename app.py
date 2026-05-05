import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. UPDATE YOUR TICKERS HERE
# Add or remove any country or sector ETF ticker below
TICKERS = [
    'SPY', 'QQQ', 'IJR', 'EWA', 'EWZ', 'EWC', 
    'ASHR', 'EWQ', 'EWG', 'EWH', 'INDA', 'EWI', 
    'EWJ', 'EWW', 'EWP', 'EIS', 'EWU', 'XLK', 'XLF'
]

# # Ticker: Description
# GROUPS = {
#     "US Related": {
#         "SPY": "S&P 500",
#         "QQQ": "Nasdaq 100",
#         "IJR": "S&P Smallcap 600",
#         "DVY": "DJ Dividend"
#     },
#     "Global": {
#         "EWA": "Australia",
#         "EWZ": "Brazil",
#         "EWC": "Canada",
#         "EWG": "Germany"
#     },
#     "Sectors": {
#         "XLK": "Technology",
#         "XLF": "Financials",
#         "XLV": "Health Care"
#     }
# }

def get_performance(ticker):
    end_date = datetime.now()
    # Pulling a bit more data to ensure we have enough for 
    # week-over-week and month-over-month calculations
    start_date = datetime(end_date.year, 1, 1) - timedelta(days=10)
    
    # auto_adjust=True will automatically handle the dividend adjustment 
    # and rename the column to 'Close'
    df = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False, auto_adjust=True)
    
    if df.empty:
        return {'Ticker': ticker, 'YTD (%)': 0, 'MTD (%)': 0, 'Week (%)': 0}

    # Since auto_adjust=True, we look for 'Close' (which is now the adjusted price)
    # If using yfinance v0.2.40+, the column might be nested, so we ensure it's flat
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Use 'Close' as the primary price source for consistency
    price_col = 'Close'
    
    current_price = df[price_col].iloc[-1]
    
    # Calculate indices
    # .asof finds the closest available trading day price
    jan_1 = df[price_col].asof(datetime(end_date.year, 1, 1))
    month_start = df[price_col].asof(datetime(end_date.year, end_date.month, 1))
    
    # Grab price from 5 trading days ago
    week_ago = df[price_col].iloc[-5] if len(df) >= 5 else df[price_col].iloc[0]

    # Calculate % Returns
    ytd = ((current_price - jan_1) / jan_1) * 100
    mtd = ((current_price - month_start) / month_start) * 100
    week = ((current_price - week_ago) / week_ago) * 100
    
    return {
        'Ticker': ticker,
        # 'Description': description,
        'YTD (%)': round(float(ytd), 2),
        'MTD (%)': round(float(mtd), 2),
        'Week (%)': round(float(week), 2)-5.3
    }

st.set_page_config(page_title="Global Asset Heatmap", layout="wide")
st.title("Asset Class Performance (Dividend Adjusted)")

if st.button('Refresh Data'):
    data = [get_performance(t) for t in TICKERS]
    df_final = pd.DataFrame(data).set_index('Ticker')

    # Apply Heatmap Styling (Red-Yellow-Green)
    styled_df = df_final.style.format("{:.1f}%").background_gradient(cmap='RdYlGn', axis=0, vmin=-5, vmax=5)
    
    st.table(styled_df)
else:
    st.write("Click the button to load live market data.")