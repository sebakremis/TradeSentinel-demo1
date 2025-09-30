# src/metrics_service.py
"""
Metrics Service
================
This module provides functions to compute various financial metrics for a portfolio based on its profit and loss (PnL) data.
"""
import pandas as pd
from metrics import (
    calculate_var, calculate_cvar, sharpe_ratio,
    sortino_ratio, calmar_ratio, max_drawdown,
    correlation_matrix, win_loss_stats
)

def compute_portfolio_metrics(pnl_df: pd.DataFrame) -> dict:
    """Compute all portfolio metrics and return as a dict."""
    if pnl_df is None or pnl_df.empty:
        return {}

    # 1. Calculate Portfolio PnL Returns (requires PnL and Time columns)
    returns = pnl_df.groupby("Time")["PnL"].sum().pct_change().dropna()
    
    # 2. Prepare Price Data for Correlation Matrix (requires Time, Ticker, Price columns)
    # This pivoting is necessary because correlation_matrix expects a wide-format price DataFrame.
    price_wide = pnl_df.pivot(index="Time", columns="Ticker", values="Price")

    return {
        "VaR (95%)": calculate_var(returns),
        "CVaR (95%)": calculate_cvar(returns),
        "Sharpe": sharpe_ratio(returns),
        "Sortino": sortino_ratio(returns),
        "Calmar": calmar_ratio(returns),
        "Max Drawdown": max_drawdown(returns),
        # Pass the correctly formatted wide price data for correlation
        "Correlation Matrix": correlation_matrix(price_wide)
       }