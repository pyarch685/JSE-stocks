# Calculates the Relative Strength Index of shares on JSE as at 2-1-2024.

# Import necessary modules for company share analysis.
import sys
import time
import pprint
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# This code switches off error messages.
pd.options.mode.chained_assignment = None

# Create lists & dictionaries to store jse Top 40 share names and jse share ticker symbols.
jse_symbols = []
jse_names = []
jse_Top40_dict = {}

# Create lists to store date stamps of buy signals.
matrixsignals = []

# Create list to store profits.
matrixprofits = []

# Create list to store date stamps of buy signals.
buy_signals = []

# Create list to store date stamps of profit signals.
profit_signals = []

# Create list to store date stamps of buying dates.
Buying_dates = []

# Create list to store date stamps of selling dates.
Selling_dates = []

# Create list to store profits.
rawprofit = []

# Create list to store company information.
company_info = []


# Prompt user for the name of the company to analyse.
def main():
    global asset, df
    jse_Top40_dict()
    pprint.pprint(jse_Top40_dict)
    time.sleep(1)
    
    while True:
        try:
            asset = input("Enter JSE company name to analyse share price: ").upper()
            if asset in jse_Top40_dict.keys():
                df = calculation(jse_Top40_dict[asset])
                break
        except ValueError:
                print(f"{asset} No price data found, symbol may be delisted.")
                break
        else:
            print(f"{asset} not found, try again!")
    jse_Top40_info(asset)
    pprint.pprint(df)
    pprint.pprint(income_stmt)
    pprint.pprint(balance_stmt)
    pprint.pprint(cashflow_stmt)
    pprint.pprint(actions_stmt)
    plot_asset()


def jse_Top40_dict():
    global jse_symbols, jse_names, jse_Top40_dict
    with open("jse_list.txt", "r") as f:
        jse_top40 = [_ for _ in f.readlines()]
        for i in jse_top40:
            symbol, name = i.split(",")
            jse_symbols.append(symbol)
            jse_names.append(name)
            jse_names = [i.replace("\n", "") for i in jse_names]
        jse_symbols = [i + ".JO" for i in jse_symbols]
        jse_Top40_dict = {key: value for key, value in zip(jse_names, jse_symbols)}
        return jse_Top40_dict


def calculation(asset):
    global df, adj_close_price, adj_close_MA200
    df = yf.download(asset, start="2015-01-01")
    df["MA200"] = df["Adj Close"].rolling(window=200).mean()
    df["price change"] = df["Adj Close"].pct_change()
    df["Upmove"] = df["price change"].apply(lambda x: x if x > 0 else 0)
    df["Downmove"] = df["price change"].apply(lambda x: abs(x) if x < 0 else 0)
    df["avg Up"] = df["Upmove"].ewm(span=19).mean()
    df["avg Down"] = df["Downmove"].ewm(span=19).mean()
    df = df.dropna()
    df["RS"] = df["avg Up"] / df["avg Down"]
    df["RSI"] = df["RS"].apply(lambda x: 100 - (100 / (x + 1)))
    df.loc[(df["Adj Close"] > df["MA200"]) & (df["RSI"] < 30), "Buy"] = "Yes"
    df.loc[(df["Adj Close"] < df["MA200"]) | (df["RSI"] > 30), "Buy"] = "No"

    # Create dataset arrays from the dataframe
    # adj_close_price = df.loc[df["Adj Close"]]
    # adj_close_MA200 = df.loc[df["MA200"]]
    return df


def jse_Top40_info(asset):
    global income_stmt, balance_stmt, cashflow_stmt, actions_stmt

    income_stmt = yf.Ticker(f"{jse_Top40_dict[asset]}").income_stmt
    balance_stmt = yf.Ticker(f"{jse_Top40_dict[asset]}").balance_sheet
    cashflow_stmt = yf.Ticker(f"{jse_Top40_dict[asset]}").cashflow
    actions_stmt = yf.Ticker(f"{jse_Top40_dict[asset]}").actions

    return income_stmt, balance_stmt, cashflow_stmt, actions_stmt


# def getSignals(df):
#     for i in range(len(df) - 12):
#         if "Yes" in df["Buy"].iloc[i]:
#             for j in range(1, 11):
#                 if df["RSI"].iloc[i + j] > 40:
#                     Buying_dates.append(df.iloc[i + 1].name)
#                     Selling_dates.append(df.iloc[i + j + 1].name)
#                     break
#                 elif j == 10:
#                     Buying_dates.append(df.iloc[i + 1].name)
#                     Selling_dates.append(df.iloc[i + j + 1].name)
#     return Buying_dates, Selling_dates


def plot_asset():
    plt.figure(figsize=(12, 5))
    # plt.scatter(df.loc[buy].index, df.loc[buy]["Adj Close"], marker="^", c="g")
    plt.plot(df["Adj Close"], 'r-', alpha=0.7)
    plt.plot(df["MA200"], 'g-', alpha=0.7)
    # plt.hist(rawprofit, bins=100)
    plt.show()
    sys.exit()


# def matrix_signals():
#     for i in matrixsignals:
#         for e in i:
#             if e.year == 2021:
#                 return e


# def raw_profit():
#     for i in matrixprofits:
#         for e in i:
#             return rawprofit.append(e)

#     wins = [i for i in rawprofit if i > 0]
#     success_rate = round(len(wins) / len(rawprofit) * 100, 2)
#     print(f"The success rate of this strategy is: {success_rate}\%.")


# def jse_Top40():
#     try:
#         for i in jse_Top40_dict.values():
#             print(i)
#             test = calculation(i)
#             buy, sell = getSignals(test)
#             Profits = (
#                 test.loc[sell].Open.values - test.loc[buy].Open.values
#             ) / test.loc[buy].Open.values
#             matrixsignals.append(buy)
#             matrixprofits.append(Profits)
#     except ValueError:
#         print("Data not available.")


# def test_jseTop40():
#     test = calculation(jse_Top40_dict[asset])
#     buy, sell = getSignals(test)
#     Profits = (test.loc[sell].Open.values - test.loc[buy].Open.values) / test.loc[
#         buy
#     ].Open.values
#     buy_signals.append(buy)
#     profit_signals.append(Profits)


if __name__ == "__main__":
    main()
