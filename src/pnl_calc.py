# src/pnl_calc.py
import pandas as pd

def calculate_pnl(price_data: dict[str, pd.DataFrame], quantities: dict[str, float]) -> pd.DataFrame:
    """
    Compute PnL for each ticker given price history and quantities.
    price_data: dict mapping ticker -> DataFrame with 'Close' column
    quantities: dict mapping ticker -> quantity held
    Returns a DataFrame with PnL and percentage change for each ticker.
    
    """
    results = []
    for ticker, df in price_data.items():
        if df is None or df.empty:
            continue
        try:
            start = df["Close"].iloc[0]
            end = df["Close"].iloc[-1]
            qty = quantities.get(ticker, 0)
            pnl = (end - start) * qty
            pct = ((end - start) / start) * 100 if start else 0.0
            results.append({
                "Ticker": ticker,
                "Quantity": qty,
                "Start Price": start,
                "End Price": end,
                "PnL ($)": pnl,
                "Change (%)": pct,
                "Position Value ($)": end * qty
            })
        except Exception as e:
            print(f"Error calculating PnL for {ticker}: {e}")
    return pd.DataFrame(results)
