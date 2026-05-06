import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. TICKER INFO AND GROUPS
TICKER_INFO = {
    "IVV": "United States (iShares Core S&P 500 ETF)",
    "EWA": "Australia (iShares MSCI Australia ETF)",
    "EWO": "Austria (iShares MSCI Austria ETF)",
    "EWK": "Belgium (iShares MSCI Belgium ETF)",
    "EWZ": "Brazil (iShares MSCI Brazil ETF)",
    "EWC": "Canada (iShares MSCI Canada ETF)",
    "ECH": "Chile (iShares MSCI Chile ETF)",
    "MCHI": "China (iShares MSCI China ETF)",
    "EIS": "Israel (iShares MSCI Israel ETF)",
    "GXG": "Colombia (iShares MSCI Colombia ETF)",
    "INDA": "India (iShares MSCI India ETF)",
    "EWJ": "Japan (iShares MSCI Japan ETF)",
    "EWM": "Malaysia (iShares MSCI Malaysia ETF)",
    "ENZL": "New Zealand (iShares MSCI New Zealand ETF)",
    "EPOL": "Poland (iShares MSCI Poland ETF)",
    "EIRL": "Ireland (iShares MSCI Ireland ETF)",
    "EWQ": "France (iShares MSCI France ETF)",
    "EWU": "United Kingdom (iShares MSCI United Kingdom ETF)",
    "EZA": "South Africa (iShares MSCI South Africa ETF)",
    "EWL": "Switzerland (iShares MSCI Switzerland ETF)",
    "EWS": "Singapore (iShares MSCI Singapore ETF)",
    "EWT": "Taiwan (iShares MSCI Taiwan ETF)",
    "EWP": "Spain (iShares MSCI Spain ETF)",
    "EDEN": "Denmark (iShares MSCI Denmark ETF)",
    "EFNL": "Finland (iShares MSCI Finland ETF)",
    "EWG": "Germany (iShares MSCI Germany ETF)",
    "EWI": "Italy (iShares MSCI Italy ETF)",
    "EWW": "Mexico (iShares MSCI Mexico ETF)",
    "GREK": "Greece (iShares MSCI Greece ETF)",
    "EWY": "South Korea (iShares MSCI South Korea ETF)",
    "THD": "Thailand (iShares MSCI Thailand ETF)",
    "TUR": "Turkey (iShares MSCI Turkey ETF)",
    "EPHE": "Philippines (iShares MSCI Philippines ETF)",
    "EWH": "Hong Kong (iShares MSCI Hong Kong ETF)",
    "EIDO": "Indonesia (iShares MSCI Indonesia ETF)",
    "ENOR": "Norway (iShares MSCI Norway ETF)",
    "EWD": "Sweden (iShares MSCI Sweden ETF)",
    "EWN": "Netherlands (iShares MSCI Netherlands ETF)",
    "EPU": "Peru (iShares MSCI Peru ETF)"
}

GLOBAL_ECONOMIES_TICKERS = [
    "EIDO",
    "EWM",
    "EPHE",
    "THD",
    "EWH",
    "MCHI",
    "EWS",
    "TUR",
    "ECH",
    "EPOL",
    "EWQ",
    "EWU",
    "EWZ",
    "EIRL",
    "GXG",
    "INDA",
    "EWJ",
    "EWA",
    "ENZL",
    "EWP",
    "EWG",
    "EDEN",
    "EWK",
    "EWI",
    "EWW",
    "GREK",
    "EFNL",
    "ENOR",
    "EWY",
    "EZA",
    "EWL",
    "IVV",
    "EWT",
    "EWO",
    "EWD",
    "EWC",
    "EWN",
    "EPU"
]

import os

# Define the path to your Excel file
EXCEL_FILE_PATH = "etf_dash_May_06.xlsx"  # <-- Change this to your actual file name

if os.path.exists(EXCEL_FILE_PATH):
    # Read only the 'export' sheet from the Excel file
    ranks_df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='export')
    
    # Convert the columns into a dictionary: {'Indonesia': 1, 'Brazil': 2, ...}
    # (Ensure 'Country' and 'Rank' match the exact column headers in your Excel sheet!)
    COUNTRY_RANKS = dict(zip(ranks_df['Country'], ranks_df['Final Rank']))
else:
    st.error(f"Could not find {EXCEL_FILE_PATH}. Ranks will not be displayed.")
    COUNTRY_RANKS = {}

