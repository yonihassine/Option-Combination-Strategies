# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 16:03:22 2021

@author: hassi
"""

from OptionClass import Option, Strategy
# Test of the option price and greeks for 2 different options

my_option1 = Option(1900, 1900, 30, 0.15, 0, 0, "Call")
my_option2 = Option(450, 495, 60, 0.22, 0.02, 0.01, "Put")


def test_OptionClass_Price():
    assert round(my_option1.BSprice, 3) == 32.594
    assert round(my_option2.BSprice, 3) == 46.669


def test_OptionClass_delta():
    assert round(my_option1.Delta, 3) == 0.509
    assert round(my_option2.Delta, 3) == -0.838


def test_OptionClass_gamma():
    assert round(my_option1.Delta, 3) == 0.509
    assert round(my_option2.Delta, 3) == -0.838


def test_OptionClass_vega():
    assert round(my_option1.Vega, 4) == 2.1726
    assert round(my_option2.Vega, 4) == 0.4472


def test_OptionClass_theta():
    assert round(my_option1.Theta, 4) == -0.5431
    assert round(my_option2.Theta, 4) == -0.0588


# Test of price and greeks of a strategy corresponding to a Long Butterfly

my_Strategy = Strategy()
my_Strategy.add_option(1880, 30, 0.16, 0, "Call", 10)
my_Strategy.add_option(1900, 30, 0.16, 0, "Call", -20)
my_Strategy.add_option(1920, 30, 0.16, 0, "Call", 10)


def test_StrategyClass_Price():
    assert round(my_Strategy.price(1900), 3) == 18.226


def test_StrategyClass_Delta():
    assert round(my_Strategy.Delta(1900), 5) == 0.00463


def test_StrategyClass_Gamma():
    assert round(my_Strategy.Gamma(1900), 4) == -0.0024


def test_StrategyClass_Vega():
    assert round(my_Strategy.Vega(1900), 4) == -1.1298


def test_StrategyClass_Theta():
    assert round(my_Strategy.Theta(1900), 4) == 0.3013
