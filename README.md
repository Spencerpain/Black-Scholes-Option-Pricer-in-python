# Black-Scholes Option Pricing Model

This project implements the Black-Scholes model to calculate prices and probabilities for European call and put options without dividends. It also includes functions for calculating implied volatility.

## Overview

The Black-Scholes model is a widely used mathematical model for pricing European options. This implementation calculates:

- **Call and Put Option Prices**: Using the Black-Scholes formula.
- **Probability of Ending In-the-Money**: The likelihood that an option will expire in-the-money.
- **Implied Volatility Calculation**: Based on a given option price, the model estimates implied volatility.

## Black-Scholes Formulas

1. **Call Option Price**:
   \[
   C = S \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)
   \]
   where:
   - \( S \): Current stock price
   - \( K \): Strike price
   - \( T \): Time to expiration (in years)
   - \( r \): Risk-free interest rate
   - \( N(d) \): Cumulative distribution function of the standard normal distribution
   - \( d_1 \) and \( d_2 \): Calculated as follows:
   
   \[
   d_1 = \frac{\ln\left(\frac{S}{K}\right) + \left(r + \frac{\sigma^2}{2}\right) T}{\sigma \sqrt{T}}
   \]
   \[
   d_2 = d_1 - \sigma \sqrt{T}
   \]

2. **Put Option Price**:
   \[
   P = K \cdot e^{-rT} \cdot N(-d_2) - S \cdot N(-d_1)
   \]

3. **Probability of Ending In-the-Money**:
   - **Call Option**: The probability that the call option will end up in-the-money (i.e., the stock price at expiration will be above the strike price) is given by \( N(d_2) \).
   - **Put Option**: The probability that the put option will end up in-the-money is \( 1 - N(d_2) \).

4. **Implied Volatility**:
   Implied volatility is estimated by iteratively adjusting volatility until the theoretical option price matches the observed market price. This project uses a simple iterative search to approximate implied volatility.

## Features

- **Option Pricing**: Computes prices for both call and put options using the Black-Scholes model.
- **In-the-Money Probability**: Calculates the probability that a call or put option will end in-the-money at expiration.
- **Implied Volatility**: Finds the implied volatility for call and put options based on the target option price.

## Requirements

- Python 3.x
- `numpy`
- `scipy`

## Installation

1. Clone the repository:

2. Install required packages

3. Choose values of S, K, T, r, and sigma

4. Run the code

   ```bash
   git clone https://github.com/yourusername/black-scholes-option-pricing.git
   cd black-scholes-option-pricing
