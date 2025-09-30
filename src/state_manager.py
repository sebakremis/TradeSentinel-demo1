# src/state_manager.py
import streamlit as st
import pandas as pd
from ensure_data import ensure_prices

DEFAULT_PORTFOLIO = pd.DataFrame({
    "Ticker": ["NVDA", "MSFT", "GOOGL"],
    "Quantity": [100, 30, 70]
})

def get_interval_settings(period):
    """Return allowed intervals and default index based on selected period."""
    interval_map = {
        "1d": ["1m", "5m", "15m", "30m", "1h"],
        "5d": ["5m", "15m", "30m", "1h", "1d"],
        "1mo": ["15m", "30m", "1h", "1d", "1wk"],
        "3mo": ["15m", "30m", "1h", "1d", "1wk"],
        "6mo": ["1d", "1wk", "1mo"],
        "1y": ["1d", "1wk", "1mo"],
        "ytd": ["1d", "1wk", "1mo"],
        "max": ["1d", "1wk", "1mo"]
    }
    options = interval_map.get(period, ["1d"])
    if period == "1d":
        default_index = options.index("30m") if "30m" in options else 0
    else:
        default_index = options.index("1d") if "1d" in options else 0
    return options, default_index

def init_state():
    """Initialize session state with defaults if not already set."""
    if "active_tickers" not in st.session_state:
        tickers = DEFAULT_PORTFOLIO["Ticker"].tolist()
        quantities = dict(zip(
            DEFAULT_PORTFOLIO["Ticker"],
            DEFAULT_PORTFOLIO["Quantity"].astype(int)
        ))
        st.session_state.active_tickers = tickers
        st.session_state.active_quantities = quantities
        st.session_state.active_period = "1mo"
        st.session_state.active_interval = "1d"
        st.session_state.data = ensure_prices(tickers, "1mo", "1d")

def update_state(portfolio_df, period, interval):
    """Update session state when user changes sidebar inputs."""
    tickers = portfolio_df["Ticker"].dropna().astype(str).str.strip().tolist()
    quantities = dict(zip(
        tickers,
        pd.Series(portfolio_df["Quantity"]).fillna(0).astype(int)
    ))
    st.session_state.active_tickers = tickers
    st.session_state.active_quantities = quantities
    st.session_state.active_period = period
    st.session_state.active_interval = interval
    st.session_state.data = ensure_prices(tickers, period, interval)
