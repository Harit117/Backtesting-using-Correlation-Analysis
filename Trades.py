import pandas as pd
from datetime import datetime, timedelta
import os
import backtrader as bt

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

contrarian_signals = {}

for symbol in tickers:
    file = f'{symbol}_10yr.csv'
    if not os.path.exists(file):
        continue

    df = pd.read_csv(file, skiprows=3, names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Date'] >= start_date]
    df = df[['Date', 'Close']].set_index('Date')
    price_series = df['Close']
    returns = price_series.pct_change().dropna()

    rolling_corr = spy_returns.rolling(30).corr(returns)
    full_corr = spy_returns.corr(returns)
    signal_series = pd.Series(0, index=rolling_corr.index)

    for i in range(30, len(rolling_corr)):
        date = rolling_corr.index[i]
        curr_corr = rolling_corr.iloc[i]
        spy_trend = spy_returns.iloc[i - 30:i].mean()
        if full_corr > 0.7 and curr_corr < 0.3 and spy_trend > 0:
            signal_series.iloc[i] = 1

    df_out = pd.DataFrame({
        'Date': signal_series.index,
        'Open': price_series.loc[signal_series.index],
        'High': price_series.loc[signal_series.index],
        'Low': price_series.loc[signal_series.index],
        'Close': price_series.loc[signal_series.index],
        'Volume': 0,
        'signal': signal_series
    }).dropna()
    df_out.set_index('Date', inplace=True)
    contrarian_signals[symbol] = df_out

class SignalFeed(bt.feeds.PandasData):
    lines = ('signal',)
    params = (('signal', -1),)

class CorrelationStrategy(bt.Strategy):
    def __init__(self):
        self.signal = self.datas[0].signal
        self.win_count = 0
        self.loss_count = 0

    def notify_trade(self, trade):
        if trade.isclosed:
            if trade.pnl > 0:
                self.win_count += 1
            elif trade.pnl < 0:
                self.loss_count += 1

    def next(self):
        if not self.position and self.signal[0] == 1:
            size = int(self.broker.get_cash() / self.data.close[0])
            self.buy(size=size)
        elif self.position and self.signal[0] != 1:
            self.close()

performance = {}

for ticker, df in contrarian_signals.items():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(CorrelationStrategy)
    datafeed = SignalFeed(dataname=df)
    cerebro.adddata(datafeed)
    cerebro.broker.setcash(1000)
    results = cerebro.run()
    strategy = results[0]
    cerebro.plot()

    duration = (df.index[-1] - df.index[0]).days / 365
    start_val = 1000
    end_val = cerebro.broker.getvalue()
    ann_return = ((end_val / start_val) ** (1 / duration) - 1) * 100
    performance[ticker] = ann_return

    trades = strategy.win_count + strategy.loss_count
    win_ratio = (strategy.win_count / trades) * 100 if trades else 0
    print(f"\n{ticker}: Trades = {trades}, Wins = {strategy.win_count}, Losses = {strategy.loss_count}, Win Ratio = {win_ratio:.2f}%, Annual Return = {ann_return:.2f}%")
import matplotlib.pyplot as plt

avg_return = sum(performance.values()) / len(performance)

plt.figure(figsize=(10, 6))
bars = plt.bar(performance.keys(), performance.values(), color='skyblue', edgecolor='black')
plt.axhline(avg_return, color='red', linestyle='--', label=f'Average: {avg_return:.2f}%')
plt.ylabel('Annualized Return (%)')
plt.xlabel('Ticker')
plt.title('📊 Annualized Return by Ticker (Contrarian Strategy)')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{height:.2f}%', ha='center')

plt.legend()
plt.tight_layout()
plt.show()
