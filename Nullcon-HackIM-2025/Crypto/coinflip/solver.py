from pwn import *
from math import gcd

GOAL = 1000000000
coin = ['head','tails']

while True:
    try:
        io = remote('52.59.124.14',5032 )
        N = 64
        balance = 2
        s = []
        for k in range(4):
            res = []
            for i in range(64):
                io.recvuntil(b')')
                io.sendline(b'1')
                io.recvuntil(b'?')
                io.sendline(b'head')
                io.recvline()
                data = io.recvline().decode().strip()
                if 'you lose' in data:
                    res.append('1')
                    balance -= 1
                elif 'you win' in data:
                    res.append('0')
                    balance += 1
                else:
                    raise ValueError(';(')
                print(f'balance = {balance}')

            state = int(''.join(res),2)
            print(f'Recovered state: {state}')
            s.append(state)

        d1 = s[2] * s[0]**3 - s[1]**4
        d2 = s[3] * s[1]**3 - s[2]**4

        m = gcd(d1,d2)
        a = (s[1]*pow(s[0],-3,m))%m

        state = a * pow(s[-1], 3, m) % m
        state = [int(bit) for bit in bin(state)[2:].zfill(N)]

        for i in range(round(math.log2(GOAL))):
            value = str(2**i).encode()
            io.recvuntil(b')')
            io.sendline(value)
            io.recvuntil(b'?')
            io.sendline(coin[state[i]].encode())
            io.recvline()
            print(f'Round {i}: {coin[state[i]]}')
            data = io.recvline().decode().strip()

        io.interactive()
    except KeyboardInterrupt:
        io.close()
        exit()
    except:
        print('We lost, Trying again!')
        io.close()
        continue
        
