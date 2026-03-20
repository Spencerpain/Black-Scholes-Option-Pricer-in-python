import numpy as np


class BinomialTree:
    """
    Cox-Ross-Rubinstein (CRR) binomial tree option pricer.

    Handles both European and American options.
    American options allow early exercise — something Black-Scholes cannot price.
    This makes the binomial tree essential for pricing American puts.
    """

    @staticmethod
    def price(S, K, T, r, sigma, option_type='call',
              american=False, steps=500):
        """
        Price an option using the CRR binomial tree.

        Parameters
        ----------
        S           : float — current stock price
        K           : float — strike price
        T           : float — time to expiry in years
        r           : float — risk-free rate
        sigma       : float — annualised volatility
        option_type : str   — 'call' or 'put'
        american    : bool  — True for American (early exercise), False for European
        steps       : int   — number of tree steps (higher = more accurate)

        Returns
        -------
        float — option price
        """
        dt      = T / steps
        u       = np.exp(sigma * np.sqrt(dt))       # up factor
        d       = 1.0 / u                            # down factor (ensures recombining tree)
        p       = (np.exp(r * dt) - d) / (u - d)    # risk-neutral up probability
        discount = np.exp(-r * dt)

        # Terminal stock prices (vectorised)
        j  = np.arange(steps + 1)
        ST = S * (u ** (steps - j)) * (d ** j)

        # Terminal payoffs
        if option_type == 'call':
            V = np.maximum(ST - K, 0.0)
        elif option_type == 'put':
            V = np.maximum(K - ST, 0.0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        # Backward induction through the tree
        for i in range(steps - 1, -1, -1):
            j  = np.arange(i + 1)
            ST = S * (u ** (i - j)) * (d ** j)
            V  = discount * (p * V[:-1] + (1 - p) * V[1:])

            # American early exercise check
            if american:
                if option_type == 'call':
                    V = np.maximum(V, ST - K)
                else:
                    V = np.maximum(V, K - ST)

        return float(V[0])

    @staticmethod
    def early_exercise_premium(S, K, T, r, sigma, option_type='put', steps=500):
        """
        Compute the early exercise premium:
        the additional value of an American option over its European equivalent.
        This is non-zero primarily for American puts and deep ITM calls with dividends.
        """
        american = BinomialTree.price(S, K, T, r, sigma, option_type, american=True,  steps=steps)
        european = BinomialTree.price(S, K, T, r, sigma, option_type, american=False, steps=steps)
        return american - european
