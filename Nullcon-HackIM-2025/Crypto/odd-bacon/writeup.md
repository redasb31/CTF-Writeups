# **odd-bacon** Writeup  
**Category**: Cryptography  
**Points**: 442  
**Solves**: 19  
**Author**: ENOFLAG  

---

## Challenge Description
`There is something wrong with the author. He uses a cipher that is essentially called "bacon", he uses a publicly known key and then he claims that there even is a security proof for this kind of cipher.`  

- We’re given a custom encryption scheme using the Speck cipher. The server encrypts the flag with two unknown 4-byte keys (`k1` and `k2`), and allows us to encrypt 1024 chosen plaintexts. Our goal is to recover the keys and decrypt the flag.

---

## Challenge Files
- **[`chall.py`](chall.py)** (Challenge code)  
- **[`solver.py`](solver.py)** (Solution script)

---

## Encryption Overview
The encryption process works as follows:  
1. **Block Processing**: Split into 4-byte blocks.  
2. **Encryption Steps**:  
   - XOR the block with `k1`.  
   - Encrypt the result with a **fixed-key Speck cipher** (function `F`).  
   - XOR the output of `F` with `k2`.  
3. **Output**: Concatenate all processed blocks.

```python
def F(block : bytes):
    # Fixed-key Speck encryption (key = 0x0123456789abcdef)
    return SpeckCipher(0x0123456789abcdef, key_size=64, block_size=32).encrypt(...)

def encrypt(msg : bytes, k1 : bytes, k2 : bytes):
    msg += b'0' * ((4 - (len(msg) % 4)) % 4)
    return b''.join(xor(k2, F(xor(msg[4*i:4*i+4], k1))) for i in range(len(msg) // 4))
```

---

## Attack Strategy
### **Step 1: Collect Ciphertexts**
We send 1024 chosen plaintexts of the form `i` (where `i` ranges from `0` to `1023`) and store their ciphertexts:  
```python
for i in range(2**10):
    k = long_to_bytes(i, 4)
    io.sendline(k.hex())
    res = bytes.fromhex(io.recvline().strip().decode()[-8:])
    results[i] = res
```

### **Step 2: Exploit XOR Relationships**
For pairs of plaintexts `(p1, p2)` where `p2 = p1 ⊕ 1`, compute the XOR of their ciphertexts:  
```python
xors[key] = xor(results[k1], results[k2])
```

This cancels out `k2`, leaving:  
```
c1 ⊕ c2 = F(p1 ⊕ k1) ⊕ F(p1 ⊕ 1 ⊕ k1) 
```

### **Step 3: Brute-Force `k1`**
We brute-force the higher 22 bits of `k1` (since 2^22 is feasible):  
```python
for i in range(2**22):
    val = i * 2**10  
    val2 = val ^ 1
    # Compute expected XOR of F(val) and F(val2)
    X = xor(F(long_to_bytes(val, 4)), F(long_to_bytes(val2, 4)))
    if X in L:  # Check against collected XORs
        break
```

### **Step 4: Recover `k1` and `k2`**
Once a collision is found:  
1. Derive `k1` using the colliding plaintext pair.  
2. Compute `k2` using `k1` and a known ciphertext:  
   ```python
   k1 = xor(plaintext, val)
   k2 = xor(encrypt(k1), results[0])
   ```

### **Step 5: Decrypt the Flag**
Decrypt the encrypted flag with the recovered keys:  
```python
def decrypt(enc : bytes, k1 : bytes, k2 : bytes):
    return b''.join(xor(k1, unF(xor(block, k2))) for block in blocks)
```

---

## Flag
`ENO{3ven_m3ns0ur_re3l1y_1s_s3cur3_f0r_4_PRF}`  

---

## Assets
- **[`chall.py`](chall.py)**: Original challenge code.  
- **[`solver.py`](solver.py)**: Full solve script. 
- **[`speck.py`](speck.py)**: Speck cipher implementation.
