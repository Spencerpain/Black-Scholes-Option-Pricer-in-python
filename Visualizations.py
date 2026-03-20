import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import warnings
import datetime

import yfinance as yf

from BlackScholesClass import BlackScholes


# ── Shared style ──────────────────────────────────────────────────────────────
plt.rcParams.update({'figure.dpi': 120, 'font.size': 10})


class Visualizer:

    # ── Greeks vs Spot ────────────────────────────────────────────────────────

    @staticmethod
    def greeks_vs_spot(K, T, r, sigma, q=0.0,
                       spot_range=None, option_type='call'):
        """
        Plot all five Greeks across a range of spot prices.
        Useful for understanding how risk profile changes with moneyness.
        """
        if spot_range is None:
            spot_range = (K * 0.5, K * 1.5)

        spots = np.linspace(*spot_range, 300)

        delta  = [BlackScholes.delta(s, K, T, r, sigma, option_type, q) for s in spots]
        gamma  = [BlackScholes.gamma(s, K, T, r, sigma, q)               for s in spots]
        vega   = [BlackScholes.vega(s, K, T, r, sigma, q)                 for s in spots]
        theta  = [BlackScholes.theta(s, K, T, r, sigma, option_type, q)  for s in spots]
        rho    = [BlackScholes.rho(s, K, T, r, sigma, option_type, q)     for s in spots]

        fig, axes = plt.subplots(2, 3, figsize=(14, 7))
        fig.suptitle(f'{option_type.capitalize()} Greeks vs Spot  '
                     f'(K={K}, T={T:.2f}y, r={r:.1%}, σ={sigma:.1%})', fontsize=12)

        pairs = [('Delta', delta, 'steelblue'),
                 ('Gamma', gamma, 'tomato'),
                 ('Vega (per 1% vol)', vega, 'mediumseagreen'),
                 ('Theta (per day)', theta, 'darkorange'),
                 ('Rho (per 1% rate)', rho, 'mediumpurple')]

        for ax, (name, values, color) in zip(axes.flat, pairs):
            ax.plot(spots, values, color=color, linewidth=2)
            ax.axvline(K, color='grey', linestyle='--', linewidth=0.8, label='Strike')
            ax.set_title(name)
            ax.set_xlabel('Spot Price ($)')
            ax.set_ylabel(name)
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3)

        axes.flat[-1].set_visible(False)
        plt.tight_layout()
        plt.show()

    # ── Option Price Heatmap ──────────────────────────────────────────────────

    @staticmethod
    def price_heatmap(K, T, r, option_type='call', q=0.0,
                      spot_range=None, vol_range=(0.05, 0.80)):
        """
        Heatmap of option price across a spot × volatility grid.
        Shows at a glance how price sensitivity shifts with vol and moneyness.
        """
        if spot_range is None:
            spot_range = (K * 0.6, K * 1.4)

        spots  = np.linspace(*spot_range, 60)
        vols   = np.linspace(*vol_range,  60)
        S_grid, vol_grid = np.meshgrid(spots, vols)

        if option_type == 'call':
            price_fn = np.vectorize(lambda s, v: BlackScholes.call_price(s, K, T, r, v, q))
        else:
            price_fn = np.vectorize(lambda s, v: BlackScholes.put_price(s, K, T, r, v, q))

        prices = price_fn(S_grid, vol_grid)

        fig, ax = plt.subplots(figsize=(10, 7))
        hm = ax.contourf(S_grid, vol_grid * 100, prices, levels=30, cmap='RdYlGn')
        cbar = fig.colorbar(hm, ax=ax)
        cbar.set_label('Option Price ($)')
        ax.axvline(K, color='white', linestyle='--', linewidth=1.5, label=f'Strike K={K}')
        ax.set_xlabel('Spot Price ($)')
        ax.set_ylabel('Implied Volatility (%)')
        ax.set_title(f'{option_type.capitalize()} Price Heatmap  '
                     f'(K={K}, T={T:.2f}y, r={r:.1%})')
        ax.legend()
        plt.tight_layout()
        plt.show()

    # ── Delta & Gamma Across Moneyness ────────────────────────────────────────

    @staticmethod
    def delta_gamma_moneyness(K, T, r, sigma, q=0.0, option_type='call'):
        """
        Delta and Gamma plotted on the same axes across moneyness (S/K).
        Gamma peaks ATM — this is the classic 'gamma risk' chart.
        """
        moneyness = np.linspace(0.5, 1.5, 300)
        spots = moneyness * K

        delta = np.array([BlackScholes.delta(s, K, T, r, sigma, option_type, q) for s in spots])
        gamma = np.array([BlackScholes.gamma(s, K, T, r, sigma, q) for s in spots])

        fig, ax1 = plt.subplots(figsize=(9, 5))
        ax2 = ax1.twinx()

        ax1.plot(moneyness, delta, color='steelblue', linewidth=2, label='Delta')
        ax2.plot(moneyness, gamma, color='tomato',    linewidth=2, label='Gamma', linestyle='--')
        ax1.axvline(1.0, color='grey', linestyle=':', linewidth=1, label='ATM')

        ax1.set_xlabel('Moneyness (S / K)')
        ax1.set_ylabel('Delta', color='steelblue')
        ax2.set_ylabel('Gamma', color='tomato')
        ax1.set_title(f'Delta & Gamma vs Moneyness — {option_type.capitalize()}  '
                      f'(T={T:.2f}y, σ={sigma:.1%})')

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        ax1.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    # ── IV Smile from Live Options Chain ──────────────────────────────────────

    @staticmethod
    def iv_smile(ticker, expiry_index=0, option_type='call', r=0.05):
        """
        Fetch a live options chain for `ticker` and plot the IV smile
        (implied volatility across strikes for a single expiry).

        Parameters
        ----------
        ticker        : str — Yahoo Finance ticker (e.g. 'AAPL')
        expiry_index  : int — which expiry to use (0 = nearest)
        option_type   : str — 'call' or 'put'
        r             : float — risk-free rate assumption
        """
        stk    = yf.Ticker(ticker)
        S      = stk.fast_info['last_price']
        expiries = stk.options

        if not expiries:
            print(f"No options data found for {ticker}.")
            return

        expiry = expiries[min(expiry_index, len(expiries) - 1)]
        chain  = stk.option_chain(expiry)
        df     = chain.calls if option_type == 'call' else chain.puts

        today = datetime.date.today()
        T = (datetime.datetime.strptime(expiry, '%Y-%m-%d').date() - today).days / 365
        if T <= 0:
            print("Expiry is in the past.")
            return

        strikes, ivs = [], []
        for _, row in df.iterrows():
            mid = (row['bid'] + row['ask']) / 2
            if mid <= 0 or row['bid'] <= 0:
                continue
            iv = BlackScholes.implied_volatility(mid, S, row['strike'], T, r, option_type)
            if not np.isnan(iv) and 0.01 < iv < 5.0:
                strikes.append(row['strike'])
                ivs.append(iv * 100)

        if not strikes:
            print("Could not compute IV for any strike.")
            return

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(strikes, ivs, 'o-', color='steelblue', markersize=4)
        ax.axvline(S, color='tomato', linestyle='--', label=f'Spot S={S:.2f}')
        ax.set_xlabel('Strike Price ($)')
        ax.set_ylabel('Implied Volatility (%)')
        ax.set_title(f'{ticker} IV Smile — {option_type.capitalize()}s  Expiry: {expiry}')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    # ── IV Surface ────────────────────────────────────────────────────────────

    @staticmethod
    def iv_surface(ticker, option_type='call', r=0.05,
                   min_volume=10, max_expiries=8):
        """
        Fetch the full options chain for `ticker`, compute implied volatility
        across all liquid strikes and expiries, and plot a 3D IV surface.

        This is the chart a volatility desk actually uses — it shows the
        term structure of vol and the smile/skew across moneyness simultaneously.

        Parameters
        ----------
        ticker      : str   — Yahoo Finance ticker (e.g. 'SPY')
        option_type : str   — 'call' or 'put'
        r           : float — risk-free rate
        min_volume  : int   — minimum volume filter for liquidity
        max_expiries: int   — number of expiries to include
        """
        print(f"Fetching options chain for {ticker}…")
        stk      = yf.Ticker(ticker)
        S        = stk.fast_info['last_price']
        expiries = stk.options[:max_expiries]
        today    = datetime.date.today()

        all_strikes, all_T, all_iv = [], [], []

        for expiry in expiries:
            exp_date = datetime.datetime.strptime(expiry, '%Y-%m-%d').date()
            T = (exp_date - today).days / 365
            if T <= 0.01:
                continue

            chain = stk.option_chain(expiry)
            df    = chain.calls if option_type == 'call' else chain.puts

            for _, row in df.iterrows():
                if row.get('volume', 0) < min_volume:
                    continue
                mid = (row['bid'] + row['ask']) / 2
                if mid <= 0 or row['bid'] <= 0:
                    continue
                iv = BlackScholes.implied_volatility(
                    mid, S, row['strike'], T, r, option_type)
                if not np.isnan(iv) and 0.01 < iv < 5.0:
                    all_strikes.append(row['strike'])
                    all_T.append(T)
                    all_iv.append(iv * 100)

        if len(all_strikes) < 5:
            print("Not enough liquid options found to plot a surface.")
            return

        strikes = np.array(all_strikes)
        Ts      = np.array(all_T)
        ivs     = np.array(all_iv)

        fig = plt.figure(figsize=(13, 7))
        ax  = fig.add_subplot(111, projection='3d')

        sc = ax.scatter(strikes, Ts, ivs,
                        c=ivs, cmap='RdYlGn_r', s=18, alpha=0.85)
        fig.colorbar(sc, ax=ax, shrink=0.5, label='IV (%)')

        ax.set_xlabel('Strike ($)')
        ax.set_ylabel('Time to Expiry (years)')
        ax.set_zlabel('Implied Volatility (%)')
        ax.set_title(f'{ticker} Implied Volatility Surface — {option_type.capitalize()}s\n'
                     f'Spot: ${S:.2f}  |  {len(all_strikes)} liquid contracts')

        plt.tight_layout()
        plt.show()
        print(f"Plotted {len(all_strikes)} contracts across {len(expiries)} expiries.")
