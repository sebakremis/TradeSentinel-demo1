# src/ui_sections.py    
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from metrics_service import compute_portfolio_metrics

def render_pnl_table(pnl_df: pd.DataFrame):
    """Render the Per-Ticker PnL table without numeric index,
    sorted by descending PnL ($)."""

    st.subheader("📋 Per-Ticker PnL")

    if pnl_df.empty:
        st.info("No PnL data available.")
        return

    # Sort by PnL descending
    df_sorted = pnl_df.sort_values(by="PnL ($)", ascending=False).reset_index(drop=True)

    # Apply styling: green for positive, red for negative
    styled_df = (
        df_sorted.style
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
            "Position Value ($)": "{:,.2f}",
        })
    )

    # Render without index
    st.dataframe(styled_df, width="stretch", hide_index=True)


def render_portfolio_summary(df_pnl: pd.DataFrame):
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
            # Use use_container_width=True to avoid the keyword argument deprecation warning
            st.plotly_chart(fig, use_container_width=True) 
        else:
            st.info("No data available for allocation pie chart.")



def render_block(price_data: dict, quantities: dict) -> None:
    """
    Render portfolio PnL over time chart.

    Parameters
    ----------
    price_data : dict
        Mapping of ticker -> DataFrame with 'Close' column (and DateTimeIndex).
    quantities : dict
        Mapping of ticker -> quantity held.
    """
    st.subheader("📉 Portfolio PnL Over Time")
    pnl_time_data = []

    for ticker, df in price_data.items():
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
                    tmp[["Time", "Ticker", "Quantity", "Price",
                         "Position Value ($)", "PnL"]]
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
            .properties(width="container", height=400)
        )
        st.altair_chart(chart, use_container_width=True)
        render_portfolio_allocation(price_data, quantities)

        # Rendering others:
        metrics = compute_portfolio_metrics(combined_df)
        render_advanced_metrics(combined_df, metrics)
        render_editable_table(combined_df)

def render_portfolio_allocation(price_data: dict[str, pd.DataFrame],
                                quantities: dict[str, int]) -> None:
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

            # Use use_container_width=True
            st.plotly_chart(fig_sector, use_container_width=True)

            # Use the new width='stretch' for st.dataframe (native component)
            st.dataframe(
                sector_alloc[["Sector", "Ticker"]],
                width="stretch",
                hide_index=True
            )

        else:
            st.info("No data available for sector allocation chart.")

def render_advanced_metrics(combined_df: pd.DataFrame, metrics: dict) -> None:
    st.subheader("📊 Advanced Metrics")
    portfolio_values = combined_df.groupby("Time")["Position Value ($)"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("VaR (95%)", f"{metrics['VaR (95%)']:.2%}")
        st.metric("CVaR (95%)", f"{metrics['CVaR (95%)']:.2%}")
    with col2:
        st.metric("Sharpe Ratio", f"{metrics['Sharpe']:.2f}")
        st.metric("Sortino Ratio", f"{metrics['Sortino']:.2f}")
    with col3:
        st.metric("Calmar Ratio", f"{metrics['Calmar']:.2f}")
        st.metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")

    # --- Asset Correlation Matrix ---
    st.subheader("📈 Asset Correlation Matrix")

    price_wide = combined_df.pivot(index="Time", columns="Ticker", values="Price")
    corr_df = metrics.get("Correlation Matrix")
    if corr_df is None:
        corr_df = price_wide.corr().round(6)  # fallback if not precomputed

    st.dataframe(
        corr_df.style.background_gradient(cmap="coolwarm", vmin=-1, vmax=1),
        width="stretch"
    )

def render_editable_table(combined_df: pd.DataFrame) -> None:
    """
    Editable Table: Interactive PnL Table with CSV Export ---
    """
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