import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import warnings
warnings.filterwarnings('ignore')

from BlackScholesClass import BlackScholes
from MonteCarlo import MonteCarlo
from BinomialTree import BinomialTree

st.set_page_config(page_title="Option Pricer", page_icon="📈", layout="wide")
st.title("Black-Scholes Option Pricing Suite")
st.markdown("Interactive pricer with Greeks, Monte Carlo, Binomial Tree, and live IV surface.")

# ── Sidebar Inputs ────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Parameters")

with st.sidebar.expander("Option Inputs", expanded=True):
    S     = st.number_input("Spot Price (S)",       value=100.0, step=1.0)
    K     = st.number_input("Strike Price (K)",     value=100.0, step=1.0)
    T     = st.number_input("Time to Expiry (years)", value=1.0, min_value=0.01, step=0.1)
    r     = st.number_input("Risk-Free Rate",       value=0.05, step=0.01, format="%.4f")
    sigma = st.number_input("Volatility (σ)",       value=0.20, step=0.01, format="%.4f")
    q     = st.number_input("Dividend Yield (q)",   value=0.00, step=0.01, format="%.4f")
    opt   = st.selectbox("Option Type", ["call", "put"])

with st.sidebar.expander("Monte Carlo Settings"):
    mc_sims = st.number_input("Simulations", value=100_000, step=10_000)

with st.sidebar.expander("Binomial Tree Settings"):
    bt_steps = st.number_input("Tree Steps", value=500, step=50)

# ── Compute ───────────────────────────────────────────────────────────────────
bs_price  = BlackScholes.call_price(S, K, T, r, sigma, q) if opt == 'call' else BlackScholes.put_price(S, K, T, r, sigma, q)
greeks    = BlackScholes.all_greeks(S, K, T, r, sigma, opt, q)
mc_price, mc_se = MonteCarlo.price(S, K, T, r, sigma, opt, int(mc_sims))
bt_euro   = BinomialTree.price(S, K, T, r, sigma, opt, american=False, steps=int(bt_steps))
bt_amer   = BinomialTree.price(S, K, T, r, sigma, opt, american=True,  steps=int(bt_steps))
pcp       = BlackScholes.put_call_parity_check(
    BlackScholes.call_price(S, K, T, r, sigma, q),
    BlackScholes.put_price(S, K, T, r, sigma, q),
    S, K, T, r, q
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Pricing", "🔢 Greeks", "📊 Visualizations", "🌐 IV Surface", "📐 Implied Vol"
])

# ════════════════════════════════════════════════════════════
# Tab 1 — Pricing
# ════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Option Price Comparison")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Black-Scholes", f"${bs_price:.4f}")
    c2.metric("Monte Carlo",   f"${mc_price:.4f}", f"±{mc_se*1.96:.4f} (95% CI)")
    c3.metric("Binomial (European)", f"${bt_euro:.4f}")
    c4.metric("Binomial (American)", f"${bt_amer:.4f}",
              f"+{bt_amer - bt_euro:.4f} early exercise premium" if bt_amer > bt_euro else None)

    st.divider()
    st.subheader("Put-Call Parity Check")
    col1, col2 = st.columns(2)
    with col1:
        pcp_df = pd.DataFrame(list(pcp.items()), columns=["Metric", "Value"]).set_index("Metric")
        st.dataframe(pcp_df, use_container_width=True)
    with col2:
        if pcp["passes"]:
            st.success("✅ Put-call parity holds — model is internally consistent.")
        else:
            st.error("❌ Put-call parity violated — check your inputs.")
        st.latex(r"C - P = S e^{-qT} - K e^{-rT}")

    st.divider()
    st.subheader("Model Notes")
    st.info(
        "**Monte Carlo** simulates 100k GBM paths — standard error shows estimation uncertainty.  \n"
        "**American options** can be exercised early. The early exercise premium is non-zero mainly for puts "
        "and deep ITM calls with dividends — Black-Scholes cannot capture this."
    )

