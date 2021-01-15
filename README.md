# Option Combination Strategies

OPC (Option Combination Strategies) is a powerful pricing tool for options combination strategies, wich calculates instantaneous greeks and P&L with interactive plots using Bokeh server. 


## Getting Started


### Prerequisites

This tool need the following libraries to be installed : `numpy`, `scipy`, `pandas`, `yfinance`, `bokeh`, `pytest`, `forex_python`

For example, you can simply install `bokeh` from PyPI by running the command:
```
pip install bokeh
```

### Launch the Bokeh Server

To run the app on a Bokeh server, we execute:

```
bokeh serve --show strat_server.py
```

The --show option will cause a browser to open up a new tab automatically to the address of the running application, which in this case is:

```
http://localhost:5006/strat_server
```

### Quick Start

An option strategy can be initialized by selecting:
1. The **exchange** on which you want to trade;
2. The **stock** you want to trade among more than 4000 stocks;
3. The **interest rate**
4. The **maturity**  of the options, selected among the real maturities quoted on the markets;
5. The **type of option**, ie *call* or *put* 
6. The **strike** of the option, selected among the real strike prices quoted on the markets;
7. The number of options (positive to *buy* or negative to *sell*);
8. Click on the green button "*Add Option*"
You will notice than on the top of the page, your portfolio has been updated

To add other options to the strategy, redo steps 4 to 8.

To remove options from your strategy, you just have to add the opposite number of options to your portfolio

Finally, one can add underlying stocks in the strategy (positive to *buy* or negative to *sell*).

*Here is an example to create a strategy on Apple Inc. stock which is traded on the NASDAQ. This strategy will* 
*consist in buying 100 call options with maturity 3 months (April 16th 2021, ie 91 days) and strike 130 (ie ATM options given the current spot price). We assume the risk free rate to be 0.20%.*


<p align="center">
<img src="https://github.com/yonihassine/Option-Combination-Strategies/blob/main/img/100call.PNG" />
</p>

<br/><br/>

Click on "*Add Option*". Then go back to the top of the page, you can see your portfolio strategy has been updated.

<p align="center">
<img src="https://github.com/yonihassine/Option-Combination-Strategies/blob/main/img/ptfupdate.PNG" />
</p>

<br/><br/>

Now assume we want to delta hedge the position. We see that the delta of the portfolio is approximately 54.
Hence, we need to short sell 54 stocks to be delta hedged.

<p align="center">
<img src="https://github.com/yonihassine/Option-Combination-Strategies/blob/main/img/deltastock.PNG" />
</p>

<br/><br/>

The 2 plots on the right side represent the P&L and greeks. Greeks can be selected on the left side of the screen. 

Finally, you can add complementary stress. On top of the variations of the underlying price, you can shift the current date by X days (t + X days) and the implied volatility by Y% (new imp vol = imp vol x (1+Y%) ) on the left side of the screen. Doing this, you will be able to graph the P&L of the portfolio versus the underlying price, in X days and/or with Y% variation of the implied volatility.

Here is an example for the instantaneous P&L and Gamma and the shifted P&L and Delta in 6 days with -6.62% move in implied vol.

<p align="center">
<img src="https://github.com/yonihassine/Option-Combination-Strategies/blob/main/img/gamma.PNG" />
</p>

<br/><br/>

<p align="center">
<img src="https://github.com/yonihassine/Option-Combination-Strategies/blob/main/img/plots.PNG" />
</p>

<br/><br/>


## Running the tests

The tests are runned using `pytest` check if an instance of the Option class, initialized with given parameters (spot, strike, maturity, interest rate, dividend yield and volatility) has the same price and greeks than the one given by the Black-Scholes formula.

Example: for an Call option with spot price 1900, strike 1900, 30 days to maturity, risk free rate 0% and dividend yield 0%, the price should be 32.594 approximately.

```
my_option1=Option (1900, 1900, 30, 0.15, 0, 0, "Call")
```
```
assert round(my_option1.BSprice,3) == 32.594
```

Similar tests are performed using an instance of the Strategy class, with several options embedded in it, instead of a single option.

```
my_Strategy = Strategy()
my_Strategy.add_option(1880, 30, 0.16, 0, "Call", 10)
my_Strategy.add_option(1900, 30, 0.16, 0, "Call", -20)
my_Strategy.add_option(1920, 30, 0.16, 0, "Call", 10)
```

```
assert round(my_Strategy.price(1900), 3) == 18.226
```


### Run the tests

You can run the automated tests with the command line:

```
test_Mytest.py
```


## Built With

* [yfinance](https://pypi.org/project/yfinance/) Used to download live market data from Yahoo! finance.
* [forex-python](https://pypi.org/project/forex-python/) Used for Foreign exchange rates and currency conversion

## Authors

* **Elyes CHENIK**
* **Yoni HASSINE**
* **Baptiste SOUILHAC**
