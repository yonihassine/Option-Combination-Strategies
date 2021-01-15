from bokeh.plotting import curdoc
from bokeh.models.widgets import Button, Slider, Select, Spinner, Div
from bokeh.layouts import column, row
from OptionClass import Strategy
from datetime import datetime

# variables for stock
exchange = "NYSE"
ticker = "AAPL"
stock_name = "Apple Inc."

my_Strategy = Strategy()

today = datetime.today()

# variables for df
step = 0.005
shift_time = 0
shift_vol = 0
greek = "Delta"

# variables to add option
option_type = "Call"
T = None
K = None
option_qty = 10
sigma = 0.15


# ##############################choose ticker widgets########################
menu_exchanges = {ex: ex for ex in my_Strategy.api.show_exchanges()}
select_exchange = Select(title="Exchange", options=list(menu_exchanges.keys()),
                         value=exchange)

menu_tickers = my_Strategy.api.show_tickers(exchange)
select_stock = Select(title="Stock", options=list(menu_tickers.keys()),
                      value=stock_name)

slider_rate = Slider(start=-5, end=10, value=0, step=0.1, title="Risk free\
                     rate (in %)")


# ##############################add option widgets#######################
menu_maturities = {mat: mat for mat in my_Strategy.api.get_maturities(ticker)}
maturity = list(menu_maturities.keys())[0]
select_maturity = Select(title="Maturity", options=list(
    menu_maturities.keys()), value=maturity)

opt_type = {"Call": "Call", "Put": "Put"}
select_type = Select(title="Option type", options=list(opt_type.keys()),
                     value=option_type)

my_Strategy.api.get_options_data(ticker, option_type, maturity)
menu_strikes = {str(k): k for k in my_Strategy.api.possible_values(ticker,
                                                                   "Strike")}
K = list(menu_strikes.keys())[0]
select_strike = Select(title="Strike", options=list(menu_strikes.keys()),
                       value=K)

spinner_qty = Spinner(value=0, step=1, title="Number of options to add \
                      (or remove)")

button_add = Button(label='Add options (or remove)', button_type="success")

spinner_qty_stocks = Spinner(value=0, step=1, title="Number of stocks")

# ##############################display widgets###############################
menu_greeks = {"Delta": "Delta", "Gamma": "Gamma", "Vega": "Vega",
               "Theta": "Theta"}
select_greek = Select(title="Greek", options=list(menu_greeks.keys()),
                      value=greek)

min_T = 1/365
slider_time = Slider(start=0, end=int(min_T * 365), value=0, step=1,
                     title="Shift Time (in days)")

min_sigma = 0
slider_vol = Slider(start=-min_sigma * 100, end=30, value=0, step=0.1,
                    title="Shift Volatility (in %)")

slider_step = Slider(start=0, end=5, value=0.5, step=0.1, title="Window size")

# update function


def update():
    global ticker, exchange, menu_tickers
    global info, greek, shift_time, shift_vol, step
    global menu_maturities, menu_strikes, K, maturity

    refresh_flag = False

    if menu_tickers[select_stock.value] != ticker:
        stock_name = select_stock.value
        ticker = menu_tickers[stock_name]
        my_Strategy.reset(ticker)
        info.text = "The current value of <b>"
        + stock_name
        + "</b> is <b>{:.2f}</b>, the dividend yield\
            is <b>{:.2f}</b>%.".format(my_Strategy.S_0, my_Strategy.q * 100)
        if my_Strategy.api.get_maturities(ticker) == -1:
            data.text = "/!\\ <b>There is no available options data for this\
                stock on yahoo</b> /!\\ "
            data.style = {'color': 'red'}

            menu_maturities = {"": ""}
            maturity = ""

            menu_strikes = {"": ""}
            K = ""
        else:
            data.text = "There is available options data for <b>{}</b> on\
                yahoo".format(stock_name)
            data.style = {'color': 'green'}

            menu_maturities = {mat: mat for mat in my_Strategy.api.
                               get_maturities(ticker)}
            maturity = list(menu_maturities.keys())[0]

            my_Strategy.api.get_options_data(ticker, option_type, maturity)
            menu_strikes = {str(k): k for k in my_Strategy.
                            api.possible_values(ticker, "Strike")}
            K = list(menu_strikes.keys())[0]

        select_maturity.options = list(menu_maturities.keys())
        select_maturity.value = maturity

        select_strike.options = list(menu_strikes.keys())
        select_strike.value = K

    if select_exchange.value != exchange:
        exchange = select_exchange.value
        menu_tickers = my_Strategy.api.show_tickers(exchange)
        select_stock.options = list(menu_tickers.keys())
        select_stock.value = list(menu_tickers.keys())[0]

    greek = select_greek.value
    shift_time = slider_time.value
    shift_vol = slider_vol.value / 100
    step = slider_step.value / 100

    my_Strategy.set_stock_quantity(spinner_qty_stocks.value)

    if my_Strategy.r != slider_rate.value:
        my_Strategy.r = slider_rate.value/100
        refresh_flag = True

    if refresh_flag:
        my_Strategy.refresh()

    my_Strategy.get_df_pnl_greeks(greek, step, shift_time, shift_vol)
    # change graphs
    my_Strategy.greeks_fig.title.text = greek


