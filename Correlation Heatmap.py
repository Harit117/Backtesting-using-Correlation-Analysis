import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

tickers = ['AAPL', 'AMZN', 'AVGO', 'BRK-B', 'GOOG', 'LLY', 'META', 'MSFT', 'NVDA', 'TSLA']
start_date = datetime.now() - timedelta(days=365 * 10)
end_date = datetime.now()

spy_file = 'SPY_10yr.csv'
price_data = {}

spy_df = pd.read_csv(spy_file, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
spy_df['Date'] = pd.to_datetime(spy_df['Date'])
spy_df = spy_df[spy_df['Date'] >= start_date]
spy_df = spy_df[['Date', 'Close']].set_index('Date')
spy_returns = spy_df['Close'].pct_change().dropna()

for symbol in tickers:
    file = f'{symbol}_10yr.csv'
    if not os.path.exists(file):
        continue
    df = pd.read_csv(file, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Date'] >= start_date]
    df = df[['Date', 'Close']].set_index('Date')
    price_data[symbol] = df['Close']

correlation_scores = pd.DataFrame(index=tickers, columns=[str(y) for y in range(start_date.year, end_date.year + 1)])

for year in correlation_scores.columns:
    yr = int(year)
    spy_yearly = spy_returns[spy_returns.index.year == yr]
    for symbol in tickers:
        stock_series = price_data[symbol].pct_change().dropna()
        stock_yearly = stock_series[stock_series.index.year == yr]
        aligned = pd.concat([spy_yearly, stock_yearly], axis=1).dropna()
        if aligned.shape[0] > 50:
            corr = aligned.corr().iloc[0,1]
            correlation_scores.loc[symbol, year] = corr
        else:
            correlation_scores.loc[symbol, year] = None

correlation_scores = correlation_scores.astype(float)

plt.figure(figsize=(12, 6))
sns.heatmap(correlation_scores, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('📈 SPY vs Stock Correlation (Yearly Averages)')
plt.xlabel('Year')
plt.ylabel('Ticker')
plt.tight_layout()
plt.show()
