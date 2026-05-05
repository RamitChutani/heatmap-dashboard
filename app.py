import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. THE DICTIONARY (PRESERVED)
GROUPS = {
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
    },
    "Global Economies (USD Performance)": {
        "SPY": "USA (S&P 500)",
        "QQQ": "USA (Nasdaq 100)",
        "INDA": "India (MSCI India ETF)",
        "EWJ": "Japan (MSCI Japan)",
        "EWG": "Germany (MSCI Germany)",
        "EWU": "United Kingdom (MSCI UK)",
        "EWQ": "France (MSCI France)",
        "EWA": "Australia (MSCI Australia)",
        "EWC": "Canada (MSCI Canada)",
        "EWI": "Italy (MSCI Italy)",
        "EWZ": "Brazil (MSCI Brazil)",
        "MCHI": "China (MSCI China)",
        "EWY": "South Korea (MSCI South Korea)",
        "EWW": "Mexico (MSCI Mexico)",
        "EWT": "Taiwan (MSCI Taiwan)",
        "EWP": "Spain (MSCI Spain)",
        "EWN": "Netherlands (MSCI Netherlands)",
        "EWS": "Singapore (MSCI Singapore)",
        "EWD": "Sweden (MSCI Sweden)",
        "EWL": "Switzerland (MSCI Switzerland)",
        "EIDO": "Indonesia (MSCI Indonesia)",
        "TUR": "Turkey (MSCI Turkey)",
        "THD": "Thailand (MSCI Thailand)",
        "EZA": "South Africa (MSCI South Africa)",
        "EIS": "Israel (MSCI Israel)",
        "GREK": "Greece (MSCI Greece)",
        "EPOL": "Poland (MSCI Poland)",
        "ENZL": "New Zealand (MSCI NZ)",
        "EPU": "Peru (MSCI Peru)",
        "EWM": "Malaysia (MSCI Malaysia)",
        "EDEN": "Denmark (MSCI Denmark)",
        "EFNL": "Finland (MSCI Finland)",
        "EWK": "Belgium (MSCI Belgium)",
        "NORW": "Norway (MSCI Norway)",
        "EIRL": "Ireland (MSCI Ireland)",
        "GXG": "Colombia (MSCI Colombia)",
        "VNM": "Vietnam (MSCI Vietnam)",
        "KSA": "Saudi Arabia (MSCI KSA)",
        "UAE": "United Arab Emirates (MSCI UAE)",
        "EGPT": "Egypt (MSCI Egypt)",
        "AFK": "Africa (Broad Market)"
    }
}

# 2. DATA ENGINE
@st.cache_data(ttl=3600)
def get_performance(ticker, description, selected_date):
    try:
        start_date = datetime(selected_date.year, 1, 1) - timedelta(days=10)
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
            'YTD': float(((current_price - price_jan) / price_jan) * 100),
            'MTD': float(((current_price - price_month) / price_month) * 100),
            'Week': float(((current_price - price_week) / price_week) * 100),
            'dates': {'YTD_D': actual_jan_date, 'MTD_D': actual_month_date, 'Wk_D': actual_week_date},
            'Error': None
        }
    except Exception as e:
        return {'Ticker': ticker, 'Description': description, 'Error': str(e)}

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
                    'Price': None, 'YTD': None, 'MTD': None, 'Week': None, 'is_error': True
                })
            else:
                d = r['dates']
                processed_data.append({
                    'Ticker': r['Ticker'], 'Description': r['Description'],
                    'Price': r['Price'], 'YTD': r['YTD'], 'MTD': r['MTD'], 'Week': r['Week'],
                    'CCY': r['Currency'], 'date_YTD': d["YTD_D"], 'date_MTD': d["MTD_D"], 'date_Wk': d["Wk_D"],
                    'is_error': False
                })
        
        if processed_data:
            full_df = pd.DataFrame(processed_data).set_index('Ticker')
            
            # --- THE KEY CHANGE: FILTER OUT ERRORS ---
            # This line removes any row where 'is_error' is True
            df = full_df[full_df['is_error'] == False].copy()
            
            if not df.empty:
                ref = df.iloc[0]
                cols_map = {
                    'YTD': f'YTD ({ref["date_YTD"]})',
                    'MTD': f'MTD ({ref["date_MTD"]})',
                    'Week': f'Week ({ref["date_Wk"]})'
                }
                display_df = df.rename(columns=cols_map)
                heat_cols = list(cols_map.values())

                st.subheader(group_name)

                # Heatmap Logic (Gradient)
                styled_df = display_df.style.background_gradient(
                    cmap='RdYlGn', axis=None, vmin=-5, vmax=5, subset=heat_cols
                )

                # Render with sorting and symbol formatting
                st.dataframe(
                    styled_df,
                    column_config={
                        "Price": st.column_config.NumberColumn("Price", format="%.2f"),
                        "CCY": st.column_config.TextColumn("Currency"),
                        **{c: st.column_config.NumberColumn(c, format="%+.2f%%") for c in heat_cols},
                        "is_error": None, "date_YTD": None, "date_MTD": None, "date_Wk": None
                    },
                    use_container_width=False,
                    width="content",
                    height=(len(display_df) * 36) + 45
                )
                st.divider()