def change_qty_option():
    global K, maturity, T, sigma, option_type, option_qty, min_T
    global min_sigma, slider_vol, slider_time

    my_Strategy.r = slider_rate.value/100
    option_type = select_type.value
    maturity = select_maturity.value
    T = (datetime.strptime(maturity, "%Y-%m-%d") - today).days
    K = float(select_strike.value)
    option_qty = spinner_qty.value
    sigma = my_Strategy.api.options_data[ticker].loc[
        my_Strategy.api.options_data[ticker]
        ["Strike"] == K, "Implied Volatility"].iloc[0]
    my_Strategy.add_option(K, T, sigma, option_type, option_qty, maturity)
    my_Strategy.refresh()

    if my_Strategy.options_list != {}:
        min_T = min(my_Strategy.options_list[o][1].T
                    for o in my_Strategy.options_list)
        min_sigma = min(my_Strategy.options_list[o][1].sigma
                        for o in my_Strategy.options_list)
    else:
        min_T = 1
        min_sigma = 0

    slider_time.end = min_T * 365
    slider_vol.start = -min_sigma * 100

    update()


def update_select_K():
    global maturity, option_type, menu_strikes
    option_type = select_type.value
    maturity = select_maturity.value
    if maturity != "":
        my_Strategy.api.get_options_data(ticker, option_type, maturity)
        menu_strikes = {str(k): k for k in
                        my_Strategy.api.possible_values(ticker, "Strike")}
    else:
        menu_strikes = {"": ""}
    select_strike.options = list(menu_strikes.keys())
    select_strike.value = list(menu_strikes.keys())[0]


controls = [select_exchange, select_stock, slider_rate, select_greek,
            slider_vol, slider_time, slider_step, spinner_qty_stocks]
controls_opt = [select_maturity, select_type]

for control in controls:
    control.on_change('value', lambda attr, old, new: update())

for control in controls_opt:
    control.on_change('value', lambda attr, old, new: update_select_K())

button_add.on_click(change_qty_option)

info = Div(text="The current value of <b>{}</b> is <b>{:.2f}</b>,\
           the dividend yield is <b>{:.2f}</b>%".format(stock_name,
           my_Strategy.S_0, my_Strategy.q * 100))
data = Div(text="There is available options data for <b>{}</b> on yahoo"
           .format(stock_name), style={'color': 'green'})
your_pf = Div(text="<b>These are the options in your portfolio</b>",
              align="center")
welcome = Div(text=" Welcome to this option strategy builder \
              software.<br><br>"
              " Here, you can build any option strategy you want using\
                  real options <b>directly available on the market</b>.<br>"
              " The data is retrieved using yahoo finance api \
                    so don't expect it to be always accurate.<br>"
                   " Also, it takes time to change your underlying stock\
                    or the exchange you are in, so just be patient =)<br>"
              " Once you selected your strategy, you can analyze \
                your P&L and greeks exposures on the graphs or\
                    in the tables.<br><br>"
              " " + "&nbsp"*60 + "<em>by Elyès Chenik, Yoni Hassine\
            and Baptiste Souilhac</em>", margin=(0, 0, 100, 0), align="start")

my_Strategy.get_df_pnl_greeks(greek, step, shift_time, shift_vol)
my_Strategy.create_figures(greek)

bokeh_doc = curdoc()

bokeh_doc.add_root(row(column(info,
                              data,
                              column(select_exchange,
                                     select_stock,
                                     slider_rate,
                                     spinner_qty_stocks, align="center"),
                              column(select_maturity,
                                     select_type,
                                     select_strike,
                                     spinner_qty,
                                     button_add, align="center",
                                     background="lightsteelblue"),
                              column(select_greek,
                                     slider_step,
                                     slider_time,
                                     slider_vol),
                              align="center",
                              background="aliceblue"),
                       column(row(column(welcome,
                                         your_pf,
                                         my_Strategy.options_table,
                                         align="center",
                                         background="white"),
                                  column(my_Strategy.pnl_fig,
                                         my_Strategy.pnl_table,
                                         sizing_mode="scale_width"),
                                  column(my_Strategy.greeks_fig,
                                         my_Strategy.greeks_table,
                                         sizing_mode="scale_width"),
                                  sizing_mode="scale_height"),
                              align="center"), background="white"))
bokeh_doc.title = "Options strategy builder"
