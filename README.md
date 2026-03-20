# Black-Scholes Option Pricing Suite

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://black-scholes-option-pricer-in-python-txajqbslrwvq7y9yubga3f.streamlit.app/)

**Live App:** https://black-scholes-option-pricer-in-python-txajqbslrwvq7y9yubga3f.streamlit.app/

---

## What This Is

This is a professional-grade options pricing and risk analysis tool built in Python. It prices financial derivatives (options contracts) using multiple industry-standard models, computes all standard risk metrics (Greeks), and visualizes how option prices and risk change across market conditions.

An **option** is a financial contract that gives the buyer the right — but not the obligation — to buy or sell an asset at a set price (the strike) before a set date (expiry). Pricing these contracts correctly is one of the core problems in quantitative finance.

---

## Models

### Black-Scholes (1973)
The foundational closed-form model for pricing European options. Assumes constant volatility and no dividends. Extended here with the **Merton continuous dividend model** — a one-line adjustment to the d1 formula that accounts for dividend yield, making it applicable to dividend-paying stocks and index options.

### Monte Carlo Simulation
Simulates thousands of possible future stock price paths using Geometric Brownian Motion and averages the discounted payoffs. Returns both a price estimate and a **standard error**, giving a confidence interval around the result. Also prices **Asian options** (path-dependent, no closed-form solution).

### Binomial Tree (Cox-Ross-Rubinstein)
Builds a recombining price tree and works backwards from expiry to price the option. Unlike Black-Scholes, this model can handle **American options**, which allow early exercise. The early exercise premium — the extra value of being able to exercise before expiry — is computed and displayed. This is critical for pricing American puts and dividends-adjusted calls.

---

## Features

### Implied Volatility — Newton-Raphson Solver
Given a market option price, backs out the implied volatility the market is pricing in. Uses the Newton-Raphson method (the industry standard) instead of a brute-force scan — converges in fewer than 10 iterations with near-machine precision.

### Greeks
The five standard sensitivities used by options traders and risk desks for hedging:

| Greek | Measures |
|-------|----------|
| **Delta (Δ)** | Price change per $1 move in the underlying |
| **Gamma (Γ)** | Rate of change of Delta — peaks at-the-money |
| **Vega (ν)** | Price change per 1% move in volatility |
| **Theta (θ)** | Time decay — price lost per calendar day |
| **Rho (ρ)** | Price change per 1% move in interest rates |

### Put-Call Parity Checker
Verifies that call and put prices satisfy the no-arbitrage identity: `C - P = S·e^(-qT) - K·e^(-rT)`. A violation would mean a risk-free profit opportunity exists — useful for validating model output.

### Visualizations
- **Greeks vs Spot** — how each Greek evolves as the stock price moves through ATM
- **Option Price Heatmap** — option price across a spot × volatility grid, showing sensitivity at a glance
- **Delta & Gamma across Moneyness** — the classic gamma risk chart
- **Live IV Smile** — fetches a real options chain and plots implied volatility across strikes for a single expiry
- **Live IV Surface** — 3D implied volatility surface across all liquid strikes and expiries. This is what a volatility desk actually looks at — the shape reveals market-implied skew, term structure, and risk premium

---

## Tech Stack

- `numpy` / `scipy` — numerical computation and statistics
- `matplotlib` — plotting
- `yfinance` — live options chain data
- `streamlit` — web interface

## Installation (Local)

```bash
git clone https://github.com/Spencerpain/Black-Scholes-Option-Pricer-in-python.git
cd Black-Scholes-Option-Pricer-in-python
pip install -r requirements.txt
streamlit run app.py
```

## File Structure

```
├── BlackScholesClass.py   # BS model, Greeks, Newton-Raphson IV, Merton, put-call parity
├── MonteCarlo.py          # Monte Carlo pricer (European + Asian)
├── BinomialTree.py        # CRR binomial tree (European + American, early exercise premium)
├── Visualizations.py      # All plots including live IV surface
├── app.py                 # Streamlit web app
└── requirements.txt
```
