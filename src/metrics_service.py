# src/metrics_service.py
"""
Metrics Service
================
This module provides functions to compute various financial metrics for a portfolio based on its profit and loss (PnL) data.
"""
import pandas as pd
from src.metrics import (calculate_var, calculate_cvar, sharpe_ratio, sortino_ratio, calmar_ratio, max_drawdown, correlation_matrix)

def compute_portfolio_metrics(pnl_df: pd.DataFrame) -> dict:
    if pnl_df is None or pnl_df.empty:
        return {}

    # Get the total portfolio market value for each time step.
    portfolio_value_series = pnl_df.groupby("Time")["Position Value ($)"].sum()

    # 2. Calculate Portfolio Returns (required for all ratios and VaR/CVaR)
    # Returns are the percentage change of the *total portfolio value*.
    returns = portfolio_value_series.pct_change().dropna()

    # 3. Prepare Price Data for Correlation Matrix
    price_wide = pnl_df.pivot(index="Time", columns="Ticker", values="Price")

    return {
        "VaR (95%)": calculate_var(returns),
        "CVaR (95%)": calculate_cvar(returns),
        "Sharpe": sharpe_ratio(returns),
        "Sortino": sortino_ratio(returns),
        "Calmar": calmar_ratio(returns),
        "Max Drawdown": max_drawdown(portfolio_value_series), # Max Drawdown often takes the value series itself
        "Correlation Matrix": correlation_matrix(price_wide)
    }