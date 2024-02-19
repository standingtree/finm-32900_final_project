"""
This module contains functions for pricing European call and put options using the Black-Scholes-Merton model,
as well as calculating implied volatility.

Functions:
- european_call_price: Calculates the price of a European call option.
- european_put_price: Calculates the price of a European put option.
- norm_cdf: Calculates the cumulative distribution function (CDF) of the standard normal distribution.
- norm_pdf: Calculates the probability density function (PDF) of the standard normal distribution.
- calc_vega: Calculates the option vega using the Black-Scholes-Merton model.
- iv_objective: Calculates the difference between the market price and the theoretical price of an option.
- calc_implied_volatility: Calculates the implied volatility of an option using the bisection method.

Usage:
1. Import the module:
    import bsm_pricer

2. Call the desired functions:
    call_price = bsm_pricer.european_call_price(S, K, r, T, sigma)
    put_price = bsm_pricer.european_put_price(S, K, r, T, sigma)
    implied_volatility = bsm_pricer.calc_implied_volatility(market_price, S, K, T, r, option_type)
"""

import math
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize


def european_call_price(S, K, r, T, sigma):
    """
    Calculates the price of a European call option using the Black-Scholes-Merton model.

    Parameters:
    S (float): Current price of the underlying asset
    K (float): Strike price of the option
    r (float): Risk-free interest rate
    T (float): Time to expiration of the option (in years)
    sigma (float): Volatility of the underlying asset. Can be implied or historical, with appropriate interpretation of results.

    Returns:
    float: Price of the European call option
    """
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    call_price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    return call_price




def european_put_price(S, K, r, T, sigma):
    """
    Calculates the price of a European put option using the Black-Scholes-Merton model.

    Parameters:
    S (float): The current price of the underlying asset.
    K (float): The strike price of the option.
    r (float): The risk-free interest rate.
    T (float): The time to expiration of the option in years.
    sigma (float): The volatility of the underlying asset. Can be implied or historical, with appropriate interpretation of results.

    Returns:
    float: The price of the European put option.
    """
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    put_price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    return put_price


def european_sigma( Bid, S, K, r, T, type = 'C', guess = 0.1):
    if type == 'C': 
        funct = lambda sigma : (european_call_price(S,K,r,T, sigma) - Bid)**2
    if type == 'P':  
        funct = lambda sigma : (european_put_price(S,K,r,T, sigma) - Bid)**2 
    result = minimize(funct, guess, bounds = [(0, None)]) 
    return result[0]

def norm_cdf(x):
    """
    Calculates the cumulative distribution function (CDF) of the standard normal distribution.

    Parameters:
    x (float): The value at which to evaluate the CDF.

    Returns:
    float: The CDF value at x.
    """
    # return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    return norm.cdf(x)


def norm_pdf(x):
    """
    Calculates the probability density function (PDF) of the standard normal distribution.

    Parameters:
    x (float): The value at which to evaluate the PDF.

    Returns:
    float: The PDF value at x.
    """
    # return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)
    return norm.pdf(x)


def calc_vega(S, K, T, r, sigma):
    '''Calculate option vega using Black-Scholes-Merton model.'''
    
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * norm_pdf(d1) * np.sqrt(T)



def iv_objective(sigma, market_price, S, K, T, r, option_type):
    """
    Objective function to calculate implied volatility.
    """
    
    if option_type=='call':
        theoretical_price = european_call_price(S=S, K=K, T=T, r=r, sigma=sigma)
    elif option_type=='put':
        theoretical_price = european_put_price(S=S, K=K, T=T, r=r, sigma=sigma)
        
    # print(option_type, 'price:',theoretical_price, sigma, market_price, (theoretical_price - market_price)**2)
    return (theoretical_price - market_price)**2


# Function to calculate implied volatility
def calc_implied_volatility(market_price, S, K, T, r, option_type, tol=1e-12, max_iter=1000):
    """
    Calculate implied volatility using scipy.optimize.minimize.
    
    """
    # Initial guess for volatility
    initial_guess = [0.5]
    
    # Bounds for volatility (must be positive)
    bounds = [(0.00001, 5.0)]
    
    # Minimize the objective function
    result = minimize(iv_objective, initial_guess, args=(market_price, S, K, T, r, option_type),
                      bounds=bounds, method='L-BFGS-B', options={'eps': 1e-15, 'gtol': 1e-15})
    
    #print('result:', result)
    if result.success:
        return result.x[0]  # Return the optimized volatility
    else:
        raise ValueError("Optimization was not successful. Try different bounds or initial guess.")
        


if __name__=='__main__':
    # take inputs from user
    S = float(input("Enter the current price of the underlying asset: "))
    K = float(input("Enter the strike price of the option: "))
    r = float(input("Enter the risk-free interest rate: "))
    T = float(input("Enter the time to expiration of the option in years: "))
    sigma = float(input("Enter the volatility of the underlying asset: "))
    print('European call option price:', european_call_price(S=S, K=K, r=r, T=T, sigma=sigma))
    print('European put option price:', european_put_price(S=S, K=K, r=r, T=T, sigma=sigma))
    
    print('Implied volatility:', calc_implied_volatility(market_price=30, S=S, K=K, r=r, T=T, option_type='call'))
    
    
    
