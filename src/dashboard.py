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
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import datetime

# --- DUMMY FUNCTION REPLACEMENTS FOR COLAB/JUPYTER COMPATIBILITY ---
def ensure_prices(tickers, period, interval):
    """Generates dummy data for the tickers."""
    data = {}
    end_date = pd.Timestamp.now().normalize()
    
    if interval.endswith('m') or period == '1d':
        date_range = pd.date_range(end=end_date, periods=30, freq='15min')
    elif period in ['1mo', '3mo']:
        date_range = pd.date_range(end=end_date, periods=30, freq='D')
    else:
        date_range = pd.date_range(end=end_date, periods=100, freq='D')

    for ticker in tickers:
        np.random.seed(hash(ticker) % 1000)
        base_price = np.random.uniform(50, 200)
        returns = np.random.normal(0, 0.01, size=len(date_range)).cumsum()
        prices = base_price * np.exp(returns)
        
        sector = np.random.choice(["Tech", "Finance", "Energy", "Healthcare"])
        
        df = pd.DataFrame({
            "Close": prices,
            "Sector": sector,
        }, index=date_range)
        
        data[ticker] = df
    return data

# Placeholder metrics functions
def calculate_var(returns, level): return 0.02 
def calculate_cvar(returns, level): return 0.03
def sharpe_ratio(returns): return 1.5
def sortino_ratio(returns): return 2.0
def calmar_ratio(returns): return 0.8
def max_drawdown(cum_returns): return 0.15
def correlation_matrix(price_wide): return price_wide.corr().fillna(0)
def win_loss_stats(pnl): return 0

# --- END OF DUMMY FUNCTIONS ---

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

# --- Static hint ---
st.sidebar.markdown(
    "💡 If you need **intraday** price data, choose an interval shorter than 1 day."
)

# --- Use stored parameters for display (Direct Access) ---
tickers = st.session_state.active_tickers
quantities = st.session_state.active_quantities
period = st.session_state.active_period
interval = st.session_state.active_interval

# --- Title ---
st.title("📈 TradeSentinel: Portfolio Monitor (demo)")

# --- Data Check ---
if not st.session_state.data:
    st.info("Portfolio data is loading or empty. Please check your ticker list.")
    st.stop()


# --- PnL Calculation (per ticker snapshot) ---
pnl_data = []
for ticker, df in st.session_state.data.items():
    if df is not None and not df.empty:
        try:
            start = df["Close"].iloc[0]
            end = df["Close"].iloc[-1]

            qty = quantities.get(ticker, 0)
            weighted_pnl = (end - start) * qty
            position_value = end * qty
            pct = ((end - start) / start) * 100 if start != 0 else 0.0

            pnl_data.append({
                "Ticker": ticker,
                "Quantity": qty,
                "Start Price": start,
                "End Price": end,
                "PnL ($)": weighted_pnl,
                "Change (%)": pct,
                "Position Value ($)": position_value
            })
        except Exception as e:
            st.warning(f"{ticker}: Error calculating PnL - {e}")