# Country rankings mapping
COUNTRY_RANKS = {
    "Indonesia": 1,
    "Brazil": 2,
    "India": 3,
    "Philippines": 4,
    "United Kingdom": 5,
    "France": 6,
    "Turkey": 7,
    "Hong Kong": 8,
    "Chile": 9,
    "Japan": 10,
    "Malaysia": 11,
    "Poland": 12,
    "Singapore": 13,
    "Thailand": 14,
    "China": 14,
    "South Korea": 16,
    "Mexico": 17,
    "United States": 18,
    "Australia": 19,
    "Colombia": 20,
    "Italy": 21,
    "Spain": 22,
    "Greece": 22,
    "South Africa": 24,
    "Norway": 25,
    "Ireland": 26,
    "New Zealand": 27,
    "Denmark": 28,
    "Germany": 29,
    "Canada": 30,
    "Belgium": 31,
    "Finland": 32,
    "Taiwan": 32,
    "Sweden": 34,
    "Peru": 35,
    "Netherlands": 36,
    "Switzerland": 37,
    "Austria": 38
}

# Create ticker-to-country mapping for rank lookup
TICKER_TO_COUNTRY = {}
for ticker, desc in TICKER_INFO.items():
    for country in COUNTRY_RANKS.keys():
        if country in desc:
            TICKER_TO_COUNTRY[ticker] = country
            break

GROUPS = {
    "Global Economies (USD Performance)": {ticker: TICKER_INFO[ticker] for ticker in GLOBAL_ECONOMIES_TICKERS
    },
    
    "India: Market Cross-Sections (INR)": {
        "^NSEI": "Nifty 50 (Large Cap)",
        "^NSMIDCP": "Nifty Midcap 100",
        "^CNXSMALL": "Nifty Smallcap 100",
        "^CRSLDX": "Nifty 500 (Broad)",
        "NIFTY_LQR_15.NS": "Nifty 50 Value 20",
        "MOMENTUM.NS": "Nifty 200 Momentum 30",
    },
    
    "India: Sectoral Breakdown (INR)": {
        "^NSEBANK": "Nifty Bank",
        "^CNXIT": "Nifty IT",
        "^CNXAUTO": "Nifty Auto",
        "^CNXPHARMA": "Nifty Pharma",
        "^CNXFMCG": "Nifty FMCG",
        "^CNXMETAL": "Nifty Metal",
        "^CNXREALTY": "Nifty Realty",
        "^CNXENERGY": "Nifty Energy",
        "^CNXPSUBANK": "PSU Bank Index",
        "^CNXINFRA": "Infrastructure"
    }
}

# 2. DATA ENGINE
@st.cache_data(ttl=3600)
def get_performance(ticker, description, selected_date):
    try:
        start_date = datetime(selected_date.year - 1, 1, 1) - timedelta(days=10)
        df = yf.download(ticker, start=start_date, end=selected_date + timedelta(days=1), 
                         interval='1d', progress=False, auto_adjust=True)
        
        if df.empty:
            return {'Ticker': ticker, 'Description': description, 'Error': 'No Data Found'}

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        price_col = 'Close'
        def get_safe_data(target_date):
            slice_df = df[:target_date]
            if slice_df.empty:
                return df[price_col].iloc[0], df.index[0].strftime('%Y-%m-%d')
            return slice_df[price_col].iloc[-1], slice_df.index[-1].strftime('%Y-%m-%d')

        current_price, actual_curr_date = get_safe_data(selected_date)
        price_jan, actual_jan_date = get_safe_data(datetime(selected_date.year, 1, 1))
        price_month, actual_month_date = get_safe_data(datetime(selected_date.year, selected_date.month, 1))
        price_year, actual_year_date = get_safe_data(datetime(selected_date.year - 1, selected_date.month, selected_date.day))
        
        target_locs = df.index.get_indexer([selected_date], method='pad')
        target_idx = target_locs[0] if target_locs[0] != -1 else (len(df) - 1)
        week_idx = max(0, target_idx - 5)
        price_week = df[price_col].iloc[week_idx]
        actual_week_date = df.index[week_idx].strftime('%Y-%m-%d')

        return {
            'Ticker': ticker,
            'Description': description,
            'Price': float(current_price),
            'Currency': "INR" if (".NS" in ticker or "^" in ticker) else "USD",
            '1Y': float(((current_price - price_year) / price_year) * 100),
            'YTD': float(((current_price - price_jan) / price_jan) * 100),
            'MTD': float(((current_price - price_month) / price_month) * 100),
            'Week': float(((current_price - price_week) / price_week) * 100),
            'dates': {'1Y_D': actual_year_date, 'YTD_D': actual_jan_date, 'MTD_D': actual_month_date, 'Wk_D': actual_week_date},
            'Rank': TICKER_TO_COUNTRY.get(ticker) and COUNTRY_RANKS.get(TICKER_TO_COUNTRY[ticker]),
            'Error': None
        }
    except Exception as e:
        return {'Ticker': ticker, 'Description': description, 'Error': str(e)}

