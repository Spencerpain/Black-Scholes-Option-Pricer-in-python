import numpy as np
from scipy.stats import norm


class BlackScholes:
    """
    Black-Scholes European option pricer with full Greeks,
    Newton-Raphson implied volatility, Merton continuous dividend extension,
    and put-call parity validation.

    Parameters
    ----------
    S     : float — current stock price
    K     : float — strike price
    T     : float — time to expiration in years
    r     : float — continuously compounded risk-free rate
    sigma : float — annualised volatility
    q     : float — continuous dividend yield (default 0, Merton extension)
    """

    # ── Core d1 / d2 ─────────────────────────────────────────────────────────

    @staticmethod
    def _d1(S, K, T, r, sigma, q=0.0):
        return (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    @staticmethod
    def _d2(S, K, T, r, sigma, q=0.0):
        return BlackScholes._d1(S, K, T, r, sigma, q) - sigma * np.sqrt(T)

    # ── Option Prices ─────────────────────────────────────────────────────────

    @staticmethod
    def call_price(S, K, T, r, sigma, q=0.0):
        """Black-Scholes (Merton) call price. Set q=0 for no dividends."""
        d1 = BlackScholes._d1(S, K, T, r, sigma, q)
        d2 = BlackScholes._d2(S, K, T, r, sigma, q)
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

    @staticmethod
    def put_price(S, K, T, r, sigma, q=0.0):
        """Black-Scholes (Merton) put price. Set q=0 for no dividends."""
        d1 = BlackScholes._d1(S, K, T, r, sigma, q)
        d2 = BlackScholes._d2(S, K, T, r, sigma, q)
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

    # ── In-the-Money Probabilities ────────────────────────────────────────────

    @staticmethod
    def call_in_the_money(S, K, T, r, sigma, q=0.0):
        """Risk-neutral probability call expires ITM: N(d2)."""
        return norm.cdf(BlackScholes._d2(S, K, T, r, sigma, q))

    @staticmethod
    def put_in_the_money(S, K, T, r, sigma, q=0.0):
        """Risk-neutral probability put expires ITM: N(-d2)."""
        return norm.cdf(-BlackScholes._d2(S, K, T, r, sigma, q))

    # ── Greeks ────────────────────────────────────────────────────────────────

    @staticmethod
    def delta(S, K, T, r, sigma, option_type='call', q=0.0):
        """
        Delta — sensitivity of option price to a $1 move in S.
        Call delta: exp(-qT) * N(d1)
        Put  delta: exp(-qT) * (N(d1) - 1)
        """
        d1 = BlackScholes._d1(S, K, T, r, sigma, q)
        if option_type == 'call':
            return np.exp(-q * T) * norm.cdf(d1)
        return np.exp(-q * T) * (norm.cdf(d1) - 1)

    @staticmethod
    def gamma(S, K, T, r, sigma, q=0.0):
        """
        Gamma — rate of change of delta per $1 move in S (same for calls and puts).
        Gamma = exp(-qT) * n(d1) / (S * sigma * sqrt(T))
        """
        d1 = BlackScholes._d1(S, K, T, r, sigma, q)
        return np.exp(-q * T) * norm.pdf(d1) / (S * sigma * np.sqrt(T))

    @staticmethod
    def vega(S, K, T, r, sigma, q=0.0):
        """
        Vega — option price change per 1% increase in volatility.
        Raw vega = S * exp(-qT) * n(d1) * sqrt(T)
        Returned per 1% vol move (divided by 100).
        """
        d1 = BlackScholes._d1(S, K, T, r, sigma, q)
        return S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) / 100

    @staticmethod
    def theta(S, K, T, r, sigma, option_type='call', q=0.0):
        """
        Theta — option price decay per calendar day (divided by 365).
        """
        d1 = BlackScholes._d1(S, K, T, r, sigma, q)
        d2 = BlackScholes._d2(S, K, T, r, sigma, q)
        common = -(S * np.exp(-q * T) * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
        if option_type == 'call':
            return (common - r * K * np.exp(-r * T) * norm.cdf(d2)
                    + q * S * np.exp(-q * T) * norm.cdf(d1)) / 365
        return (common + r * K * np.exp(-r * T) * norm.cdf(-d2)
                - q * S * np.exp(-q * T) * norm.cdf(-d1)) / 365

    @staticmethod
    def rho(S, K, T, r, sigma, option_type='call', q=0.0):
        """
        Rho — option price change per 1% increase in risk-free rate.
        """
        d2 = BlackScholes._d2(S, K, T, r, sigma, q)
        if option_type == 'call':
            return K * T * np.exp(-r * T) * norm.cdf(d2) / 100
        return -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    @staticmethod
    def all_greeks(S, K, T, r, sigma, option_type='call', q=0.0):
        """Return all Greeks as a dictionary."""
        return {
            'delta': BlackScholes.delta(S, K, T, r, sigma, option_type, q),
            'gamma': BlackScholes.gamma(S, K, T, r, sigma, q),
            'vega':  BlackScholes.vega(S, K, T, r, sigma, q),
            'theta': BlackScholes.theta(S, K, T, r, sigma, option_type, q),
            'rho':   BlackScholes.rho(S, K, T, r, sigma, option_type, q),
        }

    # ── Implied Volatility — Newton-Raphson ───────────────────────────────────

    @staticmethod
    def implied_volatility(market_price, S, K, T, r, option_type='call',
                           q=0.0, tol=1e-8, max_iter=200):
        """
        Newton-Raphson implied volatility solver.
        Converges quadratically — typically < 10 iterations.
        Returns np.nan if it fails to converge.
        """
        sigma = 0.2  # initial guess

        for _ in range(max_iter):
            if option_type == 'call':
                price = BlackScholes.call_price(S, K, T, r, sigma, q)
            else:
                price = BlackScholes.put_price(S, K, T, r, sigma, q)

            diff = price - market_price
            if abs(diff) < tol:
                return sigma

            v = BlackScholes.vega(S, K, T, r, sigma, q) * 100  # raw vega
            if abs(v) < 1e-10:
                break

            sigma -= diff / v
            sigma = max(1e-6, min(sigma, 10.0))  # keep in (0, 1000%)

        return np.nan

    # Legacy names kept for backwards compatibility
    @staticmethod
    def call_implied_volatility(price, S, K, T, r):
        return BlackScholes.implied_volatility(price, S, K, T, r, 'call')

    @staticmethod
    def put_implied_volatility(price, S, K, T, r):
        return BlackScholes.implied_volatility(price, S, K, T, r, 'put')

    # ── Put-Call Parity ───────────────────────────────────────────────────────

    @staticmethod
    def put_call_parity_check(call_price, put_price, S, K, T, r, q=0.0, tol=0.01):
        """
        Verify put-call parity: C - P = S*exp(-qT) - K*exp(-rT).
        Returns a dict with the LHS, RHS, difference, and pass/fail.
        """
        lhs = call_price - put_price
        rhs = S * np.exp(-q * T) - K * np.exp(-r * T)
        diff = abs(lhs - rhs)
        return {
            'lhs (C - P)':        round(lhs,  6),
            'rhs (S·e^-qT - K·e^-rT)': round(rhs, 6),
            'difference':         round(diff, 6),
            'passes':             diff < tol,
        }
