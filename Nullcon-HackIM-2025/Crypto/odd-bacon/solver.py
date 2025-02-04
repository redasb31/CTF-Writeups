from pwn import *
from Crypto.Util.number import long_to_bytes
from speck import SpeckCipher


def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

S = SpeckCipher(0x0123456789abcdef, key_size = 64, block_size = 32)

def F(block : bytes):
	return S.encrypt(int.from_bytes(block, byteorder = 'big')).to_bytes(4, byteorder = 'big')

def unF(block : bytes):
    return S.decrypt(int.from_bytes(block, byteorder = 'big')).to_bytes(4, byteorder = 'big')

def encrypt(msg : bytes):
	msg += b'0' * ((4 - (len(msg) % 4)) % 4)
	return (b''.join( F((msg[4*i:4*i+4])) for i in range(len(msg) // 4)))

def decrypt(enc : bytes, k1 : bytes, k2 : bytes):
	return (b''.join(xor(k1, unF(xor(enc[4*i:4*i+4], k2))) for i in range(len(enc) // 4)))

# io = process(['python', 'chall.py'])
io = remote('52.59.124.14',5033)

flag = bytes.fromhex(io.recvline().strip().decode())   

results = {}
for i in range(2**10):
    k = long_to_bytes(i, 4)
    print(f"Encryption of {k.hex()} | {i+1}/1024")
    io.recvuntil('> ')
    io.sendline(k.hex().encode())
    res = bytes.fromhex(io.recvline().strip().decode()[-8:])
    results[i] = res

xors = {}
for k1 in results:
    k2 = k1^1
    key = f'{k1}-{k2}'
    if f'{k1}-{k2}' in results or f'{k2}-{k1}' in xors:
        continue
    val1 = results[k1]
    val2 = results[k2]
    val = xor(val1, val2)
    xors[key] = val

L = list(xors.values())

for i in range(2**22):
    if i%2**20==0:
         print(i)
    val = i*2**10
    val2 = val ^ 1
    enc1 = F(long_to_bytes(val, 4))
    enc2 = F(long_to_bytes(val2, 4))
    X = xor((enc1), (enc2))
    if X in L:
        ind = L.index(X)
        break

print('###')

pair = list(xors.keys())[ind]
v1, v2 = map(int, pair.split('-'))
k1 = xor(long_to_bytes(v1, 4) , long_to_bytes(val, 4))
k2 = xor(encrypt(k1),results[0])

try:
    print("FLAG : ",decrypt(flag, k1, k2).decode())
    exit()
except:
    pass

# swap v1 and v2
v2, v1 = map(int, pair.split('-'))
k1 = xor(long_to_bytes(v1, 4) , long_to_bytes(val, 4))
k2 = xor(encrypt(k1),results[0])
print("FLAG : ",decrypt(flag, k1, k2))