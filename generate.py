import time
import hashlib
import ecdsa
from binascii import hexlify
from base58 import b58encode


start_time = time.time()
# ecdsa - Elliptic Curve Digital Signature Algorithm
private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
# set of parameters named as SECP256k1
public_key = b'\04' + private_key.get_verifying_key().to_string()

ripemd160 = hashlib.new('ripemd160')
ripemd160.update(hashlib.sha256(public_key).digest())
r = b'\0' + ripemd160.digest()

checksum = hashlib.sha256(hashlib.sha256(r).digest()).digest()[0:4]
address = b58encode(r + checksum)

print(f'private key: {hexlify(private_key.to_string())}')
print(f'public key uncompressed: {hexlify(public_key)}')
print(f'btc address: {address}')

print("--- %s seconds ---" % (time.time() - start_time))
