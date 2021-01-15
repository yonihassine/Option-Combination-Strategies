import numpy as np
from scipy.stats import norm
from api_connect import finance_api
import pandas as pd
import yfinance as yf
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.plotting import figure


class Option:
    def __init__(self, S_0, K, T, sigma, r, q,
                 option_type="Call",
                 maturity_date=None):
        # inputs
        self.S_0 = S_0
        self.K = K
        self.T = T / 365
        self.sigma = sigma
        self.r = r
        self.q = q
        self.option_type = option_type
        self.maturity_date = maturity_date
        self.BSprice = None
        self.MCprice = None

        # Greeks
        T = T / 365
        d_1 = (((np.log(S_0/K) + (r + 0.5 * sigma**2) * T))
               / (sigma * np.sqrt(T)))
        d_2 = d_1 - sigma * np.sqrt(T)

        if self.option_type == "Call":
            self.BSprice = S_0 * norm.cdf(d_1)\
                - K * np.exp(-r * T) * norm.cdf(d_2)
            self.Delta = norm.cdf(d_1)
            self.Theta = (-((S_0 * sigma * norm.pdf(d_1)) / (2 * np.sqrt(T)))
                          - r * K * np.exp(-r * T) * norm.cdf(d_2))/365
        elif self.option_type == "Put":
            self.BSprice = -S_0 * norm.cdf(-d_1)\
                + K * np.exp(-r * T) * norm.cdf(-d_2)
            self.Delta = -norm.cdf(-d_1)
            self.Theta = (-((S_0 * sigma * norm.pdf(d_1)) / (2 * np.sqrt(T)))
                          + r * K * np.exp(-r * T) * norm.cdf(-d_2))/365
        self.Gamma = (1 / (S_0 * sigma * np.sqrt(T))) * norm.pdf(d_1)
        self.Vega = S_0 * np.sqrt(T) * norm.pdf(d_1) * 0.01

    def __str__(self):
        info = 'Type:          ' + self.option_type + \
            '\nInitial price: ' + str(self.S_0) +\
            '\nStrike price:  ' + str(self.K) +\
            '\nMaturity:           ' + str(self.T) +\
            '\nImplied Volatility: ' + "{0:.0%}".format(self.sigma) +\
            '\nRisk free rate: ' + "{0:.0%}".format(self.r)
        return info


