#Matt Macarty Mean Reversion

#Importing Packages
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
plt.close('all')
from matplotlib import rcParams
rcParams['figure.figsize'] = 8,6
import seaborn as sb
sb.set()

#Collecting Data
spy = yf.download("SPY", start="2020-01-01", end="2025-06-30")
spy.columns = spy.columns.droplevel(1)
spy.head()

#Creating pandas Data Frame with Close Price
spyc = spy['Close']
spyc_df = pd.DataFrame(spyc)
spyc_df.columns = ['Close']

#Setting rolling window 
ma = 63 #Length of 1 month trading cycle

#Calculating log-returns
spyc_df['Returns'] = np.log(spyc_df['Close']).diff()

#Calculating moving average
spyc_df['Moving Average'] = spyc_df['Close'].rolling(ma).mean()

#Calculating Close Price to Moving Average ratio
spyc_df['Ratio'] = spyc_df['Close']/spyc_df['Moving Average']
spyc_df['Ratio'].describe()

#Investigating Percentiles
percentiles = [5,10,50,90,95]
breaks = np.percentile(spyc_df['Ratio'].dropna(),percentiles)
print(breaks)


#Defining Long and Short Positions
short = breaks[-1]
long = breaks[0]
spyc_df['Position'] = np.where(spyc_df.Ratio > short, -1, np.nan)
spyc_df['Position'] = np.where(spyc_df.Ratio < long, 1, spyc_df['Position'])
#spyc_df['Position'] = spyc_df['Position'].ffill()


#Calculating Strategy Returns
spyc_df['Strategy Returns'] = spyc_df['Returns'] * spyc_df['Position'].shift()

#Plotting Buy/Hold vs Strategy Returns
plt.figure(figsize=(10,5))
plt.plot(np.exp(spyc_df['Returns'].dropna().cumsum()), label='Buy/Hold Returns')
plt.plot(np.exp(spyc_df['Strategy Returns'].dropna().cumsum()), label='Strategy Returns')
plt.legend()

#Calulating Cumulative Returns
cumulative_returns = np.exp(spyc_df['Returns'].dropna().cumsum())
cumulative_strategy_returns = np.exp(spyc_df['Strategy Returns'].dropna().cumsum())

print("Cumulative Buy/Hold Returns:", cumulative_returns.iloc[-1])
print("Cumulative Strategy Returns:", cumulative_strategy_returns.iloc[-1])

