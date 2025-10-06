# TradeSentinel-demo1

### 📌 Overview

TradeSentinel is an **extensible Python framework** for portfolio research, designed for quantitative analysts and Python developers working on investment management and risk analysis applications.

This repository demonstrates a modular architecture that separates data ingestion, metric computation, and visualization—making it straightforward to extend for custom research workflows, backtesting strategies, or integration with proprietary data sources.

**Development Status:**
- Core analytics modules (`metrics.py`) are tested and validated via `test_metrics.py` and `test_metrics_edge_cases.py`
- Market data pipeline uses Yahoo Finance (`yfinance`) with adjusted close prices to ensure accurate total-return calculations
- Actively maintained with focus on code quality, modularity, and extensibility

**Roadmap:**
- Expand test coverage for correlation matrix functionality
- Refactor `dashboard.py` for improved separation of concerns
- Add support for custom data connectors and alternative risk models

> **Note:** A second demo (TradeSentinel-demo2) extends this framework with individual security analysis and equally-weighted portfolio construction capabilities. Access it at [https://tradesentinel.streamlit.app](https://tradesentinel.streamlit.app)

---

## 🔬 Research-Focused Features

### Investment Management
- **Portfolio Construction**: Modular framework for implementing and comparing portfolio strategies
- **Performance Attribution**: Track PnL by instrument, sector, and asset class with full dividend/split adjustment
- **Historical Analysis**: Configurable lookback periods for analyzing return distributions and drawdown patterns
- **Data Export**: Export metrics to CSV for further analysis in Jupyter, R, or other research environments

### Risk Analysis
- **Value-at-Risk (VaR)**: Parametric and historical VaR implementations with configurable confidence levels
- **Exposure Monitoring**: Real-time tracking of positions by asset class, sector, and risk factor
- **Correlation Analysis**: Compute rolling correlation matrices for multi-asset portfolios
- **Limit Breach Detection**: Customizable risk limit framework for position sizing and concentration constraints

### Extensibility for Developers
- **Clean Module Separation**: Data layer, analytics layer, and presentation layer are independently testable
- **API-First Design**: Core functions accept DataFrames, making integration with pandas-based workflows seamless
- **Pluggable Data Sources**: Replace Yahoo Finance with your own market data provider, database, or data warehouse
- **Test-Driven**: Comprehensive unit tests demonstrate how to validate custom metric implementations

---

## 🛠 Technology Stack

**Core Libraries:**
- `pandas` & `numpy` — Data manipulation and numerical computing
- `yfinance` — Market data retrieval (easily replaceable)
- `pytest` — Unit testing framework

**Visualization & UI:**
- `streamlit` — Interactive web interface for research exploration
- `plotly` & `altair` — Publication-quality charts and visualizations

**Deployment:**
- Streamlit Community Cloud for demo hosting
- Docker-ready for deployment in research environments

---

## 📂 Repository Structure

```
TradeSentinel-demo1/
├── data/              # Sample datasets for testing
├── src/
│   ├── metrics.py     # Core analytics: PnL, VaR, exposure calculations
│   ├── ensure_data.py # Market data ingestion abstraction layer
│   ├── dashboard.py   # Streamlit UI (reference implementation)
│   └── ...            # Additional modules
├── tests/
│   ├── test_metrics.py
│   └── test_metrics_edge_cases.py
├── requirements.txt
├── pytest.ini
└── README.md
```

**Key Modules for Developers:**
- **`metrics.py`**: Start here to understand the core analytics. Functions are pure and accept DataFrames as inputs.
- **`ensure_data.py`**: Data ingestion layer. Replace this to connect to your own data sources.
- **`dashboard.py`**: Reference UI implementation. Fork this to build custom research interfaces.

---

## 🧪 Research Use Cases

### Quantitative Strategy Development
- Prototype multi-asset portfolio strategies with real market data
- Compute risk-adjusted performance metrics (Sharpe, Sortino, max drawdown)
- Export time-series results for statistical analysis or machine learning pipelines

### Risk Model Validation
- Compare parametric vs. historical VaR across different market regimes
- Analyze tail risk and stress-test portfolios under custom scenarios
- Validate exposure calculations against risk management systems

### Academic Research & Teaching
- Demonstrate portfolio theory concepts with live data
- Provide students with a tested codebase for empirical finance projects
- Extend with factor models, optimization algorithms, or custom risk metrics

### Production System Prototyping
- Use as a reference architecture for building institutional portfolio systems
- Integrate with broker APIs, execution management systems, or data warehouses
- Scale analytics modules to handle larger universes and higher-frequency data

---

## 🚀 Quick Start

### Option 1: Live Demo (No Installation)

👉 [**Launch TradeSentinel-demo1**](https://tradesentinel-demo1.streamlit.app/)

Explore the framework's capabilities directly in your browser.

### Option 2: Local Development Setup

```bash
# Clone the repository
git clone https://github.com/sebakremis/TradeSentinel-demo1.git
cd TradeSentinel-demo1

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
pytest

# Launch the dashboard
cd src
streamlit run dashboard.py
```

### Option 3: Use Core Modules in Your Own Project

```python
import pandas as pd
from src.metrics import calculate_pnl, compute_var, analyze_exposure

# Your own data source
prices = pd.DataFrame(...)  # Load from database, CSV, API, etc.
positions = pd.DataFrame(...)

# Use TradeSentinel's tested analytics
pnl = calculate_pnl(prices, positions)
var_95 = compute_var(returns, confidence=0.95)
exposure_summary = analyze_exposure(positions, prices)
```

---

## 🔧 Extending TradeSentinel

### Add a Custom Data Source

1. Implement a new function in `ensure_data.py` following the existing interface
2. Return a pandas DataFrame with columns: `['date', 'ticker', 'price']`
3. Update `dashboard.py` to call your custom data function

### Implement a Custom Risk Metric

1. Add your function to `metrics.py` (accept DataFrame inputs, return DataFrame or scalar)
2. Write unit tests in `tests/test_metrics.py`
3. Integrate visualization in `dashboard.py` or use the metric in your own notebooks

### Deploy in Your Environment

- **Docker**: Add a `Dockerfile` with your Python environment and data connections
- **Jupyter Integration**: Import modules directly into notebooks for interactive research
- **Scheduled Jobs**: Use `ensure_data.py` and `metrics.py` in cron jobs or Airflow DAGs

---

## 📊 Data Considerations

**Adjusted Close Prices:**  
TradeSentinel uses `yfinance` with `auto_adjust=True` to retrieve adjusted close prices. This accounts for corporate actions (dividends, splits) and ensures PnL calculations reflect **total return**. For production systems, validate against your official data vendor.

**Custom Data Sources:**  
The framework is designed to be data-agnostic. Replace the Yahoo Finance connector with:
- Bloomberg API, Refinitiv, or FactSet feeds
- Internal databases (PostgreSQL, TimescaleDB, InfluxDB)
- Cloud data warehouses (Snowflake, BigQuery, Redshift)
- Alternative data providers (Quandl, Alpha Vantage, IEX Cloud)

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test module
pytest tests/test_metrics.py -v
```

**Testing Philosophy:**  
Core analytics modules are isolated from data sources and UI, making them straightforward to unit test. See `tests/test_metrics.py` for examples of how to test financial calculations with synthetic data.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Feel free to fork, modify, and use in academic or commercial projects. Contributions via pull requests are welcome.

---

## 👤 Author & Contact

**Sebastian Kremis**  
📧 [skremis@ucm.es](mailto:skremis@ucm.es)

For questions about extending TradeSentinel for research applications, feel free to open an issue or reach out directly.


