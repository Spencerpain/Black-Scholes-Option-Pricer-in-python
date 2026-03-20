import numpy as np


class MonteCarlo:
    """
    Monte Carlo option pricer using Geometric Brownian Motion.

    Supports European call and put options.
    Returns both the price estimate and the standard error,
    so you can report a confidence interval around the estimate.
    """

    @staticmethod
    def price(S, K, T, r, sigma, option_type='call',
              simulations=100_000, seed=42):
        """
        Price a European option via Monte Carlo simulation.

        Parameters
        ----------
        S           : float — current stock price
        K           : float — strike price
        T           : float — time to expiry in years
        r           : float — risk-free rate
        sigma       : float — annualised volatility
        option_type : str   — 'call' or 'put'
        simulations : int   — number of GBM paths (default 100,000)
        seed        : int   — random seed for reproducibility

        Returns
        -------
        price : float — discounted expected payoff
        se    : float — standard error (half-width of 95% CI ≈ 1.96 * se)
        """
        rng = np.random.default_rng(seed)
        Z   = rng.standard_normal(simulations)

        # Terminal stock price under risk-neutral measure
        ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)

        if option_type == 'call':
            payoffs = np.maximum(ST - K, 0.0)
        elif option_type == 'put':
            payoffs = np.maximum(K - ST, 0.0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        discount = np.exp(-r * T)
        price    = discount * np.mean(payoffs)
        se       = discount * np.std(payoffs, ddof=1) / np.sqrt(simulations)

        return price, se

    @staticmethod
    def price_asian(S, K, T, r, sigma, option_type='call',
                    steps=252, simulations=50_000, seed=42):
        """
        Price an Asian (arithmetic average) option via Monte Carlo.
        Asian options are path-dependent and have no closed-form BS solution.
        """
        rng = np.random.default_rng(seed)
        dt  = T / steps
        Z   = rng.standard_normal((simulations, steps))

        # Simulate full paths
        increments = (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
        log_paths  = np.cumsum(increments, axis=1)
        paths      = S * np.exp(log_paths)          # shape: (simulations, steps)

        avg_price = paths.mean(axis=1)

        if option_type == 'call':
            payoffs = np.maximum(avg_price - K, 0.0)
        else:
            payoffs = np.maximum(K - avg_price, 0.0)

        discount = np.exp(-r * T)
        price    = discount * np.mean(payoffs)
        se       = discount * np.std(payoffs, ddof=1) / np.sqrt(simulations)

        return price, se