# ════════════════════════════════════════════════════════════
# Tab 2 — Greeks
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Option Greeks")

    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("Delta (Δ)", f"{greeks['delta']:.4f}", help="Price change per $1 move in S")
    g2.metric("Gamma (Γ)", f"{greeks['gamma']:.4f}", help="Delta change per $1 move in S")
    g3.metric("Vega (ν)",  f"{greeks['vega']:.4f}",  help="Price change per 1% vol move")
    g4.metric("Theta (θ)", f"{greeks['theta']:.4f}", help="Price decay per calendar day")
    g5.metric("Rho (ρ)",   f"{greeks['rho']:.4f}",   help="Price change per 1% rate move")

    st.divider()
    st.subheader("Greeks vs Spot Price")

    spots  = np.linspace(S * 0.5, S * 1.5, 300)
    delta  = [BlackScholes.delta(s, K, T, r, sigma, opt, q) for s in spots]
    gamma  = [BlackScholes.gamma(s, K, T, r, sigma, q)      for s in spots]
    vega_v = [BlackScholes.vega(s, K, T, r, sigma, q)       for s in spots]
    theta  = [BlackScholes.theta(s, K, T, r, sigma, opt, q) for s in spots]
    rho_v  = [BlackScholes.rho(s, K, T, r, sigma, opt, q)   for s in spots]

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.plot(spots, delta, color='steelblue', linewidth=2, label='Delta')
        ax2 = ax.twinx()
        ax2.plot(spots, gamma, color='tomato', linewidth=2, linestyle='--', label='Gamma')
        ax.axvline(K, color='grey', linestyle=':', linewidth=1)
        ax.axvline(S, color='black', linestyle=':', linewidth=1, label='Current S')
        ax.set_xlabel('Spot Price')
        ax.set_ylabel('Delta', color='steelblue')
        ax2.set_ylabel('Gamma', color='tomato')
        ax.set_title('Delta & Gamma')
        lines = ax.get_lines() + ax2.get_lines()
        ax.legend(lines, [l.get_label() for l in lines], fontsize=8)
        ax.grid(alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, axes = plt.subplots(1, 3, figsize=(9, 3.5))
        for ax, name, vals, color in zip(
            axes,
            ['Vega (per 1%)', 'Theta (per day)', 'Rho (per 1%)'],
            [vega_v, theta, rho_v],
            ['mediumseagreen', 'darkorange', 'mediumpurple']
        ):
            ax.plot(spots, vals, color=color, linewidth=2)
            ax.axvline(K, color='grey', linestyle=':', linewidth=1)
            ax.axvline(S, color='black', linestyle=':', linewidth=1)
            ax.set_title(name, fontsize=9)
            ax.set_xlabel('Spot', fontsize=8)
            ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.divider()
    greeks_df = pd.DataFrame({
        "Greek": ["Delta (Δ)", "Gamma (Γ)", "Vega (ν)", "Theta (θ)", "Rho (ρ)"],
        "Value": [f"{greeks['delta']:.6f}", f"{greeks['gamma']:.6f}",
                  f"{greeks['vega']:.6f}", f"{greeks['theta']:.6f}", f"{greeks['rho']:.6f}"],
        "Interpretation": [
            "Option price moves this much per $1 in spot",
            "Delta changes this much per $1 in spot",
            "Option price moves this much per 1% vol increase",
            "Option loses this much per calendar day",
            "Option price moves this much per 1% rate increase",
        ]
    }).set_index("Greek")
    st.dataframe(greeks_df, use_container_width=True)

# ════════════════════════════════════════════════════════════
# Tab 3 — Visualizations
# ════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Option Price Heatmap — Spot × Volatility")

    spots_h = np.linspace(S * 0.6, S * 1.4, 60)
    vols_h  = np.linspace(0.05, 0.80, 60)
    SG, VG  = np.meshgrid(spots_h, vols_h)

    fn = np.vectorize(
        lambda s, v: BlackScholes.call_price(s, K, T, r, v, q) if opt == 'call'
                     else BlackScholes.put_price(s, K, T, r, v, q)
    )
    prices_h = fn(SG, VG)

    fig, ax = plt.subplots(figsize=(10, 6))
    hm = ax.contourf(SG, VG * 100, prices_h, levels=30, cmap='RdYlGn')
    fig.colorbar(hm, ax=ax, label='Option Price ($)')
    ax.axvline(K, color='white', linestyle='--', linewidth=1.5, label=f'Strike K={K}')
    ax.axvline(S, color='cyan',  linestyle='--', linewidth=1.5, label=f'Spot S={S}')
    ax.axhline(sigma * 100, color='yellow', linestyle='--', linewidth=1.5, label=f'Current σ={sigma:.0%}')
    ax.set_xlabel('Spot Price ($)')
    ax.set_ylabel('Implied Volatility (%)')
    ax.set_title(f'{opt.capitalize()} Price Heatmap  (K={K}, T={T:.2f}y, r={r:.1%})')
    ax.legend(fontsize=9)
    st.pyplot(fig)
    plt.close(fig)

    st.divider()
    st.subheader("Delta & Gamma Across Moneyness")

    moneyness = np.linspace(0.5, 1.5, 300)
    spots_m   = moneyness * K
    delta_m   = np.array([BlackScholes.delta(s, K, T, r, sigma, opt, q) for s in spots_m])
    gamma_m   = np.array([BlackScholes.gamma(s, K, T, r, sigma, q) for s in spots_m])

    fig, ax1 = plt.subplots(figsize=(9, 4))
    ax2 = ax1.twinx()
    ax1.plot(moneyness, delta_m, color='steelblue', linewidth=2, label='Delta')
    ax2.plot(moneyness, gamma_m, color='tomato',    linewidth=2, linestyle='--', label='Gamma')
    ax1.axvline(1.0, color='grey',  linestyle=':',  linewidth=1, label='ATM')
    ax1.axvline(S/K, color='black', linestyle='--', linewidth=1, label=f'Current S/K={S/K:.2f}')
    ax1.set_xlabel('Moneyness (S/K)')
    ax1.set_ylabel('Delta', color='steelblue')
    ax2.set_ylabel('Gamma', color='tomato')
    ax1.set_title(f'Delta & Gamma vs Moneyness — {opt.capitalize()}  (T={T:.2f}y, σ={sigma:.0%})')
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], fontsize=8)
    ax1.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

