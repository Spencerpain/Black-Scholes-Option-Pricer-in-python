
Black-Scholes Option Pricing Model in Python
This project implements the Black-Scholes model to calculate the prices of European-style call and put options. The Black-Scholes model is a widely used analytical solution for pricing options, which allows traders, investors, and researchers to estimate the fair market value of European options on non-dividend-paying stocks. The project includes calculations for implied volatility and probability of options expiring in-the-money.

Features
European Call and Put Option Pricing: Calculate the price of European call and put options based on the Black-Scholes formula.
Implied Volatility Calculation: Estimate the implied volatility based on the market price of an option.
Probability of Expiring In-the-Money: Calculate the probability of a call or put option expiring in-the-money.
Black-Scholes Formulas
For a European call option on a non-dividend-paying stock, the Black-Scholes formula is:

𝐶
=
𝑆
⋅
𝑁
(
𝑑
1
)
−
𝐾
⋅
𝑒
−
𝑟
𝑇
⋅
𝑁
(
𝑑
2
)
C=S⋅N(d 
1
​
 )−K⋅e 
−rT
 ⋅N(d 
2
​
 )
For a European put option:

𝑃
=
𝐾
⋅
𝑒
−
𝑟
𝑇
⋅
𝑁
(
−
𝑑
2
)
−
𝑆
⋅
𝑁
(
−
𝑑
1
)
P=K⋅e 
−rT
 ⋅N(−d 
2
​
 )−S⋅N(−d 
1
​
 )
where:

𝐶
C: Call option price
𝑃
P: Put option price
𝑆
S: Current stock price
𝐾
K: Strike price of the option
𝑇
T: Time to expiration (in years)
𝑟
r: Risk-free interest rate
𝜎
σ: Volatility (standard deviation) of the stock price
𝑁
(
𝑑
)
N(d): Cumulative distribution function of the standard normal distribution
Intermediate Calculations for 
𝑑
1
d 
1
​
  and 
𝑑
2
d 
2
​
 
The values 
𝑑
1
d 
1
​
  and 
𝑑
2
d 
2
​
  are given by:

𝑑
1
=
ln
⁡
(
𝑆
/
𝐾
)
+
(
𝑟
+
𝜎
2
/
2
)
⋅
𝑇
𝜎
𝑇
d 
1
​
 = 
σ 
T
​
 
ln(S/K)+(r+σ 
2
 /2)⋅T
​
 
𝑑
2
=
𝑑
1
−
𝜎
𝑇
d 
2
​
 =d 
1
​
 −σ 
T
​
 
These terms 
𝑑
1
d 
1
​
  and 
𝑑
2
d 
2
​
  represent the standardized values of the underlying asset’s expected return, adjusted for time and volatility.

Methods
The following methods are provided in the BlackScholes class:

call_price(S, K, T, r, sigma): Calculate the price of a call option.
put_price(S, K, T, r, sigma): Calculate the price of a put option.
call_in_the_money(S, K, T, r, sigma): Calculate the probability that a call option will be in-the-money at expiration.
put_in_the_money(S, K, T, r, sigma): Calculate the probability that a put option will be in-the-money at expiration.
call_implied_volatility(price, S, K, T, r): Estimate implied volatility for a call option given its market price.
put_implied_volatility(price, S, K, T, r): Estimate implied volatility for a put option given its market price.
Usage
This code can be used to price European call and put options and to gain insights into the behavior of options in various market conditions
