# **Cubic Random Generator (CRG) Writeup**
**Category**: Cryptography  
**Points**: 212  
**Solves**: 41  
**Author**: ENOFLAG   

---

## Challenge Overview
`Dr. Evil wants to play a game and he demands one million billion shitcoins for the flag.`  
We're presented with a betting game that uses a cubic congruential generator for randomness. The PRNG follows the recurrence:
```python
s_{i+1} = a * s_i³ mod m
```
Our goal is to recover the secret parameters `a` and `m` to predict future outputs and win bets.

---


## Challenge Files
- **[`chall.py`](chall.py)** (Challenge code)  
- **[`solver.py`](solver.py)** (Solution script)

---


## Key Vulnerabilities
1. **Leakable State**: Each "coin flip" reveals 1 bit of the 64-bit state
2. **Algebraic Relationship**: Consecutive states have a mathematical relationship modulo `m`

---

## Attack Strategy
### **Step 1: Leak 4 Consecutive States**
By making 256 bets (4 states × 64 bits each), we observe outcomes to reconstruct:
```
s₀, s₁, s₂, s₃
```
Each state is recovered by:
1. Betting "head" 64 times to get 64 bits
2. Converting win/lose results to binary state

---

### **Step 2: Derive Mathematical Relationships**
From the recurrence relation:
```
s₁ ≡ a·s₀³ mod m  
s₂ ≡ a·s₁³ mod m  
s₃ ≡ a·s₂³ mod m
```

**Key Insight**: Eliminate `a` by combining equations:
```
s₁ ≡ a·s₀³ mod m ⇒ a ≡ s₁/s₀³ mod m  
s₂ ≡ (s₁/s₀³)·s₁³ ≡ s₁⁴/s₀³ mod m ⇒ s₀³s₂ ≡ s₁⁴ mod m
```

This gives us:
```
d₀ = s₀³s₂ - s₁⁴ ≡ 0 mod m  
d₁ = s₁³s₃ - s₂⁴ ≡ 0 mod m
```

---

### **Step 3: Recover Modulus m**
Since both differences are multiples of `m`:
```python
m = gcd(d₀, d₁)
```

---

### **Step 4: Recover Multiplier a**
Using the first state transition:
```python
a ≡ s₁·s₀^{-3} mod m
```

---

### **Step 5: Predict Future States**
With `a` and `m` known, we can compute:
```
s₄ = a·s₃³ mod m  
s₅ = a·s₄³ mod m  
...
```
Convert each state to 64-bit binary for predicting future coin flips.

---

## Exploit Code Breakdown
The solver:
1. Leaks 4 states through controlled bets
2. Computes `m = gcd(d₀, d₁)`
3. Calculates `a = s₁·s₀^{-3} mod m`
4. Predicts future states using the CRG formula
5. Makes exponential bets to quickly reach 1B balance

---

## Flag
`ENO{1nfin1t3_r1che5_3re_y0ur5_1t_s33m5}`