# ════════════════════════════════════════════════════════════
# Tab 4 — Live IV Surface
# ════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Live Implied Volatility Surface")
    st.write("Fetches a live options chain and plots IV across strikes and expiries.")

    col1, col2, col3 = st.columns(3)
    ticker      = col1.text_input("Ticker", value="SPY")
    iv_opt_type = col2.selectbox("Chain", ["call", "put"], key="iv_opt")
    max_exp     = col3.slider("Max Expiries", 3, 12, 6)

    if st.button("Fetch & Plot IV Surface"):
        with st.spinner(f"Fetching options chain for {ticker}…"):
            try:
                import yfinance as yf
                stk      = yf.Ticker(ticker)
                spot     = stk.fast_info['last_price']
                expiries = stk.options[:max_exp]
                today    = datetime.date.today()

                all_strikes, all_T, all_iv = [], [], []

                for expiry in expiries:
                    exp_date = datetime.datetime.strptime(expiry, '%Y-%m-%d').date()
                    T_exp = (exp_date - today).days / 365
                    if T_exp <= 0.01:
                        continue
                    chain = stk.option_chain(expiry)
                    df    = chain.calls if iv_opt_type == 'call' else chain.puts
                    for _, row in df.iterrows():
                        if row.get('volume', 0) < 5:
                            continue
                        mid = (row['bid'] + row['ask']) / 2
                        if mid <= 0 or row['bid'] <= 0:
                            continue
                        iv = BlackScholes.implied_volatility(
                            mid, spot, row['strike'], T_exp, r, iv_opt_type)
                        if not np.isnan(iv) and 0.01 < iv < 5.0:
                            all_strikes.append(row['strike'])
                            all_T.append(T_exp)
                            all_iv.append(iv * 100)

                if len(all_strikes) < 5:
                    st.warning("Not enough liquid contracts found.")
                else:
                    from mpl_toolkits.mplot3d import Axes3D  # noqa
                    fig = plt.figure(figsize=(12, 6))
                    ax  = fig.add_subplot(111, projection='3d')
                    sc  = ax.scatter(all_strikes, all_T, all_iv,
                                     c=all_iv, cmap='RdYlGn_r', s=18, alpha=0.85)
                    fig.colorbar(sc, ax=ax, shrink=0.5, label='IV (%)')
                    ax.set_xlabel('Strike ($)')
                    ax.set_ylabel('Time to Expiry (yr)')
                    ax.set_zlabel('IV (%)')
                    ax.set_title(f'{ticker} IV Surface — {iv_opt_type.capitalize()}s  |  Spot: ${spot:.2f}')
                    st.pyplot(fig)
                    plt.close(fig)
                    st.success(f"Plotted {len(all_strikes)} contracts across {len(expiries)} expiries.")

                    # IV smile for nearest expiry
                    st.divider()
                    st.subheader(f"IV Smile — Nearest Expiry ({expiries[0]})")
                    nearest = [(s, iv) for s, t, iv in zip(all_strikes, all_T, all_iv)
                               if abs(t - min(all_T)) < 0.01]
                    if nearest:
                        ns, ni = zip(*sorted(nearest))
                        fig2, ax2 = plt.subplots(figsize=(8, 4))
                        ax2.plot(ns, ni, 'o-', color='steelblue', markersize=5)
                        ax2.axvline(spot, color='tomato', linestyle='--', label=f'Spot ${spot:.2f}')
                        ax2.set_xlabel('Strike ($)')
                        ax2.set_ylabel('IV (%)')
                        ax2.set_title(f'{ticker} IV Smile  ({expiries[0]})')
                        ax2.legend()
                        ax2.grid(alpha=0.3)
                        st.pyplot(fig2)
                        plt.close(fig2)

            except Exception as e:
                st.error(f"Error fetching data: {e}")