# Fetch ticker info from yfinance
@st.cache_data(ttl=86400)
def get_ticker_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            'longName': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'website': info.get('website', 'N/A'),
            'marketCap': info.get('marketCap', 'N/A'),
            'dividendYield': info.get('dividendYield', 'N/A'),
            'trailingPE': info.get('trailingPE', 'N/A'),
            'beta': info.get('beta', 'N/A'),
            '52WeekHigh': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52WeekLow': info.get('fiftyTwoWeekLow', 'N/A'),
        }
    except Exception as e:
        return {'Error': str(e)}

# 3. DASHBOARD UI
st.set_page_config(page_title="Market Heatmap", layout="wide")
st.title("Market Performance Heatmap")

yesterday = datetime.now() - timedelta(days=1)
selected_date = st.date_input("Select 'As Of' Date:", value=yesterday, max_value=yesterday)
selected_dt = datetime.combine(selected_date, datetime.min.time())

# 4. RENDER LOOP
if st.button('Refresh Dashboard'):
    for group_name, tickers in GROUPS.items():
        results = [get_performance(t, desc, selected_dt) for t, desc in tickers.items()]
        
        processed_data = []
        for r in results:
            if r is None: continue
            if r.get('Error'):
                # Mark errors but we will filter these out later
                processed_data.append({
                    'Ticker': r['Ticker'], 'Description': r['Description'],
                    'Price': None, '1Y': None, 'YTD': None, 'MTD': None, 'Week': None, 'Rank': None, 'is_error': True
                })
            else:
                d = r['dates']
                processed_data.append({
                    'Ticker': r['Ticker'], 'Description': r['Description'],
                    'Price': r['Price'], '1Y': r['1Y'], 'YTD': r['YTD'], 'MTD': r['MTD'], 'Week': r['Week'], 'date_1Y': d["1Y_D"], 'date_YTD': d["YTD_D"], 'date_MTD': d["MTD_D"], 'date_Wk': d["Wk_D"],
                    'Rank': r.get('Rank'), 'is_error': False
                })
        
        if processed_data:
            full_df = pd.DataFrame(processed_data).set_index('Ticker')
            
            # --- THE KEY CHANGE: FILTER OUT ERRORS ---
            # This line removes any row where 'is_error' is True
            df = full_df[full_df['is_error'] == False].copy()
            
            if not df.empty:
                ref = df.iloc[0]
                cols_map = {
                    '1Y': f'1Y ({ref["date_1Y"]})',
                    'YTD': f'YTD ({ref["date_YTD"]})',
                    'MTD': f'MTD ({ref["date_MTD"]})',
                    'Week': f'Week ({ref["date_Wk"]})'
                }
                display_df = df.rename(columns=cols_map)
                heat_cols = list(cols_map.values())

                st.subheader(group_name)

# --- NEW Heatmap Logic (Auto-scaled per column, centered at 0) ---
                styled_df = display_df.style
                
                for col in heat_cols:
                    # Find the highest absolute percentage in this column to create bounds
                    col_max = display_df[col].abs().max()
                    
                    # Ensure limit is valid (prevents errors if a column is empty or all 0s)
                    limit = col_max if pd.notna(col_max) and col_max > 0 else 1
                    
                    # Apply gradient column-by-column with symmetric bounds (-limit to +limit)
                    styled_df = styled_df.background_gradient(
                        cmap='RdYlGn', 
                        subset=[col], 
                        vmin=-limit, 
                        vmax=limit
                    )

                # Render with sorting and symbol formatting
                col_config = {
                    "Price": st.column_config.NumberColumn("Price", format="%.2f"),
                    **{c: st.column_config.NumberColumn(c, format="%+.2f%%") for c in heat_cols},
                    "is_error": None, "date_1Y": None, "date_YTD": None, "date_MTD": None, "date_Wk": None, "Rank": None
                }
                if group_name == "Global Economies (USD Performance)":
                    col_config["Rank"] = st.column_config.NumberColumn("Rank")
                
                st.dataframe(
                    styled_df,
                    column_config=col_config,
                    use_container_width=False,
                    width="content",
                    height=(len(display_df) * 36) + 45
                )
                st.divider()