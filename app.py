import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

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
    "EIDO", "EWM", "EPHE", "THD", "EWH", "MCHI", "EWS", "TUR", "ECH", "EPOL",
    "EWQ", "EWU", "EWZ", "EIRL", "GXG", "INDA", "EWJ", "EWA", "ENZL", "EWP",
    "EWG", "EDEN", "EWK", "EWI", "EWW", "GREK", "EFNL", "ENOR", "EWY", "EZA",
    "EWL", "IVV", "EWT", "EWO", "EWD", "EWC", "EWN", "EPU"
]

# Load Ranks from Excel
EXCEL_FILE_PATH = "etf_dash_May_06.xlsx" 
if os.path.exists(EXCEL_FILE_PATH):
    ranks_df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='export')
    COUNTRY_RANKS = dict(zip(ranks_df['Country'], ranks_df['Final Rank']))
else:
    st.error(f"Could not find {EXCEL_FILE_PATH}. Ranks will not be displayed.")
    COUNTRY_RANKS = {}

# Create ticker-to-country mapping
TICKER_TO_COUNTRY = {}
for ticker, desc in TICKER_INFO.items():
    for country in COUNTRY_RANKS.keys():
        if country in desc:
            TICKER_TO_COUNTRY[ticker] = country
            break

GROUPS = {
    "Global Economies (USD Performance)": {ticker: TICKER_INFO[ticker] for ticker in GLOBAL_ECONOMIES_TICKERS},
    "India: Market Cross-Sections (INR)": {
        "^NSEI": "Nifty 50 (Large Cap)",
        "^NSMIDCP": "Nifty Midcap 100",
        "^CNXSMALL": "Nifty Smallcap 100",
        "^CRSLDX": "Nifty 500 (Broad)",
        "NIFTY_LQR_15.NS": "Nifty 50 Value 20",
        "MOMENTUM.NS": "Nifty 200 Momentum 30",
    },
    "India: Sectoral Breakdown (INR)": {
        "^NSEBANK": "Nifty Bank", "^CNXIT": "Nifty IT", "^CNXAUTO": "Nifty Auto",
        "^CNXPHARMA": "Nifty Pharma", "^CNXFMCG": "Nifty FMCG", "^CNXMETAL": "Nifty Metal",
        "^CNXREALTY": "Nifty Realty", "^CNXENERGY": "Nifty Energy", 
        "^CNXPSUBANK": "PSU Bank Index", "^CNXINFRA": "Infrastructure"
    }
}

# 2. DATA ENGINE
@st.cache_data(ttl=3600)
def get_performance(ticker, description, selected_date):
    try:
        start_date = datetime(selected_date.year - 1, 1, 1) - timedelta(days=40)
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
        price_1m, actual_1m_date = get_safe_data(selected_date - timedelta(days=30))
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
            '1Y': float(((current_price - price_year) / price_year) * 100),
            'YTD': float(((current_price - price_jan) / price_jan) * 100),
            'MTD': float(((current_price - price_month) / price_month) * 100),
            '1M': float(((current_price - price_1m) / price_1m) * 100),
            'Week': float(((current_price - price_week) / price_week) * 100),
            'dates': {
                '1Y_D': actual_year_date, 'YTD_D': actual_jan_date, 
                'MTD_D': actual_month_date, '1M_D': actual_1m_date, 'Wk_D': actual_week_date
            },
            'Rank': TICKER_TO_COUNTRY.get(ticker) and COUNTRY_RANKS.get(TICKER_TO_COUNTRY[ticker]),
            'Error': None
        }
    except Exception as e:
        return {'Ticker': ticker, 'Description': description, 'Error': str(e)}

# 3. DASHBOARD UI
st.set_page_config(page_title="Market Heatmap", layout="wide")
st.title("Market Performance Heatmap")

# Set default to 2 days ago for Streamlit Cloud reliability
default_date = datetime.now() - timedelta(days=2)
selected_date = st.date_input("Select 'As Of' Date:", value=default_date, max_value=default_date)
selected_dt = datetime.combine(selected_date, datetime.min.time())

# 4. RENDER LOOP
if st.button('Refresh Dashboard'):
    for group_name, tickers in GROUPS.items():
        results = [get_performance(t, desc, selected_dt) for t, desc in tickers.items()]
        
        processed_data = []
        for r in results:
            if r is None: continue
            if r.get('Error'):
                processed_data.append({
                    'Ticker': r['Ticker'], 'Description': r['Description'], 'is_error': True
                })
            else:
                d = r['dates']
                processed_data.append({
                    'Ticker': r['Ticker'], 'Description': r['Description'],
                    'Price': r['Price'], '1Y': r['1Y'], 'YTD': r['YTD'], 'MTD': r['MTD'], 
                    '1M': r['1M'], 'Week': r['Week'],
                    'date_1Y': d["1Y_D"], 'date_YTD': d["YTD_D"], 'date_MTD': d["MTD_D"], 
                    'date_1M': d["1M_D"], 'date_Wk': d["Wk_D"],
                    'Rank': r.get('Rank'), 'is_error': False
                })
        
        if processed_data:
            full_df = pd.DataFrame(processed_data).set_index('Ticker')
            df = full_df[full_df['is_error'] == False].copy()
            
            if not df.empty:
                ref = df.iloc[0]
                cols_map = {
                    '1Y': f'1Y ({ref["date_1Y"]})',
                    'YTD': f'YTD ({ref["date_YTD"]})',
                    'MTD': f'MTD ({ref["date_MTD"]})',
                    '1M': f'1M ({ref["date_1M"]})',
                    'Week': f'Week ({ref["date_Wk"]})'
                }
                display_df = df.rename(columns=cols_map)
                heat_cols = list(cols_map.values())

                st.subheader(group_name)

                # Custom Red/Green Styling Logic
                def style_performance(val, col_max):
                    if pd.isna(val) or col_max == 0: return ''
                    intensity = min(abs(val) / col_max, 1.0)
                    alpha = 0.1 + (intensity * 0.7) 
                    if val < 0:
                        return f'background-color: rgba(255, 75, 75, {alpha});'
                    else:
                        return f'background-color: rgba(0, 128, 0, {alpha});'

                styled_df = display_df.style
                for col in heat_cols:
                    c_max = display_df[col].abs().max()
                    styled_df = styled_df.map(style_performance, col_max=c_max, subset=[col])

                # Column configuration
                col_config = {
                    "Price": st.column_config.NumberColumn("Price", format="%.2f"),
                    **{c: st.column_config.NumberColumn(c, format="%+.2f%%") for c in heat_cols},
                    "is_error": None, "date_1Y": None, "date_YTD": None, 
                    "date_MTD": None, "date_1M": None, "date_Wk": None, "Rank": None
                }
                
                if group_name == "Global Economies (USD Performance)":
                    col_config["Rank"] = st.column_config.NumberColumn("Rank", format="%d")
                
                st.dataframe(
                    styled_df,
                    column_config=col_config,
                    use_container_width=False,
                    width="content",
                    height=(len(display_df) * 36) + 45
                )
                st.divider()