# --- Display Per-Ticker Table ---
if pnl_data:
    df_pnl = pd.DataFrame(pnl_data)

    st.subheader("📋 Per-Ticker PnL")

    # Display with conditional coloring + formatted floats
    st.dataframe(
        df_pnl.style
        .map(
            lambda v: "color: green" if isinstance(v, (int, float)) and v > 0
            else ("color: red" if isinstance(v, (int, float)) and v < 0 else ""),
            subset=["PnL ($)", "Change (%)"]
        )
        .format({
            "Quantity": "{:,.0f}",
            "Start Price": "{:,.2f}",
            "End Price": "{:,.2f}",
            "PnL ($)": "{:,.2f}",
            "Change (%)": "{:,.2f}",
            "Position Value ($)": "{:,.2f}"
        }),
        # Use the new 'width="stretch"' syntax for this native Streamlit component
        width="stretch" 
    )


    # --- Portfolio Summary + Pie Chart ---
    total_pnl = df_pnl["PnL ($)"].sum()
    total_value = df_pnl["Position Value ($)"].sum()
    total_pct = (total_pnl / total_value) * 100 if total_value else 0.0

    st.subheader("📊 Portfolio Summary")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.metric("Total PnL ($)", f"${total_pnl:,.2f}")
        st.metric("Total Position Value ($)", f"${total_value:,.2f}")
        st.metric("Total Change (%)", f"{total_pct:.2f}%")

    with col2:
        pie_df = df_pnl[["Ticker", "Position Value ($)"]].copy()
        total_value_pie = pie_df["Position Value ($)"].sum()

        if not pie_df.empty and total_value_pie > 0:
            pie_df["Percentage"] = (pie_df["Position Value ($)"] / total_value_pie) * 100

            fig = px.pie(
                pie_df,
                names="Ticker",
                values="Position Value ($)",
                title="Portfolio Allocation by Ticker",
                hole=0.3
            )

            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(showlegend=False, title_x=0.3)
            # FIX: Revert to use_container_width=True to avoid the keyword argument deprecation warning
            st.plotly_chart(fig, use_container_width=True) 
        else:
            st.info("No data available for allocation pie chart.")

    # --- Portfolio PnL Over Time ---
    st.subheader("📉 Portfolio PnL Over Time")
    pnl_time_data = []
    for ticker, df in st.session_state.data.items():
        if df is not None and not df.empty:
            try:
                tmp = df.copy()
                qty = quantities.get(ticker, 0)
                tmp["Quantity"] = qty
                tmp["Price"] = tmp["Close"]
                tmp["Position Value ($)"] = tmp["Price"] * tmp["Quantity"]
                tmp["PnL"] = (tmp["Price"] - tmp["Price"].iloc[0]) * tmp["Quantity"]
                tmp["Ticker"] = ticker
                tmp["Time"] = tmp.index
                pnl_time_data.append(
                    tmp[["Time", "Ticker", "Quantity", "Price", "Position Value ($)", "PnL"]]
                )
            except Exception as e:
                st.warning(f"{ticker}: Error building time series - {e}")

    if pnl_time_data:
        combined_df = pd.concat(pnl_time_data, ignore_index=True)
        chart = (
            alt.Chart(combined_df)
            .mark_line()
            .encode(
                x=alt.X("Time:T", title="Time"),
                y=alt.Y("PnL:Q", title="PnL ($)"),
                color=alt.Color("Ticker:N", title="Ticker"),
            )
            # FIX: Use Altair's 'container' to expand the chart (not 'stretch')
            .properties(width='container', height=400)
        )
        # FIX: Revert to use_container_width=True to avoid the keyword argument deprecation warning
        st.altair_chart(chart, use_container_width=True) 

        # --- Portfolio Allocation by Sector ---
        st.subheader("📊 Portfolio Allocation by Sector")
        latest_data = []
        for ticker, df in st.session_state.data.items():
            if df is not None and not df.empty:
                latest_close = df["Close"].iloc[-1]
                qty = quantities.get(ticker, 0)
                sector = df["Sector"].iloc[0] if "Sector" in df.columns and not df["Sector"].empty else "Unknown"
                position_value = latest_close * qty
                latest_data.append({
                    "Ticker": ticker,
                    "Sector": sector,
                    "PositionValue": position_value
                })

        if latest_data:
            sector_df = pd.DataFrame(latest_data)

            sector_alloc = (
                sector_df.groupby("Sector")
                .agg({
                    "PositionValue": "sum",
                    "Ticker": lambda s: ", ".join(sorted(set(s)))
                })
                .reset_index()
            )

            total_val = sector_alloc["PositionValue"].sum()
            sector_alloc["Percentage"] = (sector_alloc["PositionValue"] / total_val) * 100

            fig_sector = go.Figure(
                data=[
                    go.Pie(
                        labels=sector_alloc["Sector"],
                        values=sector_alloc["PositionValue"],
                        hole=0.3,
                        textinfo="percent+label",
                        textposition="inside",
                        hoverinfo="skip"
                    )
                ]
            )

            fig_sector.update_layout(
                title="Portfolio Allocation by Sector",
                showlegend=False,
                title_x=0.3,
                margin=dict(l=10, r=10, t=60, b=10)
            )

            # FIX: Revert to use_container_width=True
            st.plotly_chart(fig_sector, use_container_width=True)

            # Use the new width='stretch' for st.dataframe (native component)
            st.dataframe(
                sector_alloc[["Sector", "Ticker"]],
                width="stretch",
                hide_index=True
            )

        else:
            st.info("No data available for sector allocation chart.")

        # --- Advanced Metrics Section ---
        st.subheader("📊 Advanced Metrics")

        portfolio_values = combined_df.groupby("Time")["Position Value ($)"].sum()
        portfolio_returns = portfolio_values.pct_change().dropna()
        cum_returns = (1 + portfolio_returns).cumprod().fillna(1)

        var_95 = calculate_var(portfolio_returns, 0.95)
        cvar_95 = calculate_cvar(portfolio_returns, 0.95)
        sharpe = sharpe_ratio(portfolio_returns)
        sortino = sortino_ratio(portfolio_returns)
        calmar = calmar_ratio(portfolio_returns)
        mdd = max_drawdown(cum_returns)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("VaR (95%)", f"{var_95:.2%}")
            st.metric("CVaR (95%)", f"{cvar_95:.2%}")
        with col2:
            st.metric("Sharpe Ratio", f"{sharpe:.2f}")
            st.metric("Sortino Ratio", f"{sortino:.2f}")
        with col3:
            st.metric("Calmar Ratio", f"{calmar:.2f}")
            st.metric("Max Drawdown", f"{mdd:.2%}")

        # --- Asset Correlation Matrix ---
        st.subheader("📈 Asset Correlation Matrix")

        price_wide = combined_df.pivot(index="Time", columns="Ticker", values="Price")
        corr_df = correlation_matrix(price_wide).round(6)

        # Use the new width='stretch' for st.dataframe (native component)
        st.dataframe(
            corr_df.style.background_gradient(cmap="coolwarm", vmin=-1, vmax=1),
            width="stretch"
        )

        # --- Editable Table: Interactive PnL Table with CSV Export ---
        st.subheader("🔍 Explore & Export PnL Data")

        tickers_selected = st.multiselect(
            "Select Ticker(s)",
            options=sorted(combined_df["Ticker"].unique().tolist()),
            default=sorted(combined_df["Ticker"].unique().tolist()),
            key="export_ticker_select"
        )

        date_min = combined_df["Time"].min().date()
        date_max = combined_df["Time"].max().date()

        date_range = st.date_input(
            "Select Date Range",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max,
            key="export_date_range"
        )
        
        # Ensure date_range is a tuple of two dates
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date = date_range[0]
            end_date = date_range[1]
        else:
            start_date = date_min
            end_date = date_max

        filtered_df = combined_df[
            combined_df["Ticker"].isin(tickers_selected)
            & (combined_df["Time"].dt.date >= start_date)
            & (combined_df["Time"].dt.date <= end_date)
        ].copy()

        if not filtered_df.empty:
            total_pnl_filtered = filtered_df["PnL"].sum()
            avg_pnl_filtered = filtered_df["PnL"].mean()
            total_value_filtered = filtered_df["Position Value ($)"].sum()
            avg_price_filtered = filtered_df["Price"].mean()


            df_display = filtered_df.sort_values("Time", ascending=False).copy()

            df_display["Date"] = df_display["Time"].dt.strftime("%Y-%m-%d")
            df_display["Time"] = df_display["Time"].dt.strftime("%H:%M:%S")

            cols = ["Date", "Time"] + [c for c in df_display.columns if c not in ["Date", "Time"]]
            df_display = df_display[cols].reset_index(drop=True)

            for col in ["Price", "Position Value ($)", "PnL"]:
                if col in df_display.columns:
                    df_display[col] = df_display[col].astype(float).round(2)

            # Use the new width='stretch' for st.dataframe (native component)
            st.dataframe(
                df_display.style.format({
                    "Quantity": "{:,.0f}",
                    "Price": "{:,.2f}",
                    "PnL": "{:,.2f}",
                    "Position Value ($)": "{:,.2f}"
                }),
                width="stretch",
                hide_index=True
            )

            filename = f"pnl_data_{'_'.join(tickers_selected)}_{start_date}_{end_date}.csv"
            csv_data = df_display.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="💾 Download filtered data as CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
            )
        else:
            st.info("No valid data to display. Try refreshing or adjusting filters.")


# Credits
st.markdown("---")
st.markdown(
    "🔗 [View Source Code on GitHub](https://github.com/sebakremis/TradeSentinel)",
    unsafe_allow_html=True
)
st.caption("Built using Streamlit and Python.")