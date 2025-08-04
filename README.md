Rolling Correlation Analysis & Backtrader Strategy for S&P 500

This repository explores a contrarian quant strategy built on 10 years of SPY and top S&P 500 stock data. We start by cleaning and structuring the raw CSVs, then calculate rolling correlations between SPY and individual stocks using a dynamic time window. These correlations are visualized year-wise in 10×10 heatmaps, revealing changing relationships across market cycles.

Signals are derived from low-correlation behavior — stocks less tethered to SPY are selected for LONG positions, challenging conventional trends. Each stock is backtested using the Backtrader framework, with results compiled into a comparative bar chart showcasing annualized returns across tickers.

The repo includes modular Python scripts, strategy logic breakdowns, and insightful visualizations to help researchers and traders replicate or build on this approach. Ideal for those experimenting with correlation-based signals, backtesting workflows, or just curious about alternative portfolio dynamics.
