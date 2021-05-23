/*RELEASE x64*/
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include<random>
#include<chrono>

#include <openssl/sha.h>
#include <openssl/ripemd.h>
#include <secp256k1.h>

#define CPPHTTPLIB_OPENSSL_SUPPORT
#include<httplib.h>

using namespace std;


typedef unsigned char byte;

static secp256k1_context* ctx = secp256k1_context_create(
    SECP256K1_CONTEXT_SIGN | SECP256K1_CONTEXT_VERIFY);

httplib::SSLClient cli("blockchain.info");


//Conversion to base58
char* base58(byte* s, int s_size, char* out, int out_size)
{
    static const char* base_chars = "123456789"
        "ABCDEFGHJKLMNPQRSTUVWXYZ"
        "abcdefghijkmnopqrstuvwxyz";

    byte* s_cp = new byte[s_size];
    memcpy(s_cp, s, s_size);

    int c, i, n;

    out[n = out_size] = 0;
    while (n--) {
        for (c = i = 0; i < s_size; i++) {
            c = c * 256 + s_cp[i];
            s_cp[i] = c / 58;
            c %= 58;
        }
        out[n] = base_chars[c];
    }
    delete[] s_cp;
    return out;
}

//Generate private key
byte* generate_private_key(byte* out)
{
    random_device rd;
    mt19937::result_type seed = rd() ^ (
        (mt19937::result_type)
        chrono::duration_cast<chrono::seconds>(
            chrono::system_clock::now().time_since_epoch()
            ).count() +
        (mt19937::result_type)
        chrono::duration_cast<chrono::microseconds>(
            chrono::high_resolution_clock::now().time_since_epoch()
            ).count());

    mt19937 gen(seed);
    uniform_int_distribution<unsigned> distrib(0, 255);

    do
    {
        for (int i = 0; i < 32; i++)
        {
            out[i] = (unsigned char)distrib(gen);
        }
    } while (!secp256k1_ec_seckey_verify(ctx, out));

    return out;
}

//Convert byte array to string
string tostr(byte* arr, int size)
{
    stringstream ss;
    for (int i = 0; i < size; i++)
    {
        ss << hex << setw(2) << setfill('0') << (int)arr[i];
    }
    return ss.str();
}

//Checking the address
void check_address(string address)
{
    string request = "/address/?format=json";
    request.insert(9, address);

    cout << "Checking address \"" + address + "\"...";

    auto res = cli.Get(request.c_str());


    if (res->status == 200)
    {
        cout << "\n\nThe address is valid. Info: \n";
        cout << res->body;
    }
    else cout << "\n\nThe address is invalid";
}


int main()
{
    byte privatekey[32];

    secp256k1_pubkey publickey;
    size_t publickey_len = 65;
    byte publickey_ser[65];

    byte address_byte[5 + RIPEMD160_DIGEST_LENGTH];

    char address[35];

    // Count the number of addresses generated in 1 minute
    cout << "Generating addresses...";

    int count = 0;
    auto t0 = chrono::system_clock::now();
    while ((chrono::system_clock::now() - t0) < chrono::seconds{ 2 })
    {
        generate_private_key(privatekey);

        secp256k1_ec_pubkey_create(ctx, &publickey, privatekey);
        secp256k1_ec_pubkey_serialize(ctx, publickey_ser, &publickey_len, &publickey, SECP256K1_EC_UNCOMPRESSED);

        address_byte[0] = 0;
        RIPEMD160(SHA256(publickey_ser, publickey_len, 0), publickey_len, address_byte + 1);

        memcpy(
            address_byte + 21,
            SHA256(SHA256(address_byte, 21, 0), SHA256_DIGEST_LENGTH, 0), //Checksum
            4
        );

        base58(address_byte, 25, address, 34);
        address[34] = '\0';

        count++;
    }

    cout << "\nTotal addresses in 1 min: " << count;

    cout << "\n\n--------Last generated--------" << endl;
    cout << "\nPrivate key: " << tostr(privatekey, 32);
    cout << "\nPublic key uncompressed: " << tostr(publickey_ser, 65);
    cout << "\nAddress: " << address;

    //Check the address
    cout << "\n\n--------Checking the address--------\n\n";

    check_address(address);

}
