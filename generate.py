import os
import time
import hashlib
import ecdsa
from binascii import hexlify
from base58 import b58encode
import re
from urllib.request import urlopen


def check_balance(address):
    # Add time different of 0 if you need more security on the checks
    WARN_WAIT_TIME = 0

    blockchain_tags_json = [
        'total_received',
        'final_balance',
    ]

    SATOSHIS_PER_BTC = 1e+8

    check_address = address

    parse_address_structure = re.match(r' *([a-zA-Z1-9]{1,34})', check_address)
    if (parse_address_structure is not None or len(address) > 34):
        check_address = parse_address_structure.group(1)
    else:
        print("\nThis Bitcoin Address is invalid" + check_address)
        exit(1)

    # Read info from Blockchain about the Address
    reading_state = 1
    while (reading_state):
        try:
            htmlfile = urlopen("https://blockchain.info/address/%s?format=json" % check_address, timeout=10)
            htmltext = htmlfile.read().decode('utf-8')
            reading_state = 0
        except:
            reading_state += 1
            print("Checking... " + str(reading_state))

    blockchain_info_array = []
    tag = ''
    try:
        for tag in blockchain_tags_json:
            blockchain_info_array.append(
                float(re.search(r'%s":(\d+),' % tag, htmltext).group(1)))
    except:
        print("Error '%s'." % tag);
        exit(1)

    for i, btc_tokens in enumerate(blockchain_info_array):
        if (blockchain_tags_json[i] == 'final_balance'):
            return btc_tokens / SATOSHIS_PER_BTC


def random_secret_exponent(curve_order):
    while True:
        bytes = os.urandom(32)
        random_hex = hexlify(bytes)
        random_int = int(random_hex, 16)
        if random_int >= 1 and random_int < curve_order:
            return random_int


def generate_private_key():
    curve = ecdsa.curves.SECP256k1
    se = random_secret_exponent(curve.order)
    from_secret_exponent = ecdsa.keys.SigningKey.from_secret_exponent
    return from_secret_exponent(se, curve, hashlib.sha256)

# 1. Generating private key using ECDSA with curve SECP256k1 (should be described more)
# 2. Getting public key from private
# 3. Calculation control sum to check for any mistakes
# 4. Getting address
start_time = time.time()

for _ in range(20):
    # ecdsa - Elliptic Curve Digital Signature Algorithm
    # private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    private_key = generate_private_key()
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
    print(check_balance(address.decode("utf-8")))

print("--- %s seconds ---" % (time.time() - start_time))
