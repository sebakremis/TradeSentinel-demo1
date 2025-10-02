# TradeSentinel-demo1 — First Demo

### 📌 Overview

TradeSentinel is a Python-powered dashboard for real-time portfolio monitoring, providing insights into PnL, exposure, and risk metrics.

This repo is the first demo for the TradeSentinel project. Demo is **stable** and has been validated through extensive testing:
- Core metrics implemented in `metrics.py` were successfully tested in `test_metrics.py` and `test_metrics_edge_cases.py`.  
- Historical data retrieved via **Yahoo Finance (yfinance)** was manually validated to ensure accuracy and consistency with market data.  

Ongoing and planned improvements include:
- Adding dedicated tests for the **Correlation Matrix** functionality.  
- Refactoring `dashboard.py` to improve **modularity** and maintainability.  

> Note: A new demo for TradeSentinel has been developed in a private repository. This version builds on the original portfolio simulation dashboard and now includes individual ticker analysis, enabling users to construct and evaluate an Equally Weighted Portfolio.

👉 [Launch the new demo here](https://tradesentinel.streamlit.app)

In this new demo, the study interval is fixed to daily prices, as this timeframe is the most suitable for the type of analysis performed in the project. Users can now focus on selecting the appropriate lookback period for their study, with the added flexibility of defining a custom lookback window by choosing specific start and end dates from a calendar.

## 🚀 Features
- **Live market data:** Fetches prices from APIs (Yahoo Finance).

- **PnL tracking:** Calculates mark-to-market PnL by instrument, sector, or portfolio.
   * Note: For historical data, `TradeSentinel` uses adjusted close prices (via auto_adjust=True) to account for dividends and splits. This ensures that PnL calculations reflect total return and avoids artificial price drops on dividend dates.    
- **Risk metrics:** Computes Value-at-Risk (VaR), exposure by asset class, and limit breaches.
- **Interactive dashboard:** Built with Streamlit for intuitive visualization.

## 🛠 Tech stack
- **Python:** `pandas`, `numpy`, `altair`, `streamlit`, `plotly`
- **Data APIs:** `Yahoo Finance`
- **Deployment:** `Streamlit Community Cloud`

## 📂 Project structure
- **data/** — Sample datasets  
- **src/** — Core Python scripts  
  - **ensure_data.py** — Market data ingestion  
  - **dashboard.py** — App UI and visualization  
  - *(other supporting modules)*  
- **tests/** — Unit tests  
- **requirements.txt** — Python dependencies  
- **README.md** — Project documentation  
- **LICENSE** — License file  


## 📈 Example use case
- **Intraday PnL tracking**: Monitor live portfolio PnL and key metrics during market hours to quickly spot drawdowns or performance spikes.
- **Comprehensive portfolio analysis**: View and explore portfolio metrics and visualizations over a selected time horizon. Analyze historical performance, sector allocation, and asset distribution trends to support medium‑ and long‑term investment decisions.
- **On-demand CSV snapshots**: Export the current portfolio metrics view to CSV for quick sharing, further analysis, or archiving as a daily snapshot.
- **Foundation for scalable financial platforms**: Use `TradeSentinel`’s modular architecture as the starting point for building more complex solutions — for example, integrating with broker APIs for live order execution, adding multi‑asset risk engines, or connecting to internal data warehouses for firm‑wide exposure reporting. Its clean separation between data ingestion, analytics, and visualization makes it easy to extend into a full‑scale portfolio management or risk monitoring system.

---

## 🚀 Launch the first demo

### Live demo
<a href="https://tradesentinel-first-demo.streamlit.app/" target="_blank">🌐 Click here to launch TradeSentinel first demo on Streamlit Community Cloud</a>  
_No installation required — runs directly in your browser._  
*(Tip: On GitHub, links always open in the same tab. Right‑click and choose “Open link in new tab” if you prefer.)*


### Alternatively, clone the repo and run `dashboard.py` locally:
```bash
# Clone the repository
git clone https://github.com/sebakremis/TradeSentinel.git
cd TradeSentinel/src

# Install dependencies
pip install -r ../requirements.txt

# Run the dashboard
streamlit run dashboard.py
```
* **To exit a dashboard.py local session**: close the Dashboard tab & press `Ctrl + C` in your terminal.
## 📜 License  
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details. 

---
**Author:** Sebastian Kremis 
**Contact:** skremis@ucm.es

