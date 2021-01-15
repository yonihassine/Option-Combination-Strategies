import yfinance as yf
from forex_python.converter import CurrencyRates
import pandas as pd

df_tickers = dict(pd.read_excel("tickers.xlsx", sep=",",  sheet_name=None))


class finance_api:
    def __init__(self, portfolio_currency):
        self.portfolio_currency = portfolio_currency
        self.c_rates = CurrencyRates()
        self.tickers = df_tickers
        self.col_dict = {'Contract': 'contractSymbol',
                         'Last Trade Date': 'lastTradeDate',
                         'Strike': 'strike',
                         'Last Price': 'lastPrice',
                         'Implied Volatility': 'impliedVolatility',
                         'inTheMoney': 'inTheMoney',
                         'Contract Size': 'contractSize',
                         'Currency': 'currency'}

        self.col_dict_bis = {'contractSymbol': 'Contract',
                             'lastTradeDate': 'Last Trade Date',
                             'strike': 'Strike',
                             'lastPrice': 'Last Price',
                             'impliedVolatility': 'Implied Volatility',
                             'inTheMoney': 'inTheMoney',
                             'contractSize': 'Contract Size',
                             'currency': 'Currency'}

        self.col_names = list(self.col_dict.keys())

        self.options_data = dict()

    def show_exchanges(self):
        return list(self.tickers.keys())

    def show_tickers(self, exchange):
        temp = self.tickers[exchange]
        return {temp.loc[i, "Name"]: temp.loc[i, "Symbol"] for i in temp.index}

    def get_div_yield(self, ticker):
        try:
            out = yf.Ticker(ticker).info['dividendYield']
        except Exception:
            print("No dividend yield for this stock")
            return -1
        return out

    def get_price(self, ticker, convert_currency=True):
        stock_info = yf.Ticker(ticker).info
        curr = stock_info['currency']
        bid = stock_info['bid']
        ask = stock_info['ask']
        price = (bid + ask)/2
        if bid == 0 or ask == 0:
            price = stock_info['previousClose']
        if self.portfolio_currency != curr and convert_currency:
            return self.c_rates.convert(curr, self.portfolio_currency, price)
        else:
            return price

    def get_maturities(self, ticker):
        try:
            sol = list(yf.Ticker(ticker).options)
        except Exception:
            print("No option data available on yahoo for this ticker")
            return -1
        return sol

    def possible_values(self, ticker, attribute):
        if self.options_data == dict():
            print("No option data loaded")
            return -1
        else:
            return sorted(list(set(self.options_data[ticker]
                                   [attribute].values)))

    def get_options_data(self, ticker, option_type, maturity):
        if maturity not in self.get_maturities(ticker):
            print("Maturity not in maturities list")
            return -1
        try:
            asset = yf.Ticker(ticker)
        except Exception as e:
            print("Wrong ticker name")
            return e.__class__

        if option_type == "Call":
            res = asset.option_chain(maturity).calls.sort_values(
                'lastTradeDate', ascending=False)
        elif option_type == "Put":
            res = asset.option_chain(maturity).puts.sort_values(
                'lastTradeDate', ascending=False)
        else:
            print("Wrong option type name, \
                  you can type either \'Call\' or \'Put'")
            return -1
        res = res[list(self.col_dict_bis.keys())]
        res.columns = list(map(
            lambda x: self.col_dict_bis[x], list(res.columns)))
        self.options_data[ticker] = res

    def filter_options(self, ticker, attribute, value):
        if value not in self.possible_values(ticker, attribute):
            print('{} is not a possible {} value'.format(value, attribute))
            return -1
        self.options_data[ticker] = self.options_data[ticker]
        [self.options_data[ticker][attribute] == value]


first_api = finance_api('EUR')

# print(first_api.get_price('AAPL'))