class Strategy:
    def __init__(self, ticker="AAPL", currency="EUR", stocks=0):
        self.options_list = {}
        self.stocks = stocks
        self.ticker = ticker
        self.source_currency = yf.Ticker(self.ticker).info['currency']
        self.currency = currency
        self.api = finance_api(currency)
        self.S_0 = self.api.get_price(ticker, False)
        self.S_0_converted = self.api.get_price(ticker)
        self.q = self.api.get_div_yield(ticker)
        if self.q is None:
            self.q = 0
        self.r = 0

        self.df_pnl = pd.SparseDataFrame
        self.df_greeks = pd.SparseDataFrame

        self.cds_options = ColumnDataSource()
        self.cds_pnl = ColumnDataSource()
        self.cds_greeks = ColumnDataSource()

        self.columns_options = [TableColumn(field="Amount", title="Amount"),
                                TableColumn(field="Option type",
                                            title='Option type'),
                                TableColumn(field="Maturity date",
                                            title="Maturity"),
                                TableColumn(field="Maturity",
                                            title="Days to maturity"),
                                TableColumn(field="Strike",
                                            title="Strike"),
                                TableColumn(field="Implied volatility",
                                            title="Implied volatility (in %)"),
                                TableColumn(field="Value", title="Value")]
        self.columns_pnl = []
        self.columns_greeks = []

        self.options_table = DataTable(columns=self.columns_options,
                                       source=self.cds_options)
        self.pnl_table = DataTable(columns=self.columns_pnl,
                                   source=self.cds_pnl)
        self.greeks_table = DataTable(columns=self.columns_greeks,
                                      source=self.cds_greeks)

        self.pnl_fig = figure()
        self.greeks_fig = figure()

    def add_option(self, K, T, sigma, option_type, amount, maturity_date=None):
        opt_label = "{} , strike {}, {} days".format(option_type, K, T)
        if opt_label in self.options_list:
            if self.options_list[opt_label][0] + amount == 0:
                del self.options_list[opt_label]
            else:
                self.options_list[opt_label][0] += amount
        else:
            self.options_list[opt_label] = [amount, Option(self.S_0, K, T,
                                                           sigma, self.r,
                                                           self.q, option_type,
                                                           maturity_date)]

    def set_stock_quantity(self, n_stocks):
        self.stocks = n_stocks

    def refresh(self):
        self.S_0 = self.api.get_price(self.ticker, False)
        for opt_label in self.options_list:
            self.options_list[opt_label][1].S_0 = self.S_0
            self.options_list[opt_label][1].r = self.r
            self.options_list[opt_label][1].q = self.q
        self.get_df_options()

    def reset(self, ticker):
        print(ticker, "here")
        self.options_list = {}
        self.ticker = ticker
        self.source_currency = yf.Ticker(self.ticker).info['currency']
        self.S_0 = self.api.get_price(ticker, False)
        self.S_0_converted = self.api.get_price(ticker)
        self.q = self.api.get_div_yield(ticker)
        if self.q is None:
            self.q = 0
        self.cds_options.data = {col.field: [] for col in self.columns_options}
        print(ticker, "success")

    def Delta(self, S_0=0, shift_time=0, shift_vol=0):
        if S_0 == 0 and shift_time == 0 and shift_vol == 0:
            out = sum([self.options_list[o][1].Delta * self.options_list[o][0]
                       for o in self.options_list]) + self.stocks
        else:
            if S_0 == 0:
                S_0 = self.S_0
            out = self.stocks +\
                sum([Option(S_0, self.options_list[o][1].K,
                            (365 * self.options_list[o][1].T) - shift_time,
                            self.options_list[o][1].sigma + shift_vol,
                            self.r, self.q,
                            self.options_list[o][1].option_type).Delta
                     * self.options_list[o][0] for o in self.options_list])
        return out

    def Gamma(self, S_0=0, shift_time=0, shift_vol=0):
        if S_0 == 0 and shift_time == 0 and shift_vol == 0:
            out = sum([self.options_list[o][1].Gamma
                       * self.options_list[o][0]
                       for o in self.options_list])
        else:
            if S_0 == 0:
                S_0 = self.S_0
            out = sum([Option(S_0, self.options_list[o][1].K,
                              (365 * self.options_list[o][1].T) - shift_time,
                              self.options_list[o][1].sigma + shift_vol,
                              self.r, self.q,
                              self.options_list[o][1].option_type).Gamma
                       * self.options_list[o][0] for o in self.options_list])
        return out

    def Vega(self, S_0=0, shift_time=0, shift_vol=0):
        if S_0 == 0 and shift_time == 0 and shift_vol == 0:
            out = sum([self.options_list[o][1].Vega * self.options_list[o][0]
                       for o in self.options_list])
        else:
            if S_0 == 0:
                S_0 = self.S_0
            out = sum([Option(S_0, self.options_list[o][1].K,
                              (365 * self.options_list[o][1].T) - shift_time,
                              self.options_list[o][1].sigma + shift_vol,
                              self.r, self.q,
                              self.options_list[o][1].option_type).Vega
                       * self.options_list[o][0] for o in self.options_list])
        return out

    def Theta(self, S_0=0, shift_time=0, shift_vol=0):
        if S_0 == 0 and shift_time == 0 and shift_vol == 0:
            out = sum([self.options_list[o][1].Theta * self.options_list[o][0]
                      for o in self.options_list])
        else:
            if S_0 == 0:
                S_0 = self.S_0
            out = sum([Option(S_0, self.options_list[o][1].K,
                              (365*self.options_list[o][1].T) - shift_time,
                              self.options_list[o][1].sigma + shift_vol,
                              self.r, self.q,
                              self.options_list[o][1].option_type).Theta
                       * self.options_list[o][0] for o in self.options_list])
        return out

    def price(self, S_0=0, shift_time=0, shift_vol=0, convert_currency=False):
        if S_0 == 0 and shift_time == 0 and shift_vol == 0:
            out = self.S_0 * self.stocks\
                + sum([self.options_list[o][1].BSprice
                       * self.options_list[o][0]
                       for o in self.options_list])
        else:
            if S_0 == 0:
                S_0 = self.S_0
            out = S_0 * self.stocks\
                + sum([Option(S_0, self.options_list[o][1].K,
                              (365 * self.options_list[o][1].T) - shift_time,
                              self.options_list[o][1].sigma + shift_vol,
                              self.options_list[o][1].r,
                              self.options_list[o][1].q,
                              self.options_list[o][1].option_type).BSprice
                       * self.options_list[o][0] for o in self.options_list])
        if convert_currency:
            out = self.api.c_rates.convert(self.source_currency, self.currency,
                                           out)
        return out

    # print data frames
    def get_df_options(self):
        self.cds_options.data = {col.field: [] for col in self.columns_options}
        for opt_label in self.options_list:
            o = self.options_list[opt_label]
            self.cds_options.stream({"Amount": [o[0]],
                                     "Option type": [o[1].option_type],
                                     "Maturity date": [o[1].maturity_date],
                                     "Maturity": [o[1].T * 365],
                                     "Strike": [o[1].K],
                                     "Implied volatility": [o[1].sigma * 100],
                                     "Value": [o[1].BSprice * o[0]]})
        self.options_table.source, self.options_table.columns =\
            self.cds_options, self.columns_options

    def get_df_pnl(self, step, shift_time, shift_vol, nb_display=40):
        df_pnl = pd.DataFrame()
        list_i = pd.Series([i for i in range(nb_display + 1)])
        df_pnl['Forward'] = self.S_0 * (1 + step * (list_i - 20))
        df_pnl['Instantaneous P&L'] =\
            df_pnl['Forward'].apply(lambda u: self.price(u)) - self.price()
        df_pnl['P&L in {} days with {:.2f}% vol move'.format(shift_time,
                                                             shift_vol * 100)]\
            = df_pnl['Forward'].apply(lambda u: self.price(u, shift_time,
                                                           shift_vol))\
            - self.price()
        df_pnl.dropna(axis=0, how='any', inplace=True)
        self.df_pnl = df_pnl
        self.cds_pnl.data = {"Forward": df_pnl.iloc[:, 0],
                             "Instantaneous": df_pnl.iloc[:, 1],
                             "Future": df_pnl.iloc[:, 2]}
        self.columns_pnl =\
            [TableColumn(field="Forward", title="Forward"),
             TableColumn(field="Instantaneous", title='Instantaneous P&L'),
             TableColumn(field="Future",
                         title='P&L in {} days with {:.2f}% vol move'.format(
                             shift_time, shift_vol * 100))]
        self.pnl_table.source, self.pnl_table.columns =\
            self.cds_pnl, self.columns_pnl

    def get_df_greeks(self, greek, step, shift_time, shift_vol, nb_display=40):
        dict_fonc = {"Delta": self.Delta, "Gamma": self.Gamma,
                     "Vega": self.Vega, "Theta": self.Theta}
        df_greeks = pd.DataFrame()
        list_i = pd.Series([i for i in range(nb_display + 1)])
        df_greeks['Forward'] = self.S_0 * (1 + step * (list_i - 20))
        df_greeks['Instantaneous ' + greek] =\
            df_greeks['Forward'].apply(lambda u: dict_fonc[greek](u))
        df_greeks[greek + ' in {} days with {:.2f}% vol move'.format(
            shift_time, shift_vol * 100)] =\
            df_greeks['Forward'].apply(lambda u: dict_fonc[greek](u,
                                                                  shift_time,
                                                                  shift_vol))
        df_greeks.dropna(axis=0, how='any', inplace=True)
        self.df_greeks = df_greeks
        self.cds_greeks.data = {"Forward": df_greeks.iloc[:, 0],
                                "Instantaneous": df_greeks.iloc[:, 1],
                                "Future": df_greeks.iloc[:, 2]}
        self.columns_greeks =\
            [TableColumn(field="Forward", title="Forward"),
             TableColumn(field="Instantaneous",
                         title='Instantaneous ' + greek),
             TableColumn(field="Future",
                         title=greek +
                         ' in {} days with {:.2f}% vol move'.format(
                             shift_time, shift_vol * 100))]
        self.greeks_table.source, self.greeks_table.columns =\
            self.cds_greeks, self.columns_greeks

    def create_figures(self, greek):
        self.pnl_fig = figure(plot_width=600,
                              plot_height=400,
                              x_axis_label='Stock Price',
                              y_axis_label='P&L Value',
                              title="P&L",
                              sizing_mode="scale_both",
                              background_fill_color="white",
                              border_fill_color="white")
        self.pnl_fig.line("Forward", "Instantaneous", source=self.cds_pnl,
                          line_color='dodgerblue',
                          legend_label="Instantaneous Value")
        # self.columns_pnl[1].title)
        self.pnl_fig.line("Forward", "Future", source=self.cds_pnl,
                          line_color='red', line_dash='dashed',
                          legend_label="Projected Value")
        # self.columns_pnl[-1].title)

        self.greeks_fig = figure(plot_width=600,
                                 plot_height=400,
                                 x_axis_label='Stock Price',
                                 y_axis_label='Value',
                                 title=greek,
                                 sizing_mode="scale_both",
                                 background_fill_color="white",
                                 border_fill_color="white")
        self.greeks_fig.line("Forward", "Instantaneous",
                             source=self.cds_greeks, line_color='dodgerblue',
                             legend_label="Instantaneous Value")
        # self.columns_greeks[1].title)
        self.greeks_fig.line("Forward", "Future",
                             source=self.cds_greeks, line_color='red',
                             line_dash='dashed',
                             legend_label="Projected Value")
        # self.columns_greeks[-1].title)

    def get_df_pnl_greeks(self, greek, step, shift_time,
                          shift_vol, nb_display=40):
        self.get_df_pnl(step, shift_time, shift_vol, nb_display)
        self.get_df_greeks(greek, step, shift_time, shift_vol, nb_display)