# ════════════════════════════════════════════════════════════
# Tab 5 — Implied Volatility Calculator
# ════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Implied Volatility Calculator")
    st.write("Enter a market price and back out the implied volatility using Newton-Raphson.")

    col1, col2 = st.columns(2)
    with col1:
        market_price = st.number_input("Market Option Price", value=10.0, step=0.5)
        iv_type      = st.selectbox("Option Type", ["call", "put"], key="iv_type")
    with col2:
        st.write("")
        st.write("")
        if st.button("Calculate IV"):
            iv = BlackScholes.implied_volatility(market_price, S, K, T, r, iv_type, q)
            if np.isnan(iv):
                st.error("Could not converge. Check that the market price is valid for these inputs.")
            else:
                st.metric("Implied Volatility", f"{iv:.4%}")
                st.success(f"Newton-Raphson converged to σ = {iv:.6f}")

                # Show Greeks at this IV
                st.divider()
                st.subheader("Greeks at Implied Volatility")
                g = BlackScholes.all_greeks(S, K, T, r, iv, iv_type, q)
                g_df = pd.DataFrame({
                    "Greek": list(g.keys()),
                    "Value": [f"{v:.6f}" for v in g.values()]
                }).set_index("Greek")
                st.dataframe(g_df, use_container_width=True)
