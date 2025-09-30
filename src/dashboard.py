# src/dashboard.py
"""

dashboard.py

============



Streamlit dashboard for monitoring intraday and historical Profit & Loss (PnL), portfolio risk metrics, and asset/sector allocations for multiple tickers.



Features

--------

- **Sidebar controls:**

- Editable table (`st.data_editor`) for entering tickers and quantities (dynamic rows, instant updates).

- Select historical data period and price interval with context-aware interval options.

- Refresh data on demand with basic validation and helpful messages.



- **Data fetching & caching:**

- Retrieves market price data for the selected tickers using `ensure_prices` from `ensure_data.py`.

- Caches data and user selections in `st.session_state` to avoid redundant fetches (`active_tickers`, `active_quantities`, `active_period`, `active_interval`, `data`).



- **PnL & position metrics:**

- Computes per ticker PnL in absolute ($) and percentage terms from first to last bar in the selected period/interval.

- Calculates position values based on latest prices and quantities.

- Adds Quantity, Price, and Position Value ($) columns to all outputs.

- Handles missing or invalid data gracefully.



- **Portfolio summary & allocation:**

- Displays total PnL, total position value, and total % change.

- Portfolio Allocation pie chart by ticker (Plotly), with labels inside slices and hidden legend.

- Portfolio Allocation by sector (Plotly) plus a simplified sector-to-tickers table.



- **Visualization:**

- Styled per-ticker PnL DataFrame with green/red highlighting for gains/losses.

- Portfolio PnL Over Time line chart by ticker (Altair).

- Pie charts with percentage labels inside slices and centered titles.



- **Advanced risk & performance metrics:**

- VaR (95%), CVaR (95%), Sharpe, Sortino, Calmar ratios, and Max Drawdown computed from portfolio returns.

- Asset Correlation Matrix table with gradient styling.

- Win/Loss stats derived from PnL time series.



- **Interactive PnL table with CSV export:**

- Filter by ticker(s) and date range.

- Shows filtered summary metrics (total/average PnL, position value in M$, average price).

- Download filtered data as CSV (includes Quantity, Price, Position Value ($), and PnL) with a dynamic filename.



Usage

-----

Run the dashboard with Streamlit:

streamlit run src/dashboard.py



Dependencies

------------

- streamlit

- pandas

- altair

- plotly

- ensure_data.ensure_prices

- metrics (calculate_var, calculate_cvar, sharpe_ratio, sortino_ratio, calmar_ratio, max_drawdown, correlation_matrix, win_loss_stats)



Notes

-----

Ensure that `ensure_data.py` is available and properly configured to fetch market data before running this dashboard.

"""

import streamlit as st
import pandas as pd


from ui_sections import render_pnl_table, render_portfolio_summary, render_block
from pnl_calc import calculate_pnl
from ensure_data import ensure_prices



# --- Sidebar controls ---
st.sidebar.title("Set portfolio to analyze:")

# Default portfolio data
default_data = pd.DataFrame({
    "Ticker": ["NVDA", "MSFT", "GOOGL"],
    "Quantity": [100, 30, 70]
})

# Initialization Block
if "active_tickers" not in st.session_state:
    default_tickers = default_data["Ticker"].tolist()
    default_quantities = dict(zip(default_data["Ticker"], default_data["Quantity"].astype(int)))
    
    st.session_state.active_tickers = default_tickers
    st.session_state.active_quantities = default_quantities
    st.session_state.active_period = "1mo"
    st.session_state.active_interval = "1d"
    st.session_state.data = ensure_prices(default_tickers, "1mo", "1d")

# Editable table for tickers and quantities
portfolio_df = st.sidebar.data_editor(
    default_data,
    num_rows="dynamic",
    width="stretch"
)

# --- Period & Interval selection with dynamic filtering ---
period_input = st.sidebar.selectbox(
    "Period",
    ["1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd", "max"],
    index=2, 
    key="period_select"
)

# Allowed intervals mapping
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

interval_options = interval_map[period_input]

default_interval_index = (
    interval_options.index("30m") if period_input == "1d"
    else interval_options.index("1d")
)

interval_input = st.sidebar.selectbox(
    "Interval",
    interval_options,
    index=default_interval_index,
    key="interval_select"
)

# --- Update button (not refresh) ---
if st.sidebar.button("Update Portfolio"):
    tickers_input = portfolio_df["Ticker"].dropna().astype(str).str.strip().tolist()
    quantities_input = portfolio_df["Quantity"]

    st.session_state.active_tickers = tickers_input
    st.session_state.active_quantities = dict(
        zip(tickers_input, pd.Series(quantities_input).fillna(0).astype(int))
    )
    st.session_state.active_period = period_input
    st.session_state.active_interval = interval_input

    with st.spinner("Fetching market data..."):
        st.session_state.data = ensure_prices(
            st.session_state.active_tickers,
            period=st.session_state.active_period,
            interval=st.session_state.active_interval,
        )



# --- Use stored parameters for display (Direct Access) ---
tickers = st.session_state.active_tickers
quantities = st.session_state.active_quantities
period = st.session_state.active_period
interval = st.session_state.active_interval
data = st.session_state.data

# --- Title ---
st.title("📈 TradeSentinel: Portfolio Monitor (demo)")

# --- Data Check ---
if not st.session_state.data:
    st.info("Portfolio data is loading or empty. Please check your ticker list.")
    st.stop()


# --- PnL Calculation (per ticker snapshot) ---
pnl_data = calculate_pnl(data, quantities)

# --- Display  ---
if pnl_data is not None and not pnl_data.empty:
    # --- Per-Ticker PnL Table ---
    df_pnl = pd.DataFrame(pnl_data)
    render_pnl_table(df_pnl)

    # --- Portfolio Summary + Pie Chart ---
    render_portfolio_summary(df_pnl)
  
    # --- Render Block: Chart - Allocation by Sector - Advanced Metrics - Editable Table ---
    render_block(data, quantities)

        


# Credits
st.markdown("---")
st.markdown(
    "🔗 [View Source Code on GitHub](https://github.com/sebakremis/TradeSentinel)",
    unsafe_allow_html=True
)
st.caption("Built using Streamlit and Python.")