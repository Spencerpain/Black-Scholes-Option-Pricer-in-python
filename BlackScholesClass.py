import numpy as np
from scipy.stats import norm

class BlackScholes:
    """ 
    Class to calculate the European (no dividends) call and put option prices. 
    This is done using the Black-Scholes formula 
   
    
    S: Price of underlying stock
    K: Strike price
    T: Time until expiration (in years)
    r: Risk-free interest rate 
    sigma: Volatility (standard deviation) of stock 
    """
    @staticmethod
    def _d1(S, K, T, r, sigma):
        return (1 / (sigma * np.sqrt(T))) * (np.log(S/K) + (r + sigma**2 / 2) * T)
    
    @staticmethod
    def _d2(S, K, T, r, sigma):
        return BlackScholes._d1(S, K, T, r, sigma) - sigma * np.sqrt(T)
    
    @staticmethod
    def call_price(S, K, T, r, sigma):
        """ Main method for calculating price of a call option """
        d1 = BlackScholes._d1(S, K, T, r, sigma)
        d2 = BlackScholes._d2(S, K, T, r, sigma)
        return norm.cdf(d1) * S - norm.cdf(d2) * K * np.exp(-r*T)
    
    @staticmethod
    def put_price(S, K, T, r, sigma):
        """ Main method for calculating price of a put option """
        d1 = BlackScholes._d1(S, K, T, r, sigma)
        d2 = BlackScholes._d2(S, K, T, r, sigma)
        return norm.cdf(-d2) * K * np.exp(-r*T) - norm.cdf(-d1) * S
    
    @staticmethod
    def call_in_the_money(S, K, T, r, sigma):
        """ 
        Calculate probability that call option will be in the money at
        maturity according to Black-Scholes.
        """
        d2 = BlackScholes._d2(S, K, T, r, sigma)
        return norm.cdf(d2)
    
    @staticmethod
    def put_in_the_money(S, K, T, r, sigma):
        """ 
        Calculate probability that put option will be in the money at
        maturity according to Black-Scholes.
        """
        d2 = BlackScholes._d2(S, K, T, r, sigma)
        return 1 - norm.cdf(d2)
    
    @staticmethod
    def call_implied_volatility(price, S, K, T, r):
        """ Calculate implied volatility of a call option up to 2 decimals of precision. """
        sigma = 0.0001
        while sigma < 1:
            d1 = BlackScholes._d1(S, K, T, r, sigma)
            d2 = BlackScholes._d2(S, K, T, r, sigma)
            price_implied = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
            if abs(price - price_implied) < 0.0001:
                return sigma
            sigma += 0.0001
        return "Not Found"

    @staticmethod
    def put_implied_volatility(price, S, K, T, r):
        """ Calculate implied volatility of a put option up to 2 decimals of precision. """
        sigma = 0.0001
        while sigma < 1:
            call = BlackScholes.call_price(S, K, T, r, sigma)
            price_implied = K * np.exp(-r*T) - S + call
            if abs(price - price_implied) < 0.0001:
                return sigma
            sigma += 0.0001
        return "Not Found"