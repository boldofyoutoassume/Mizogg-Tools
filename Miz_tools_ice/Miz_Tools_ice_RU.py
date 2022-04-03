# -*- coding: utf-8 -*-
'''
Сделано Mizogg Tools для помощи в поиске биткойнов. Удачи и счастливой охоты Miz_Tools_ice_RU.py Версия 6 
31 Bitcoin ATH and Doge Tools
Using iceland2k14 secp256k1 https://github.com/iceland2k14/secp256k1  fastest Python Libary

https://mizogg.co.uk
'''
import requests, codecs, hashlib, ecdsa, bip32utils, binascii, sys, time, random, itertools, csv
import secp256k1 as ice
from mnemonic import Mnemonic
from bit import *
from bit.format import bytes_to_wif
from urllib.request import urlopen
from time import sleep
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from hdwallet import HDWallet
from typing import Optional
from hdwallet.symbols import ETH as SYMBOL

n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def get_balance(addr):
    contents = requests.get('https://sochain.com/api/v2/get_address_balance/BTC/' + addr, timeout=10)
    res = contents.json()
    response = (contents.content)
    balance = dict(res['data'])['confirmed_balance']
    return balance

def data_info():
    blocs=requests.get("https://blockchain.info/rawaddr/"+addr)
    ress = blocs.json()
    hash160 = dict(ress)["hash160"]
    address = dict(ress)["address"]
    n_tx = dict(ress)["n_tx"]
    total_received = dict(ress)["total_received"]
    total_sent = dict(ress)["total_sent"]
    final_balance = dict(ress)["final_balance"]
    txs = dict(ress)["txs"]
    data.append({
        'hash160': hash160,
        'address': address,
        'n_tx': n_tx,
        'total_received': total_received,
        'total_sent': total_sent,
        'final_balance': final_balance,
        'txs': txs,
    })

def get_doge(daddr):
    Dogecoin = requests.get("https://dogechain.info/api/v1/address/balance/"+ daddr)
    resedoge = Dogecoin.json()
    BalanceDoge = dict(resedoge)['balance']
    return BalanceDoge

class BrainWallet:

    @staticmethod
    def generate_address_from_passphrase(passphrase):
        private_key = str(hashlib.sha256(
            passphrase.encode('utf-8')).hexdigest())
        address =  BrainWallet.generate_address_from_private_key(private_key)
        return private_key, address

    @staticmethod
    def generate_address_from_private_key(private_key):
        public_key = BrainWallet.__private_to_public(private_key)
        address = BrainWallet.__public_to_address(public_key)
        return address

    @staticmethod
    def __private_to_public(private_key):
        private_key_bytes = codecs.decode(private_key, 'hex')
        # Get ECDSA public key
        key = ecdsa.SigningKey.from_string(
            private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
        key_bytes = key.to_string()
        key_hex = codecs.encode(key_bytes, 'hex')
        # Add bitcoin byte
        bitcoin_byte = b'04'
        public_key = bitcoin_byte + key_hex
        return public_key

    @staticmethod
    def __public_to_address(public_key):
        public_key_bytes = codecs.decode(public_key, 'hex')
        # Run SHA256 for the public key
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        # Run ripemd160 for the SHA256
        ripemd160_bpk = hashlib.new('ripemd160')
        ripemd160_bpk.update(sha256_bpk_digest)
        ripemd160_bpk_digest = ripemd160_bpk.digest()
        ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
        # Add network byte
        network_byte = b'00'
        network_bitcoin_public_key = network_byte + ripemd160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(
            network_bitcoin_public_key, 'hex')
        # Double SHA256 to get checksum
        sha256_nbpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_nbpk_digest = sha256_nbpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_nbpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_2_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
        checksum = sha256_2_hex[:8]
        # Concatenate public key and checksum to get the address
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
        wallet = BrainWallet.base58(address_hex)
        return wallet

    @staticmethod
    def base58(address_hex):
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        b58_string = ''
        # Get the number of leading zeros and convert hex to decimal
        leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
        # Convert hex to decimal
        address_int = int(address_hex, 16)
        # Append digits to the start of string
        while address_int > 0:
            digit = address_int % 58
            digit_char = alphabet[digit]
            b58_string = digit_char + b58_string
            address_int //= 58
        # Add '1' for each 2 leading zeros
        ones = leading_zeros // 2
        for one in range(ones):
            b58_string = '1' + b58_string
        return b58_string

def data_wallet():
    for child in range(0,20):
        bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
        bip32_child_key_obj = bip32_root_key_obj.ChildKey(
            44 + bip32utils.BIP32_HARDEN
        ).ChildKey(
            0 + bip32utils.BIP32_HARDEN
        ).ChildKey(
            0 + bip32utils.BIP32_HARDEN
        ).ChildKey(0).ChildKey(child)
        data.append({
                'bip32_root_key': bip32_root_key_obj.ExtendedKey(),
                'bip32_extended_private_key': bip32_child_key_obj.ExtendedKey(),
                'path': f"m/44'/0'/0'/0/{child}",
                'address': bip32_child_key_obj.Address(),
                'publickey': binascii.hexlify(bip32_child_key_obj.PublicKey()).decode(),
                'privatekey': bip32_child_key_obj.WalletImportFormat(),
            })
            
def data_eth():
    for address_index in range(divs):
        bip44_derivation: BIP44Derivation = BIP44Derivation(
            cryptocurrency=EthereumMainnet, account=0, change=False, address=address_index
        )
        bip44_hdwallet.from_path(path=bip44_derivation)
        data.append({
                'path': bip44_hdwallet.path(),
                'address': bip44_hdwallet.address(),
                'privatekey': bip44_hdwallet.private_key(),
                'privatedec': int(bip44_hdwallet.private_key(), 16),
            })
        bip44_hdwallet.clean_derivation()            
            
"""
@author: iceland
"""

def get_rs(sig):
    rlen = int(sig[2:4], 16)
    r = sig[4:4+rlen*2]
#    slen = int(sig[6+rlen*2:8+rlen*2], 16)
    s = sig[8+rlen*2:]
    return r, s
    
def split_sig_pieces(script):
    sigLen = int(script[2:4], 16)
    sig = script[2+2:2+sigLen*2]
    r, s = get_rs(sig[4:])
    pubLen = int(script[4+sigLen*2:4+sigLen*2+2], 16)
    pub = script[4+sigLen*2+2:]
    assert(len(pub) == pubLen*2)
    return r, s, pub


# Returns list of this list [first, sig, pub, rest] for each input
def parseTx(txn):
    if len(txn) <130:
        print('[WARNING] rawtx most likely incorrect. Please check..')
        sys.exit(1)
    inp_list = []
    ver = txn[:8]
    if txn[8:12] == '0001':
        print('UnSupported Tx Input. Presence of Witness Data')
        sys.exit(1)
    inp_nu = int(txn[8:10], 16)
    
    first = txn[0:10]
    cur = 10
    for m in range(inp_nu):
        prv_out = txn[cur:cur+64]
        var0 = txn[cur+64:cur+64+8]
        cur = cur+64+8
        scriptLen = int(txn[cur:cur+2], 16)
        script = txn[cur:2+cur+2*scriptLen] #8b included
        r, s, pub = split_sig_pieces(script)
        seq = txn[2+cur+2*scriptLen:10+cur+2*scriptLen]
        inp_list.append([prv_out, var0, r, s, pub, seq])
        cur = 10+cur+2*scriptLen
    rest = txn[cur:]
    return [first, inp_list, rest]

#==============================================================================
def get_rawtx_from_blockchain(txid):
    try:
        htmlfile = urlopen("https://blockchain.info/rawtx/%s?format=hex" % txid, timeout = 20)
    except:
        print('Unable to connect internet to fetch RawTx. Exiting..')
        sys.exit(1)
    else: res = htmlfile.read().decode('utf-8')
    return res
# =============================================================================

def getSignableTxn(parsed):
    res = []
    first, inp_list, rest = parsed
    tot = len(inp_list)
    time.sleep(10)
    for one in range(tot):
        e = first
        for i in range(tot):
            e += inp_list[i][0] # prev_txid
            e += inp_list[i][1] # var0
            if one == i: 
                e += '1976a914' + HASH160(inp_list[one][4]) + '88ac'
            else:
                e += '00'
            e += inp_list[i][5] # seq
        e += rest + "01000000"
        z = hashlib.sha256(hashlib.sha256(bytes.fromhex(e)).digest()).hexdigest()
        res.append([inp_list[one][2], inp_list[one][3], z, inp_list[one][4], e])
    return res
#==============================================================================
def HASH160(pubk_hex):
    return hashlib.new('ripemd160', hashlib.sha256(bytes.fromhex(pubk_hex)).digest() ).hexdigest()

def SEQ_wallet():
    for i in range(0,rangediv):
        percent = div * i
        ran= start+percent
        seed = str(ran)
        HEX = "%064x" % ran
        wifc = ice.btc_pvk_to_wif(HEX)
        wifu = ice.btc_pvk_to_wif(HEX, False)
        caddr = ice.privatekey_to_address(0, True, int(seed)) #Compressed
        uaddr = ice.privatekey_to_address(0, False, int(seed))  #Uncompressed
        p2sh = ice.privatekey_to_address(1, True, int(seed)) #p2sh
        bech32 = ice.privatekey_to_address(2, True, int(seed))  #bech32
        data.append({
            'seed': seed,
            'HEX': HEX,
            'wifc': wifc,
            'wifu': wifu,
            'caddr': caddr,
            'uaddr': uaddr,
            'p2sh': p2sh,
            'bech32': bech32,
            'percent': f"Hex scan Percent {i}%",
        })

def divsion_wallet():
    for i in range(0,rangediv):
        percent = div * i
        ran= start+percent
        seed = str(ran)
        HEX = "%064x" % ran
        divsion.append({
            'seed': seed,
            'HEX': HEX,
            'percent': f"{i}%",
        })
def iter_all(count):
    if count == 0:
        yield start
    else:
        for a in alphabet:
            if count == a:
                continue
            else:
                for scan in iter_all(count-1):
                    yield scan + a

def hash160pub(hex_str):
    sha = hashlib.sha256()
    rip = hashlib.new('ripemd160')
    sha.update(hex_str)
    rip.update( sha.digest() )
    print ( "key_hash = \t" + rip.hexdigest() )
    return rip.hexdigest()
    
prompt= '''
    ************************ Главное меню Mizogg's Tools ********************************************
    *                       Инструменты одиночной проверки                                          *
    *  Вариант 1. Биткойн-адрес с проверкой баланса                                 =  1            *
    *  Вариант 2. Биткойн-адрес на HASH160                                          =  2            *
    *  Вариант 3. HASH160 на биткойн-адрес (не работает)                            =  3            *
    *  Вариант 4. Мозговой кошелек Биткойн с проверкой баланса                      =  4            *
    *  Вариант 5. Шестнадцатеричный код в десятичный (HEX 2 DEC)                    =  5            *
    *  Вариант 6. Десятичный в шестнадцатеричный (DEC 2 HEX)                        =  6            *
    *  Вариант 7. Шестнадцатеричный адрес в биткойн с проверкой баланса Dogecoin    =  7            *
    *  Вариант 8. Десятичный адрес в биткойн с проверкой баланса       Dogecoin     =  8            *
    *  Вариант 9. Мнемонические слова для биткойн-адреса с проверкой баланса        =  9            *
    *  Вариант 10.WIF на биткойн-адрес с проверкой баланса                          =  10           *
    *  Вариант 11.Получить подпись ECDSA R, S, Z с помощью инструмента rawtx или txid = 11          *
    *  Вариант 12.Разделение диапазона IN HEX или DEC инструмент                   =  12            *
    *                                                                                               *
    *                    Генераторы и мультипроверочные инструменты                                 *
    *  Вариант 13. Биткойн-адреса из файла с проверкой баланса                      = 13            *
    *  Вариант 14. Биткойн-адреса из файла в файл HASH160                           = 14            *
    *  Вариант 15. Список Brain Wallet из файла с проверкой баланса                 = 15            *
    *  Вариант 16. Генератор мнемонических слов, случайный выбор [офлайн]           = 16            *
    *  Вариант 17. Случайное сканирование биткойнов в случайном порядке в диапазоне = 17            *
    *  Вариант 18. Последовательность биткойнов сканируется последовательно в диапазоне деления= 18 *
    *  Вариант 19. Биткойн случайная обратная позиция K                             = 19            *
    *  Вариант 20. Последовательность биткойнов, обратная K позиция                 = 20            *
    *  Вариант 21. Биткойн WIF Recovery или WIF Checker 5 K L                       = 21            *
    *  Вариант 22. Биткойн-адреса из файла в открытый ключ                          = 22            *
    *    Option 23.Public Key from file to Bitcoin Addresses(NOTWORKING)= 23                        *
    *                                                                                               *
    *                 ETH Generators & Multi Check Tools                                            *
    *    Option 24.ETH Address with TXS Check         [Internet required]= 24                       *
    *    Option 25.Hexadecimal to Decimal (HEX 2 DEC) [Internet required]= 25                       *
    *    Option 26.Decimal to Hexadecimal (DEC 2 HEX) [Internet required]= 26                       *
    *    Option 27.Mnemonic Words to dec and hex      [Internet required]= 27                       *
    *    Option 28.Mnemonic Words Generator Random Choice [Offline]      = 28                       *
    *    Option 29.Mnemonic Words Generator Random Choice [ONLINE]       = 29                       *
    *                                                                                               *
    *                   Extras Miscellaneous Tools                                                  *
    *    Option 30.Doge Coin sequential Scan Balance Check [ONLINE]      = 30                       *
    *    Option 31.Doge Coin Random Scan Balance Check [ONLINE]          = 31                       *
    *                                                                                               *
    ************ Главное меню Mizogg's Tools Using iceland2k14 secp256k1 ****************************

Введите свой выбор здесь Enter 1-31 : 
'''


mylistapi = []
while True:
    data = []
    mylist = []
    count=0
    skip = 0
    ammount = 0.00000000
    total= 0
    iteration = 0
    start_time = time.time()
    api1="?apiKey=freekey"
    api2="?apiKey=freekey"
    api3="?apiKey=freekey"
    #api4="?apiKey=freekey"
    mylistapi=[str(api1), str(api2), str(api3)]
    #mylistapi=[str(api1), str(api2), str(api3), str(api4)]
    apikeys=random.choice(mylistapi)
    start=int(input(prompt))
    if start == 1:
        print ('Инструмент проверки баланса адреса')
        addr = str(input('Введите здесь свой биткойн-адрес : '))
        print ('\nBitcoin Address = ', addr, '    Balance So Chain = ', get_balance(addr), ' BTC')
        data_info()
        for data_w in data:
            hash160 = data_w['hash160']
            address = data_w['address']
            n_tx = data_w['n_tx']
            total_received = data_w['total_received']
            total_sent = data_w['total_sent']
            final_balance = data_w['final_balance']
            print('================== Block Chain ==================')
            print('Bitcoin address   = ', address)
            print('hash160   = ', hash160)
            print('Number of tx    = ', n_tx)
            print('Total Received  = ', total_received)
            print('Total Sent      = ', total_sent)
            print('Final Balance   = ', final_balance)
            print('================== Block Chain ==================')
            time.sleep(3.0)
    elif start == 2:
        print ('Адрес для инструмента HASH160')
        addr = str(input('Введите здесь свой биткойн-адрес : '))
        if addr.startswith('1'):
            address_hash160 = (ice.address_to_h160(addr))
        if addr.startswith('3'):
            address_hash160 = (ice.address_to_h160(addr))
        if addr.startswith('bc1') and len(addr.split('\t')[0])< 50 :
            address_hash160 = (ice.bech32_address_decode(addr,coin_type=0))
        print ('\nBitcoin Address = ', addr, '\nTo HASH160 = ', address_hash160)
        time.sleep(3.0)
    elif start == 3:
        print ('Инструмент HASH160 для биткойн-адреса')
        hash160 =(str(input('Введите свой HASH160 здесь : ')))
        print ('Скоро не работает')
    elif start == 4:
        print ('Мозговой кошелек Биткойн Адрес Инструмент')    
        passphrase = (input("Введите пароль ЗДЕСЬ : "))
        wallet = BrainWallet()
        private_key, addr = wallet.generate_address_from_passphrase(passphrase)
        print('\nPassphrase     = ',passphrase)
        print('Private Key      = ',private_key)
        print('Bitcoin Address  = ', addr, '    Balance = ', get_balance(addr), ' BTC')
        data_info()
        for data_w in data:
            hash160 = data_w['hash160']
            address = data_w['address']
            n_tx = data_w['n_tx']
            total_received = data_w['total_received']
            total_sent = data_w['total_sent']
            final_balance = data_w['final_balance']
            print('================== Block Chain ==================')
            print('Bitcoin address   = ', address)
            print('hash160   = ', hash160)
            print('Number of tx    = ', n_tx)
            print('Total Received  = ', total_received)
            print('Total Sent      = ', total_sent)
            print('Final Balance   = ', final_balance)
            print('================== Block Chain ==================')
            time.sleep(3.0)
    elif start == 5:
        print('Шестнадцатеричный в десятичный инструмент')
        HEX = str(input('Введите свой шестнадцатеричный HEX здесь : '))
        dec = int(HEX, 16)
        length = len(bin(dec))
        length -=2
        print('\nHexadecimal = ',HEX, '\nTo Decimal = ', dec, '  bits ', length)
        time.sleep(3.0)
    elif start == 6:
        print('Десятичный в шестнадцатеричный инструмент')
        dec = int(input('Введите свой десятичный DEC здесь : '))
        HEX = "%064x" % dec
        length = len(bin(dec))
        length -=2
        print('\nDecimal = ', dec, '  bits ', length, '\nTo Hexadecimal = ', HEX)
        time.sleep(3.0)
    elif start == 7:
        prompthex= '''
    ************************* Hexadecimal to Bitcoin Address Tool ************************* 
    *                                                                                     *
    *    1-Single Hexadecimal to Bitcoin Address. Balance check [Internet required]       *
    *    2-List Multi Hexadecimal to Bitcoin Address. Balance check [Internet required]   *
    *    Type 1-2 to Start    (Option 2 Requires hex.txt file list of Hexadecimal         *
    *                                                                                     *
    ************************* Hexadecimal to Bitcoin Address Tool *************************
        '''
        starthex=int(input(prompthex))
        if starthex == 1:
            print('Инструмент преобразования шестнадцатеричного адреса в биткойн')
            HEX=str(input("Шестнадцатеричный HEX ->  "))
            dec = int(HEX, 16)
            wifc = ice.btc_pvk_to_wif(HEX)
            wifu = ice.btc_pvk_to_wif(HEX, False)
            caddr = ice.privatekey_to_address(0, True, dec) #Compressed
            uaddr = ice.privatekey_to_address(0, False, dec)  #Uncompressed
            p2sh = ice.privatekey_to_address(1, True, dec) #p2sh
            bech32 = ice.privatekey_to_address(2, True, dec)  #bech32
            dogeaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, True, dec) #DOGE
            dogeuaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, False, dec) #DOGE
            query = {caddr}|{uaddr}|{p2sh}|{bech32}
            request = requests.get("https://blockchain.info/multiaddr?active=" + ','.join(query), timeout=10)
            try:
                request = request.json()
                print('PrivateKey (hex) : ', HEX)
                print('PrivateKey (dec) : ', dec)
                print('PrivateKey (wif) Compressed   : ', wifc)
                print('PrivateKey (wif) UnCompressed : ', wifu)
                print('Bitcoin Address Compressed   = ', caddr, '    Balance = ', get_balance(caddr), ' BTC')
                print('Bitcoin Address UnCompressed = ', uaddr, '    Balance = ', get_balance(uaddr), ' BTC')
                print('Bitcoin Address p2sh         = ', p2sh, '    Balance = ', get_balance(p2sh), ' BTC')
                print('Bitcoin Address Bc1  bech32  = ', bech32, '    Balance = ', get_balance(bech32), ' BTC')
                for row in request["addresses"]:
                    print(row)
                print('Dogecoin Address Compressed   = ', dogeaddr, '    Balance = ', get_doge(dogeaddr))
                print('Dogecoin Address UnCompressed = ', dogeuaddr, '    Balance = ', get_doge(dogeuaddr))
                time.sleep(3.0)
            except:
                pass
        if starthex == 2:
            with open("hex.txt", "r") as file:
                line_count = 0
                for line in file:
                    line != "\n"
                    line_count += 1
            with open('hex.txt', newline='', encoding='utf-8') as f:
                for line in f:
                    mylist.append(line.strip())
            for i in range(0,len(mylist)):
                myhex = mylist[i]
                HEX = myhex.split()[0]
                dec = int(HEX, 16)
                wifc = ice.btc_pvk_to_wif(HEX)
                wifu = ice.btc_pvk_to_wif(HEX, False)
                caddr = ice.privatekey_to_address(0, True, dec) #Compressed
                uaddr = ice.privatekey_to_address(0, False, dec)  #Uncompressed
                p2sh = ice.privatekey_to_address(1, True, dec) #p2sh
                bech32 = ice.privatekey_to_address(2, True, dec)  #bech32
                dogeaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, True, dec) #DOGE
                dogeuaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, False, dec) #DOGE
                count+=1
                total+=2
                print('Total HEX addresses Loaded:', line_count)
                if float (get_balance(caddr)) or float (get_balance(uaddr)) or float (get_balance(p2sh)) or float (get_balance(bech32)) or float (get_doge(dogeaddr)) or float (get_doge(dogeuaddr)) > ammount:
                    print('PrivateKey (hex) : ', HEX)
                    print('PrivateKey (dec) : ', dec)
                    print('PrivateKey (wif) Compressed   : ', wifc)
                    print('PrivateKey (wif) UnCompressed : ', wifu)
                    print('Bitcoin Address Compressed   = ', caddr, '    Balance = ', get_balance(caddr), ' BTC')
                    print('Bitcoin Address UnCompressed = ', uaddr, '    Balance = ', get_balance(uaddr), ' BTC')
                    print('Bitcoin Address p2sh         = ', p2sh, '    Balance = ', get_balance(p2sh), ' BTC')
                    print('Bitcoin Address Bc1  bech32  = ', bech32, '    Balance = ', get_balance(bech32), ' BTC')
                    print('Dogecoin Address Compressed   = ', dogeaddr, '    Balance = ', get_doge(dogeaddr))
                    print('Dogecoin Address UnCompressed = ', dogeuaddr, '    Balance = ', get_doge(dogeuaddr))
                    f=open('winner.txt','a')
                    f.write('\nPrivateKey (hex): ' + HEX + '\nBitcoin Address Compressed : ' + caddr + '\nBitcoin Address UnCompressed :' + uaddr + '\nBitcoin Address p2sh : ' + p2sh + '\nBitcoin Address bc1 :' + bech32 + '\nDogecoin Address Compressed : ' + dogeaddr + '\nDogecoin Address UnCompressed :' + dogeuaddr + '\nPrivateKey (wif) Compressed : ' + wifc + '\nPrivateKey (wif) UnCompressed : ' + wifu + '\n==================================')
                    f.close()
                else: 
                    print('Scan Number : ', count, ' : Total Wallets Checked : ', total)
                    print('Bitcoin Address Compressed   = ', caddr, '    Balance = ', get_balance(caddr), ' BTC')
                    print('Bitcoin Address UnCompressed = ', uaddr, '    Balance = ', get_balance(uaddr), ' BTC')
                    print('Bitcoin Address p2sh         = ', p2sh, '    Balance = ', get_balance(p2sh), ' BTC')
                    print('Bitcoin Address Bc1  bech32  = ', bech32, '    Balance = ', get_balance(bech32), ' BTC')
                    print('Dogecoin Address Compressed   = ', dogeaddr, '    Balance = ', get_doge(dogeaddr))
                    print('Dogecoin Address UnCompressed = ', dogeuaddr, '    Balance = ', get_doge(dogeuaddr))
                    time.sleep(1.5)
                    
    elif start == 8:
        print('Инструмент преобразования десятичного адреса в биткойн')
        dec=int(input('Десятичный Dec (Максимум 115792089237316195423570985008687907852837564279074904382605163141518161494336 ) ->  '))
        HEX = "%064x" % dec  
        wifc = ice.btc_pvk_to_wif(HEX)
        wifu = ice.btc_pvk_to_wif(HEX, False)
        caddr = ice.privatekey_to_address(0, True, dec) #Compressed
        uaddr = ice.privatekey_to_address(0, False, dec)  #Uncompressed
        p2sh = ice.privatekey_to_address(1, True, dec) #p2sh
        bech32 = ice.privatekey_to_address(2, True, dec)  #bech32
        dogeaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, True, dec) #DOGE
        dogeuaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, False, dec) #DOGE
        query = {caddr}|{uaddr}|{p2sh}|{bech32}
        request = requests.get("https://blockchain.info/multiaddr?active=" + ','.join(query), timeout=10)
        try:
            request = request.json()
            print('PrivateKey (hex) : ', HEX)
            print('PrivateKey (dec) : ', dec)
            print('PrivateKey (wif) Compressed   : ', wifc)
            print('PrivateKey (wif) UnCompressed : ', wifu)
            print('Bitcoin Address Compressed   = ', caddr, '    Balance = ', get_balance(caddr), ' BTC')
            print('Bitcoin Address UnCompressed = ', uaddr, '    Balance = ', get_balance(uaddr), ' BTC')
            print('Bitcoin Address p2sh         = ', p2sh, '    Balance = ', get_balance(p2sh), ' BTC')
            print('Bitcoin Address Bc1  bech32  = ', bech32, '    Balance = ', get_balance(bech32), ' BTC')
            for row in request["addresses"]:
                print(row)
            print('Dogecoin Address Compressed   = ', dogeaddr, '    Balance = ', get_doge(dogeaddr))
            print('Dogecoin Address UnCompressed = ', dogeuaddr, '    Balance = ', get_doge(dogeuaddr))
            time.sleep(3.0)
        except:
            pass
    elif start == 9:
        promptword= '''
    ************************* Mnemonic Words 12/15/18/21/24 tool ************************* 
    *                                                                                    *
    *    1-OWN Words to Bitcoin with Balance Check [Internet required]                   *
    *    2-Generated Words to Bitcoin with Balance Check [Internet required]             *
    *    Type 1-2 to Start                                                               *
    *                                                                                    *
    ************************* Mnemonic Words 12/15/18/21/24 tool *************************
        '''
        startwords=int(input(promptword))
        if startwords == 1:
            print('Mnemonic 12/15/18/21/24 Words to Bitcoin Address Tool')
            wordlist = str(input('Enter Your Mnemonic Words = '))
            Lang = int(input(' Choose language 1.english, 2.french, 3.italian, 4.spanish, 5.chinese_simplified, 6.chinese_traditional, 7.japanese or 8.korean '))
            if Lang == 1:
                Lang1 = "english"
            elif Lang == 2:
                Lang1 = "french"
            elif Lang == 3:
                Lang1 = "italian"
            elif Lang == 4:
                Lang1 = "spanish"
            elif Lang == 5:
                Lang1 = "chinese_simplified"
            elif Lang == 6:
                Lang1 = "chinese_traditional"
            elif Lang == 7:
                Lang1 = "japanese"
            elif Lang == 8:
                Lang1 = "korean"
            else:
                print("WRONG NUMBER!!! Starting with english")
                Lang1 = "english"
            mnemo = Mnemonic(Lang1)
            mnemonic_words = wordlist
        if startwords == 2:
            print('Mnemonic 12/15/18/21/24 Words to Bitcoin Address Tool')
            R = int(input('Enter Ammount Mnemonic Words 12/15/18/21/24 : '))
            if R == 12:
                s1 = 128
            elif R == 15:
                s1 = 160
            elif R == 18:
                s1 = 192
            elif R == 21:
                s1 = 224
            elif R == 24:
                s1 = 256
            else:
                print("WRONG NUMBER!!! Starting with 24 Words")
                s1 = 256
            Lang = int(input(' Choose language 1.english, 2.french, 3.italian, 4.spanish, 5.chinese_simplified, 6.chinese_traditional, 7.japanese or 8.korean '))
            if Lang == 1:
                Lang1 = "english"
            elif Lang == 2:
                Lang1 = "french"
            elif Lang == 3:
                Lang1 = "italian"
            elif Lang == 4:
                Lang1 = "spanish"
            elif Lang == 5:
                Lang1 = "chinese_simplified"
            elif Lang == 6:
                Lang1 = "chinese_traditional"
            elif Lang == 7:
                Lang1 = "japanese"
            elif Lang == 8:
                Lang1 = "korean"
            else:
                print("WRONG NUMBER!!! Starting with english")
                Lang1 = "english"
            mnemo = Mnemonic(Lang1)
            mnemonic_words = mnemo.generate(strength=s1)
        seed = mnemo.to_seed(mnemonic_words, passphrase="")
        data_wallet()
        for target_wallet in data:
            print('\nmnemonic_words  : ', mnemonic_words, '\nDerivation Path : ', target_wallet['path'], '\nBitcoin Address : ', target_wallet['address'], ' Balance = ', get_balance(target_wallet['address']), ' BTC', '\nPrivatekey WIF  : ', target_wallet['privatekey'])
            time.sleep(3.0)
    elif start == 10:
        print('WIF to Bitcoin Address Tool')
        WIF = str(input('Enter Your Wallet Import Format WIF = '))
        addr = Key(WIF).address
        print('\nWallet Import Format WIF = ', WIF)
        print('Bitcoin Address  = ', addr, '    Balance = ', get_balance(addr), ' BTC')
        data_info()
        for data_w in data:
            hash160 = data_w['hash160']
            address = data_w['address']
            n_tx = data_w['n_tx']
            total_received = data_w['total_received']
            total_sent = data_w['total_sent']
            final_balance = data_w['final_balance']
            print('================== Block Chain ==================')
            print('Bitcoin address   = ', address)
            print('hash160   = ', hash160)
            print('Number of tx    = ', n_tx)
            print('Total Received  = ', total_received)
            print('Total Sent      = ', total_sent)
            print('Final Balance   = ', final_balance)
            print('================== Block Chain ==================')
            time.sleep(3.0)
    elif start == 11:
        promptrsz= '''
    ********************** Получить подпись ECDSA R, S, Z инструмент rawtx или txid ********************************* 
    *                                                                                                               *
    *1-txid  Начинается расчет R,S,Z API блокчейна. [Требуется Интернет]                                            *
    *2-rawtx R, S, Z, Pubkey для каждого из входных данных, присутствующих в данных rawtx. [Интернет не требуется]  *
    *    Введите 1-2, чтобы начать                                                                                  *
    *                                                                                                               *
    ********************** Получить подпись ECDSA R, S, Z инструмент rawtx или txid ********************************* 
        '''
        startrsz=int(input(promptrsz))
        if startrsz == 1:
            txid = input(str('Type your txid here = ')) #'82e5e1689ee396c8416b94c86aed9f4fe793a0fa2fa729df4a8312a287bc2d5e'
            rawtx = ''
            if rawtx == '':
                rawtx = get_rawtx_from_blockchain(txid)
                print('\nStarting Program...')

                m = parseTx(rawtx)
                e = getSignableTxn(m)

                for i in range(len(e)):
                    print('='*70,f'\n[Input Index #: {i}]\n     R: {e[i][0]}\n     S: {e[i][1]}\n     Z: {e[i][2]}\nPubKey: {e[i][3]}')
                    f=open('file.txt','a')
                    f.write(f'{e[i][0]},{e[i][1]},{e[i][2]}\n')
                    f.close
        elif startrsz == 2:
            rawtx = input(str('Type your rawtx here = ')) #'01000000028370ef64eb83519fd14f9d74826059b4ce00eae33b5473629486076c5b3bf215000000008c4930460221009bf436ce1f12979ff47b4671f16b06a71e74269005c19178384e9d267e50bbe9022100c7eabd8cf796a78d8a7032f99105cdcb1ae75cd8b518ed4efe14247fb00c9622014104e3896e6cabfa05a332368443877d826efc7ace23019bd5c2bc7497f3711f009e873b1fcc03222f118a6ff696efa9ec9bb3678447aae159491c75468dcc245a6cffffffffb0385cd9a933545628469aa1b7c151b85cc4a087760a300e855af079eacd25c5000000008b48304502210094b12a2dd0f59b3b4b84e6db0eb4ba4460696a4f3abf5cc6e241bbdb08163b45022007eaf632f320b5d9d58f1e8d186ccebabea93bad4a6a282a3c472393fe756bfb014104e3896e6cabfa05a332368443877d826efc7ace23019bd5c2bc7497f3711f009e873b1fcc03222f118a6ff696efa9ec9bb3678447aae159491c75468dcc245a6cffffffff01404b4c00000000001976a91402d8103ac969fe0b92ba04ca8007e729684031b088ac00000000'
            print('\nStarting Program...')
            m = parseTx(rawtx)
            e = getSignableTxn(m)
            for i in range(len(e)):
                print('='*70,f'\n[Input Index #: {i}]\n     R: {e[i][0]}\n     S: {e[i][1]}\n     Z: {e[i][2]}\nPubKey: {e[i][3]}')
                f=open('file.txt','a')
                f.write(f'{e[i][0]},{e[i][1]},{e[i][2]}\n')
                f.close
        elif startrsz == 3:
            addr = str(input('Enter Your Bitcoin Address Here : '))
            contents = requests.get('https://chain.so/api/v2/address/BTC/' + addr, timeout=10)
            res = contents.json()
            response = (contents.content)
            TXS = dict(res['data'])['txs']
            for row in TXS:
                hexs = row["txid"]
                print(hexs)
                f=open('hexs.txt','a')
                f.write(hexs + '\n')
                f.close
            mylist=[]
            header = ['Transation ID ', 'Input Index', 'R', 'K for R', 'R bits', 'S', 'K for S', 'S bits', 'Z', 'K for Z', 'Z bits','PubKey']
            fr=open('full.csv', 'a', encoding='UTF8')
            writer = csv.writer(fr)
            writer.writerow(header)
            with open('hexs.txt', newline='', encoding='utf-8') as f:
                for line in f:
                    mylist.append(line.strip())
                    print('\nStarting Program... Sleeping 10 Seconds Between Scans')
                    for x in range(0,len(mylist)):
                        txid = mylist[x]
                        rawtx = ''
                    if rawtx == '':
                        rawtx = get_rawtx_from_blockchain(txid)

                        m = parseTx(rawtx)
                        e = getSignableTxn(m)
                        for i in range(len(e)):
                            data = []
                            hex1= e[i][0]
                            r = int(hex1, 16)
                            lengthr = len(bin(r))
                            lengthr -=2
                            hex2= e[i][1]
                            s = int(hex2, 16)
                            lengths = len(bin(s))
                            lengths -=2
                            hex3= e[i][2]
                            z = int(hex3, 16)
                            lengthz = len(bin(z))
                            lengthz -=2
                            pubkey = e[i][3]
                            print ('Current Transation = ',txid)
                            print('='*70,f'\n[Input Index #: {i}]\n     R: {e[i][0]}\n K for R = {r} {lengthr}  bits\n     S: {e[i][1]}\n K for S = {s} {lengths}  bits \n     Z: {e[i][2]}\n K for Z = {z} {lengthz}  bits \nPubKey: {e[i][3]}')
                            if i == 10:
                                print ('Sleep 10 Seconds Please wait Loading Next Transactions')
                                time.sleep(10)
                            f=open('filefull.txt','a')
                            f.write(f'\n[Input Index #: {i}]\n     R: {e[i][0]}\n K for R = {r} {lengthr}  bits\n     S: {e[i][1]}\n K for S = {s} {lengths}  bits\n     Z: {e[i][2]}\n K for Z = {z} {lengthz}  bits \nPubKey: {e[i][3]}')
                            f.close
                            data = [txid, f'{i}', f'{e[i][0]}', f'{r}', f'{lengthr}', f'{e[i][1]}', f'{s}', f'{lengths}', f'{e[i][2]}', f'{z}', f'{lengthz}', f'{e[i][3]}']
                            writer.writerow(data)
        elif startrsz == 4:
            mylist = []
            data = []
            header = ['Transation ID ', 'Input Index', 'R', 'K for R', 'R bits', 'S', 'K for S', 'S bits', 'Z', 'K for Z', 'Z bits','PubKey']
            fr=open('full.csv', 'a', encoding='UTF8')
            writer = csv.writer(fr)
            writer.writerow(header)
            with open('trans.txt', newline='', encoding='utf-8') as f:
                for line in f:
                    mylist.append(line.strip())
                    print('\nStarting Program... Sleeping 10 Seconds Between Scans')
                    for x in range(0,len(mylist)):
                        txid = mylist[x]
                        rawtx = ''
                    if rawtx == '':
                        rawtx = get_rawtx_from_blockchain(txid)

                        m = parseTx(rawtx)
                        e = getSignableTxn(m)
                        for i in range(len(e)):
                            data = []
                            hex1= e[i][0]
                            r = int(hex1, 16)
                            lengthr = len(bin(r))
                            lengthr -=2
                            hex2= e[i][1]
                            s = int(hex2, 16)
                            lengths = len(bin(s))
                            lengths -=2
                            hex3= e[i][2]
                            z = int(hex3, 16)
                            lengthz = len(bin(z))
                            lengthz -=2
                            pubkey = e[i][3]
                            print ('Current Transation = ',txid)
                            print('='*70,f'\n[Input Index #: {i}]\n     R: {e[i][0]}\n K for R = {r} {lengthr}  bits\n     S: {e[i][1]}\n K for S = {s} {lengths}  bits \n     Z: {e[i][2]}\n K for Z = {z} {lengthz}  bits \nPubKey: {e[i][3]}')
                            if i == 50:
                                print ('Sleep 10 Seconds Please wait Loading Next Transactions')
                                time.sleep(10)
                            f=open('filefull.txt','a')
                            f.write(f'\n[Input Index #: {i}]\n     R: {e[i][0]}\n K for R = {r} {lengthr}  bits\n     S: {e[i][1]}\n K for S = {s} {lengths}  bits\n     Z: {e[i][2]}\n K for Z = {z} {lengthz}  bits \nPubKey: {e[i][3]}')
                            f.close
                            data = [txid, f'{i}', f'{e[i][0]}', f'{r}', f'{lengthr}', f'{e[i][1]}', f'{s}', f'{lengths}', f'{e[i][2]}', f'{z}', f'{lengthz}', f'{e[i][3]}']
                            writer.writerow(data)
        else:
            print("WRONG NUMBER!!! MUST CHOSE 1 - 4 ")
    elif start == 12:
        prompt123= '''
            **************** Инструменты разделения диапазона *********************
            *          Разделить диапазон в битах или байтах                      *
            *               Вариант 1 Разделить диапазон в битах = 1              *
            *               Вариант 2 Разделить диапазон в байтах = 2             *
            **************** Инструменты разделения диапазона *********************
        Введите свой выбор здесь Введите 1-2 :
        '''
        promptstart=int(input(prompt123))
        if promptstart == 1:
            x=int(input("Биты начального диапазона Мин. 1–255 ->  "))
            y=int(input("биты диапазона остановки Макс. 256 -> "))
            start=2**x
            stop=2**y
            
        elif promptstart == 2:    
            start=int(input("начальный диапазон Мин. байт 1-115792089237316195423570985008687907852837564279074904382605163141518161494335 ->  "))
            stop=int(input("диапазон остановки Макс. байт 115792089237316195423570985008687907852837564279074904382605163141518161494336 -> "))

        rangediv=int(input("Раздел диапазона 1% t0 ???% ->  "))
        display =int(input("Выберите метод Метод отображения: 1 - HEX:; 2 - ДЕК  "))

        remainingtotal=stop-start
        div = round(remainingtotal / rangediv)
           
        divsion = []
               
        if display == 1:
            divsion = []
            divsion_wallet()
            for data_w in divsion:
                HEX = data_w['HEX']
                print('Процентов', data_w['percent'], ' : Privatekey (hex): ', data_w['HEX'])
                with open("hex.txt", "a") as f:
                    f.write(f"""\nПроцентов{data_w['percent']} Privatekey (hex): {data_w['HEX']}""")
                    f.close
        elif display == 2:
            divsion = []
            divsion_wallet()
            for data_w in divsion:
                seed = data_w['seed']
                print('Процентов', data_w['percent'], ' : Privatekey (dec): ', data_w['seed'])
                with open("dec.txt", "a") as f:
                    f.write(f"""\nПроцентов{data_w['percent']} Privatekey (dec): {data_w['seed']}""")
                    f.close
        else:
            print("НЕПРАВИЛЬНЫЙ НОМЕР!!! ДОЛЖЕН ВЫБРАТЬ 1 - 2 ")
                
    elif start == 13:
        promptchk= '''
    ************************* Биткойн-адреса из файла с проверкой баланса ************************* 
    *                                                                                             *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком биткойн-адресов.             *
    *    ** Ваш список адресов будет проверен на наличие баланса [требуется Интернет]             *
    *    ** ЛЮБЫЕ БИТКОИН-КОШЕЛЬКИ, НАЙДЕННЫЕ С БАЛАНСОМ, БУДУТ СОХРАНЕНЫ НА (balance.txt)        *
    *                                                                                             *
    ************************* Биткойн-адреса из файла с проверкой баланса *************************
        '''
        print(promptchk)
        time.sleep(0.5)
        print('Биткойн-адреса загружаются, пожалуйста, подождите..................................:')
        with open("btc.txt", "r") as file:
            line_count = 0
            for line in file:
                line != "\n"
                line_count += 1
        with open('btc.txt', newline='', encoding='utf-8') as f:
            for line in f:
                mylist.append(line.strip())
        print('Всего биткойн-адресов загружено now Checking Balance ', line_count)
        remaining=line_count
        for i in range(0,len(mylist)):
            count+=1
            remaining-=1
            addr = mylist[i]
            time.sleep(0.5)
            if float (get_balance(addr)) > ammount:
                print ('\nBitcoin Address = ', addr, '    Остаток средств = ', get_balance(addr), ' BTC')
                f=open('balance.txt','a')
                f.write('\nBitcoin Address = ' + addr + '    Остаток средств = ' + get_balance(addr) + ' BTC')
                f.close()
            else:
                print ('\nНомер сканирования = ',count, ' == Оставшийся = ', remaining)
                print ('\nBitcoin Address = ', addr, '    Остаток средств = ', get_balance(addr), ' BTC')
    elif start == 14:
        prompthash= '''
    *********************** Биткойн-адреса из файла в файл HASH160 Инструмент *********************** 
    *                                                                                                *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком биткойн-адресов.                *
    *    ** Ваш список адресов будет преобразован в HASH160 [Интернет не требуется]                  *
    *    ** Адреса HASH160 будут сохранены в файл с именем hash160.txt.                              *
    *                                                                                                *
    *********************** Биткойн-адреса из файла в файл HASH160 Инструмент ************************
        '''
        print(prompthash)
        time.sleep(0.5)
        print('Биткойн-адреса загружаются, пожалуйста, подождите..................................:')
        fname = 'btc.txt'
        with open(fname) as textfile, open("base_h160_1_bc1.txt", 'w+') as f_1, open("base_h160_3.txt", 'w+') as f_2:
            for line in textfile.readlines()[1:]:
                addr = (line.rstrip('\n'))
                if addr.startswith('1'):
                    address = addr.split('\t')[0]
                    f_1.write(ice.address_to_h160(address) + '\n')
                    count +=1
                if addr.startswith('3'):
                    address = addr.split('\t')[0]
                    f_2.write(ice.address_to_h160(address) + '\n')
                    count +=1
                if addr.startswith('bc1') and len(addr.split('\t')[0])< 50 :
                    address = addr.split('\t')[0]
                    f_1.write(ice.bech32_address_decode(address,coin_type=0) + '\n')
                    count +=1
            else:
                skip += 1
                print ('Total write address>',count, '-skiped address>',skip)

    elif start == 15:
        promptbrain= '''
    *********************** Список кошельков Brain из файла с помощью инструмента проверки баланса ******
    *                                                                                                   *
    *    ** Для этого инструмента требуется файл с именем brainwords.txt со списком слов Brain Wallet.  *
    *    ** Ваш список будет конвертирован в биткойны, а баланс проверен [требуется Интернет]           *
    *    ** ЛЮБЫЕ КОШЕЛЬКИ BRAIN, НАЙДЕННЫЕ С БАЛАНСОМ, БУДУТ СОХРАНЯТЬСЯ В (winner.txt)                *
    *                                                                                                   *
    ************* Список кошельков Brain из файла с помощью инструмента проверки баланса ****************
        '''
        print(promptbrain)
        time.sleep(0.5)
        print('ЗАГРУЗКА СПИСКА ПАРОЛЕЙ КОШЕЛЬКА BRAIN>>>>')
        with open("brainwords.txt", "r") as file:
            line_count = 0
            for line in file:
                line != "\n"
                line_count += 1
        with open('brainwords.txt', newline='', encoding='utf-8') as f:
            for line in f:
                mylist.append(line.strip())
        print('Всего загружен пароль кошелька Brain:', line_count)
        remaining=line_count
        for i in range(0,len(mylist)):
            time.sleep(0.5)
            count+=1
            remaining-=1
            passphrase = mylist[i]
            wallet = BrainWallet()
            private_key, addr = wallet.generate_address_from_passphrase(passphrase)
            if float (get_balance(addr)) > ammount:
                print ('\nBitcoin Address = ', addr, '    Остаток средств = ', get_balance(addr), ' BTC')
                print('Passphrase       : ',passphrase)
                print('Private Key      : ',private_key)
                print('Номер сканирования : ', count, ' : Оставшиеся пароли : ', remaining)
                f=open('winner.txt','a')
                f.write('\nBitcoin Address = ' + addr + '    Остаток средств = ' + get_balance(addr) + ' BTC')
                f.write('\nPassphrase       : '+ passphrase)
                f.write('\nPrivate Key      : '+ private_key)
                f.close()
            else:
                print ('\nScan Number = ',count, ' == Оставшиеся пароли = ', remaining)
                print ('\nBitcoin Address = ', addr, '    Остаток средств = ', get_balance(addr), ' BTC')
                time.sleep(1.0)
    elif start == 16:
        promptMnemonic= '''
    *********************** Генератор мнемонических слов Random [Offline] *************************
    *                                                                                             *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком баз данных биткойн-адресов.  *
    *    ** ЛЮБЫЕ МНЕМОНИЧЕСКИЕ СЛОВА, СООТВЕТСТВУЮЩИЕ БАЗЕ ДАННЫХ BTC, СОХРАНЯЮТСЯ В (winner.txt)*
    *                                                                                             *
    *********************** Генератор мнемонических слов Random [Offline] *************************
        '''
        print(promptMnemonic)
        time.sleep(0.5)
        filename ='btc.txt'
        with open(filename) as f:
            line_count = 0
            for line in f:
                line != "\n"
                line_count += 1        
        with open(filename) as file:
            add = file.read().split()
        add = set(add)
        print('Всего биткойн-адресов загружено ', line_count)        
        print('Мнемоника 12/15/18/21/24 Words to Bitcoin Address Tool')
        R = int(input('Введите количество мнемонических слов 12/15/18/21/24:'))
        if R == 12:
            s1 = 128
        elif R == 15:
            s1 = 160
        elif R == 18:
            s1 = 192
        elif R == 21:
            s1 = 224
        elif R == 24:
            s1 = 256
        else:
            print("НЕПРАВИЛЬНЫЙ НОМЕР!!! Начиная с 24 слов")
            s1 = 256
        display = int(input('1=Full Display (Slower) 2=Slient Mode (Faster) : '))
        while True:
            data=[]
            count += 1
            total += 20
            mnemo = Mnemonic("english")
            mnemonic_words = mnemo.generate(strength=s1)
            seed = mnemo.to_seed(mnemonic_words, passphrase="")
            entropy = mnemo.to_entropy(mnemonic_words)
            data_wallet()
            for target_wallet in data:
                address = target_wallet['address']
                if address in add:
                    print('\nMatch Found')
                    print('\nmnemonic_words  : ', mnemonic_words)
                    print('Derivation Path : ', target_wallet['path'], ' : Bitcoin Address : ', target_wallet['address'])
                    print('Privatekey WIF  : ', target_wallet['privatekey'])
                    with open("winner.txt", "a") as f:
                        f.write(f"""\nMnemonic_words:  {mnemonic_words}
                        Derivation Path:  {target_wallet['path']}
                        Privatekey WIF:  {target_wallet['privatekey']}
                        Public Address Bitcoin:  {target_wallet['address']}
                        =====Made by mizogg.co.uk Donations 3GCypcW8LWzNfJEsTvcFwUny3ygPzpTfL4 =====""")
            else:
                if display == 1:
                    print(' [' + str(count) + '] ------------------------')
                    print('Total Checked [' + str(total) + '] ')
                    print('\nmnemonic_words  : ', mnemonic_words)
                    for bad_wallet in data:
                        print('Derivation Path : ', bad_wallet['path'], ' : Bitcoin Address : ', bad_wallet['address'])
                        print('Privatekey WIF  : ', bad_wallet['privatekey'])
                if display == 2:
                    print(' [' + str(count) + '] ------', 'Total Checked [' + str(total) + '] ', end='\r')

    elif start == 17:
        promptrandom= '''
    *********************** Случайное сканирование биткойнов в случайном порядке в Range Tool ***********
    *                                                                                                   *
    *    ** Случайное сканирование биткойнов случайным образом в диапазоне [Offline]                    *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком баз данных биткойн-адресов.        *
    *    ** ЛЮБЫЕ СООТВЕТСТВУЮЩИЕ КОШЕЛЬКИ, СООТВЕТСТВУЮЩИЕ БАЗЕ ДАННЫХ BTC, СОХРАНЯЮТ В (winner.txt)   *
    *                                                                                                   *
    *******[+] Запуск....Пожалуйста, подождите....Загружается список биткойн-адресов....*****************
        '''
        print(promptrandom)
        time.sleep(0.5)
        filename ='btc.txt'
        with open(filename) as f:
            line_count = 0
            for line in f:
                line != "\n"
                line_count += 1
        with open(filename) as file:
            add = file.read().split()
        add = set(add)
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count)) 
        start=int(input("начальный диапазон Мин. 1-115792089237316195423570985008687907852837564279074904382605163141518161494335 ->  "))
        stop=int(input("диапазон остановки Макс.115792089237316195423570985008687907852837564279074904382605163141518161494336 -> "))
        print("Начинается поиск... Пожалуйста, подождите мин. диапазон: " + str(start))
        print("Максимальный диапазон: " + str(stop))
        print("==========================================================")
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count))    
        while True:
            count += 4
            iteration += 1
            ran=random.randrange(start,stop)
            seed = str(ran)
            HEX = "%064x" % ran   
            wifc = ice.btc_pvk_to_wif(HEX)
            wifu = ice.btc_pvk_to_wif(HEX, False)
            caddr = ice.privatekey_to_address(0, True, int(seed)) #Compressed
            uaddr = ice.privatekey_to_address(0, False, int(seed))  #Uncompressed
            P2SH = ice.privatekey_to_address(1, True, int(seed)) #p2sh
            BECH32 = ice.privatekey_to_address(2, True, int(seed))  #bech32

            if caddr in add or uaddr in add or P2SH in add or BECH32 in add :
                print('\nMatch Found')
                print('\nPrivatekey (dec): ', seed,'\nPrivatekey (hex): ', HEX, '\nPrivatekey Uncompressed: ', wifu, '\nPrivatekey compressed: ', wifc, '\nPublic Address 1 Uncompressed: ', uaddr, '\nPublic Address 1 Compressed: ', caddr, '\nPublic Address 3 P2SH: ', P2SH, '\nPublic Address bc1 BECH32: ', BECH32)
                f=open("winner.txt","a")
                f.write('\nPrivatekey (dec): ' + seed)
                f.write('\nPrivatekey (hex): ' + HEX)
                f.write('\nPrivatekey Uncompressed: ' + wifu)
                f.write('\nPrivatekey compressed: ' + wifc)
                f.write('\nPublic Address 1 Compressed: ' + caddr)
                f.write('\nPublic Address 1 Uncompressed: ' + uaddr)
                f.write('\nPublic Address 3 P2SH: ' + P2SH)
                f.write('\nPublic Address bc1 BECH32: ' + BECH32)
            else:
                if iteration % 10000 == 0:
                    elapsed = time.time() - start_time
                    print(f'It/CPU={iteration} checked={count} Hex={HEX} Keys/Sec={iteration / elapsed:.1f}')
    elif start == 18:
        promptsequence= '''
    *********************** Биткойн-последовательность Division in Range Tool ***************************
    *                                                                                                   *
    *    ** Последовательность биткойнов и деление диапазона на 1%-1000000%                             *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком баз данных биткойн-адресов.        *
    *    ** ЛЮБЫЕ СООТВЕТСТВУЮЩИЕ КОШЕЛЬКИ, СООТВЕТСТВУЮЩИЕ БАЗЕ ДАННЫХ BTC, СОХРАНЯЮТ В (winner.txt)   *
    *                                                                                                   *
    *******[+] Запуск....Пожалуйста, подождите....Загружается список биткойн-адресов....*****************
        '''
        print(promptsequence)
        time.sleep(0.5)
        filename ='btc.txt'
        with open(filename) as f:
            line_count = 0
            for line in f:
                line != "\n"
                line_count += 1
        with open(filename) as file:
            add = file.read().split()
        add = set(add)
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count)) 
        start=int(input("начальный диапазон Мин. 1-115792089237316195423570985008687907852837564279074904382605163141518161494335 ->  "))
        stop=int(input("диапазон остановки Макс.115792089237316195423570985008687907852837564279074904382605163141518161494336 -> "))
        mag=int(input("Величина прыжкового шага -> "))
        rangediv=int(input("Раздел диапазона 1% t0 ???% ->  "))
        display =int(input("Выберите метод Метод отображения: 1 - Меньше деталей: (Самый быстрый); 2 - Шестнадцатеричные детали: (медленнее); 3 - Детали кошелька: (медленнее)  "))
        print("Начинается поиск... Пожалуйста, подождите мин. диапазон: " + str(start))
        print("Максимальный диапазон: " + str(stop))
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count))

        remainingtotal=stop-start
        div = round(remainingtotal / rangediv)
        finish = div + start
        finishscan = round(stop / rangediv)
        while start < finish:
            try:
                data = []
                remainingtotal-=mag
                finish-=mag
                start+=mag
                count += 1
                total += rangediv*4
                SEQ_wallet()
                for data_w in data:
                    caddr = data_w['caddr']
                    uaddr = data_w['uaddr']
                    p2sh = data_w['p2sh']
                    bech32 = data_w['bech32']
                    if caddr in add or uaddr in add or p2sh in add or bech32 in add:
                        print('\nСовпадение найдено в : ', data_w['percent'])
                        print('\nPrivatekey (dec): ', data_w['seed'], '\nPrivatekey (hex): ', data_w['HEX'], '\nPrivatekey Uncompressed: ', data_w['wifu'], '\nPrivatekey compressed: ', data_w['wifc'], '\nPublic Address 1 Uncompressed: ', data_w['uaddr'], '\nPublic Address 1 compressed: ', data_w['caddr'], '\nPublic Address 3 P2SH: ', data_w['p2sh'], '\nPublic Address bc1 BECH32: ', data_w['bech32'])
                        with open("winner.txt", "a") as f:
                            f.write(f"""\nMatch Found IN  {data_w['percent']}
                            Privatekey (dec):  {data_w['seed']}
                            Privatekey (hex): {data_w['HEX']}
                            Privatekey Uncompressed:  {data_w['wifu']}
                            Privatekey Compressed:  {data_w['wifc']}
                            Public Address 1 Uncompressed:  {data_w['uaddr']}
                            Public Address 1 Compressed:  {data_w['caddr']}
                            Public Address 3 P2SH:  {data_w['p2sh']}
                            Public Address bc1 BECH32:  {data_w['bech32']}
                            =====Made by mizogg.co.uk Donations 3GCypcW8LWzNfJEsTvcFwUny3ygPzpTfL4 =====""")
                            
                    else:
                        if display == 1:
                            print('Сканировать: ', count , ' :Оставшийся: ', str(finish), ' :Всего: ', str(total), end='\r')
                        elif display == 2:
                            for bad_wallet in data:
                                print(bad_wallet['percent'], '\nPrivatekey (hex): ', bad_wallet['HEX'], end='\r')
                        elif display == 3:
                            for bad_wallet in data:
                                print(bad_wallet['percent'])
                                print('\nPrivatekey (dec): ', bad_wallet['seed'], '\nPrivatekey (hex): ', bad_wallet['HEX'], '\nPrivatekey Uncompressed: ', bad_wallet['wifu'], '\nPrivatekey compressed: ', bad_wallet['wifc'], '\nPublic Address 1 Uncompressed: ', bad_wallet['uaddr'], '\nPublic Address 1 compressed: ', bad_wallet['caddr'], '\nPublic Address 3 P2SH: ', bad_wallet['p2sh'], '\nPublic Address bc1 BECH32: ', bad_wallet['bech32'])
                        else:
                            print("НЕПРАВИЛЬНЫЙ НОМЕР!!! ДОЛЖЕН ВЫБРАТЬ 1, 2 или 3")
                            break
                        
                                
            except(KeyboardInterrupt, SystemExit):
                exit('\nОбнаружено сочетание клавиш CTRL-C. Выход изящно. Спасибо и удачной охоты')
    elif start == 19:
        promptinverse= '''
    *********************** Инструмент случайного обратного диапазона биткойнов K ***********************
    *                                                                                                   *
    *    ** Биткойн Случайный инверсный K-диапазон                                                      *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком баз данных биткойн-адресов.        *
    *    ** ЛЮБЫЕ СООТВЕТСТВУЮЩИЕ КОШЕЛЬКИ, СООТВЕТСТВУЮЩИЕ БАЗЕ ДАННЫХ BTC, СОХРАНЯЮТ В (winner.txt)   *
    *                                                                                                   *
    ********[+] Запуск.........Пожалуйста, подождите.....Загружается список адресов биткойнов.....*******
        '''
        print(promptinverse)
        time.sleep(0.5)
        filename ='btc.txt'
        with open(filename) as f:
            line_count = 0
            for line in f:
                line != "\n"
                line_count += 1
        with open(filename) as file:
            add = file.read().split()
        add = set(add)
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count))  
        start = int(input("начальный диапазон Мин. 1-57896044618658097711785492504343953926418782139537452191302581570759080747168 ->  "))
        stop = int(input("диапазон остановки МАКС. 57896044618658097711785492504343953926418782139537452191302581570759080747169 ->  "))
        print("Начинается поиск... Пожалуйста, подождите мин. диапазон: " + str(start))
        print("Максимальный диапазон: " + str(stop))
        print("==========================================================")
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count))
        while True:
            count += 8
            iteration += 1
            ran=random.randrange(start,stop)
            k1 = int(ran)
            HEXk1 = "%064x" % k1
            k2 = (k1*(n-1))%n
            HEXk2 = "%064x" % k2
            wifck1 = ice.btc_pvk_to_wif(HEXk1)
            wifuk1 = ice.btc_pvk_to_wif(HEXk1, False)
            caddrk1 = ice.privatekey_to_address(0, True, k1) #Compressed
            uaddrk1 = ice.privatekey_to_address(0, False, k1)  #Uncompressed
            P2SHk1 = ice.privatekey_to_address(1, True, k1) #p2sh
            BECH32k1 = ice.privatekey_to_address(2, True, k1)  #bech32
            
            wifck2 = ice.btc_pvk_to_wif(HEXk2)
            wifuk2 = ice.btc_pvk_to_wif(HEXk2, False)
            caddrk2 = ice.privatekey_to_address(0, True, k2) #Compressed
            uaddrk2 = ice.privatekey_to_address(0, False, k2)  #Uncompressed
            P2SHk2 = ice.privatekey_to_address(1, True, k2) #p2sh
            BECH32k2 = ice.privatekey_to_address(2, True, k2)  #bech32    
            if caddrk1 in add or uaddrk1 in add or P2SHk1 in add or BECH32k1 in add :
                print('\nMatch Found')
                print('\nPrivatekey (dec): ', k1,'\nPrivatekey (hex): ', HEXk1, '\nPrivatekey Uncompressed: ', wifuk1, '\nPrivatekey compressed: ', wifck1, '\nPublic Address 1 Uncompressed: ', uaddrk1, '\nPublic Address 1 Compressed: ', caddrk1, '\nPublic Address 3 P2SH: ', P2SHk1, '\nPublic Address bc1 BECH32: ', BECH32k1)
                f=open("winner.txt","a")
                f.write('\nPrivatekey (dec): ' + str(k1))
                f.write('\nPrivatekey (hex): ' + HEXk1)
                f.write('\nPrivatekey Uncompressed: ' + wifuk1)
                f.write('\nPrivatekey compressed: ' + wifck1)
                f.write('\nPublic Address 1 Compressed: ' + caddrk1)
                f.write('\nPublic Address 1 Uncompressed: ' + uaddrk1)
                f.write('\nPublic Address 3 P2SH: ' + P2SHk1)
                f.write('\nPublic Address bc1 BECH32: ' + BECH32k1)
            if caddrk2 in add or uaddrk2 in add or P2SHk2 in add or BECH32k2 in add :
                print('\nMatch Found')
                print('\nPrivatekey (dec): ', k2,'\nPrivatekey (hex): ', HEXk2, '\nPrivatekey Uncompressed: ', wifuk2, '\nPrivatekey compressed: ', wifck2, '\nPublic Address 1 Uncompressed: ', uaddrk2, '\nPublic Address 1 Compressed: ', caddrk2, '\nPublic Address 3 P2SH: ', P2SHk2, '\nPublic Address bc1 BECH32: ', BECH32k2)
                f=open("winner.txt","a")
                f.write('\nPrivatekey (dec): ' + str(k2))
                f.write('\nPrivatekey (hex): ' + HEXk2)
                f.write('\nPrivatekey Uncompressed: ' + wifuk2)
                f.write('\nPrivatekey compressed: ' + wifck2)
                f.write('\nPublic Address 1 Compressed: ' + caddrk2)
                f.write('\nPublic Address 1 Uncompressed: ' + uaddrk2)
                f.write('\nPublic Address 3 P2SH: ' + P2SHk2)
                f.write('\nPublic Address bc1 BECH32: ' + BECH32k2)
            else:
                if iteration % 10000 == 0:
                    elapsed = time.time() - start_time
                    addper= round(iteration / elapsed)*8
                    print(f'It/CPU={iteration} checked={count} Address/Sec={addper} Keys/Sec={iteration / elapsed:.1f}')
    elif start == 20:
        promptinversesq= '''
    *********************** Биткойн-последовательность Inverse K Range Tool *****************************
    *                                                                                                   *
    *    ** Биткойн-последовательность, обратный K-диапазон                                             *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком баз данных биткойн-адресов.        *
    *    ** ЛЮБЫЕ СООТВЕТСТВУЮЩИЕ КОШЕЛЬКИ, СООТВЕТСТВУЮЩИЕ БАЗЕ ДАННЫХ BTC, СОХРАНЯЮТ В (winner.txt)   *
    *                                                                                                   *
    ******[+] Запуск.........Пожалуйста, подождите.....Загружается список адресов биткойнов.....*********
        '''
        print(promptinversesq)
        time.sleep(0.5)
        filename ='btc.txt'
        with open(filename) as f:
            line_count = 0
            for line in f:
                line != "\n"
                line_count += 1
        with open(filename) as file:
            add = file.read().split()
        add = set(add)
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count))  
        start = int(input("начальный диапазон Мин. 1-57896044618658097711785492504343953926418782139537452191302581570759080747168 ->  "))
        stop = int(input("диапазон остановки МАКС. 57896044618658097711785492504343953926418782139537452191302581570759080747169 ->  "))
        mag=int(input("Величина прыжкового шага -> "))
        print("Начинается поиск... Пожалуйста, подождите мин. диапазон: " + str(start))
        print("Максимальный диапазон: " + str(stop))
        print("==========================================================")
        print('Всего биткойн-адресов загружено и проверено : ',str (line_count))
        while start < stop:
            count += 8
            iteration += 1
            start+=mag
            k1 = int(start)
            HEXk1 = "%064x" % k1
            k2 = (k1*(n-1))%n
            HEXk2 = "%064x" % k2
            wifck1 = ice.btc_pvk_to_wif(HEXk1)
            wifuk1 = ice.btc_pvk_to_wif(HEXk1, False)
            caddrk1 = ice.privatekey_to_address(0, True, k1) #Compressed
            uaddrk1 = ice.privatekey_to_address(0, False, k1)  #Uncompressed
            P2SHk1 = ice.privatekey_to_address(1, True, k1) #p2sh
            BECH32k1 = ice.privatekey_to_address(2, True, k1)  #bech32
            
            wifck2 = ice.btc_pvk_to_wif(HEXk2)
            wifuk2 = ice.btc_pvk_to_wif(HEXk2, False)
            caddrk2 = ice.privatekey_to_address(0, True, k2) #Compressed
            uaddrk2 = ice.privatekey_to_address(0, False, k2)  #Uncompressed
            P2SHk2 = ice.privatekey_to_address(1, True, k2) #p2sh
            BECH32k2 = ice.privatekey_to_address(2, True, k2)  #bech32    
            if caddrk1 in add or uaddrk1 in add or P2SHk1 in add or BECH32k1 in add :
                print('\nMatch Found')
                print('\nPrivatekey (dec): ', k1,'\nPrivatekey (hex): ', HEXk1, '\nPrivatekey Uncompressed: ', wifuk1, '\nPrivatekey compressed: ', wifck1, '\nPublic Address 1 Uncompressed: ', uaddrk1, '\nPublic Address 1 Compressed: ', caddrk1, '\nPublic Address 3 P2SH: ', P2SHk1, '\nPublic Address bc1 BECH32: ', BECH32k1)
                f=open("winner.txt","a")
                f.write('\nPrivatekey (dec): ' + str(k1))
                f.write('\nPrivatekey (hex): ' + HEXk1)
                f.write('\nPrivatekey Uncompressed: ' + wifuk1)
                f.write('\nPrivatekey compressed: ' + wifck1)
                f.write('\nPublic Address 1 Compressed: ' + caddrk1)
                f.write('\nPublic Address 1 Uncompressed: ' + uaddrk1)
                f.write('\nPublic Address 3 P2SH: ' + P2SHk1)
                f.write('\nPublic Address bc1 BECH32: ' + BECH32k1)
            if caddrk2 in add or uaddrk2 in add or P2SHk2 in add or BECH32k2 in add :
                print('\nMatch Found')
                print('\nPrivatekey (dec): ', k2,'\nPrivatekey (hex): ', HEXk2, '\nPrivatekey Uncompressed: ', wifuk2, '\nPrivatekey compressed: ', wifck2, '\nPublic Address 1 Uncompressed: ', uaddrk2, '\nPublic Address 1 Compressed: ', caddrk2, '\nPublic Address 3 P2SH: ', P2SHk2, '\nPublic Address bc1 BECH32: ', BECH32k2)
                f=open("winner.txt","a")
                f.write('\nPrivatekey (dec): ' + str(k2))
                f.write('\nPrivatekey (hex): ' + HEXk2)
                f.write('\nPrivatekey Uncompressed: ' + wifuk2)
                f.write('\nPrivatekey compressed: ' + wifck2)
                f.write('\nPublic Address 1 Compressed: ' + caddrk2)
                f.write('\nPublic Address 1 Uncompressed: ' + uaddrk2)
                f.write('\nPublic Address 3 P2SH: ' + P2SHk2)
                f.write('\nPublic Address bc1 BECH32: ' + BECH32k2)
            else:
                if iteration % 10000 == 0:
                    elapsed = time.time() - start_time
                    addper= round(iteration / elapsed)*8
                    print(f'It/CPU={iteration} checked={count} Address/Sec={addper} Keys/Sec={iteration / elapsed:.1f}')
        
        
    elif start == 21:
        promptWIF= '''
    *********************** Биткойн WIF Recovery или инструмент проверки WIF ************************
    *                                                                                               *
    *    ** Найдите недостающие части формата импорта кошелька (WIF) для биткойнов                  *
    *    ** Этот инструмент работает только с WIF Starting 5 K L                                    *
    *    ** ЛЮБОЙ СООТВЕТСТВУЮЩИЙ WIF, СОЗДАННЫЙ ЭТОМУ АДРЕСУ СОВПАДЕНИЯ, СОХРАНИТ В (winner.txt)   *
    *                                                                                               *
    *********************** Биткойн WIF Recovery или инструмент проверки WIF ************************
        '''
        print(promptWIF)
        time.sleep(0.5)   
        miss = int(input('Сколько пропущенных символов Введите 0, если нет: '))
        if miss == 0:
            startsingle= str(input('Введите свой WIF ЗДЕСЬ : '))
            if startsingle[0] == '5':
                private_key_WIF = startsingle
                first_encode = base58.b58decode(private_key_WIF)
                private_key_full = binascii.hexlify(first_encode)
                private_key = private_key_full[2:-8]
            if startsingle[0] in ['L', 'K']:
                private_key_WIF = startsingle
                first_encode = base58.b58decode(private_key_WIF)
                private_key_full = binascii.hexlify(first_encode)
                private_key = private_key_full[2:-10]
            key = Key.from_hex(str(private_key.decode('utf-8')))
            wif = bytes_to_wif(key.to_bytes(), compressed=False)
            wif1 = bytes_to_wif(key.to_bytes(), compressed=True)
            key1 = Key(wif)
            addr = key.address
            addr1 = key1.address
            print('\nPrivateKey= ', private_key.decode('utf-8'), '\nCompressed Address = ', addr, '\nCompressed WIF = ', wif1, '\nUncompressed = ', addr1, '\nUncompressed WIF = ', wif)
            f=open('winner.txt','a')
            f.write('\nPrivateKey= ' + private_key.decode('utf-8') + '\nCompressed Address = ' + addr + '\nCompressed WIF = ' + wif1 + '\nUncompressed = ' + addr1 + '\nUncompressed WIF = ' + wif)
            f.close()
        else:
            start= str(input('Выйти из банка или ввести начальную часть : '))
            stop = str(input('Выйти из банка или ввести конечную часть : '))
            add= str(input('Введите биткойн-адрес Ищете совпадение с WIF = '))
            for a in iter_all(miss):
                total+=1
                if start[0] == '5':
                    private_key_WIF = a + stop
                    first_encode = base58.b58decode(private_key_WIF)
                    private_key_full = binascii.hexlify(first_encode)
                    private_key = private_key_full[2:-8]
                if start[0] in ['L', 'K']:
                    private_key_WIF = a + stop
                    first_encode = base58.b58decode(private_key_WIF)
                    private_key_full = binascii.hexlify(first_encode)
                    private_key = private_key_full[2:-10]
                key = Key.from_hex(str(private_key.decode('utf-8')))
                wif = bytes_to_wif(key.to_bytes(), compressed=False)
                wif1 = bytes_to_wif(key.to_bytes(), compressed=True)
                key1 = Key(wif)
                addr = key.address
                addr1 = key1.address
                print(' Scanning : ', total,' : Current TEST WIF= ', private_key_WIF, end='\r')
                #print('\n GOOD LUCK AND HAPPY HUNTING', '\nPrivateKey= ', private_key.decode('utf-8'), '\nCompressed Address = ', addr, '\nCompressed WIF = ', wif1, '\nUncompressed = ', addr1, '\nUncompressed WIF = ', wif)
                if addr in add or addr1 in add:
                    print('\n Congraz FOUND!!!', '\nPrivateKey= ', private_key.decode('utf-8'), '\nCompressed Address = ', addr, '\nCompressed WIF = ', wif1, '\nUncompressed = ', addr1, '\nUncompressed WIF = ', wif)
                    f=open('winner.txt','a')
                    f.write('\n Congraz FOUND!!!' + '\nPrivateKey= ' + private_key.decode('utf-8') + '\nCompressed Address = ' + addr + '\nCompressed WIF = ' + wif1 + '\nUncompressed = ' + addr1 + '\nUncompressed WIF = ' + wif)
                    f.close()     
    elif start == 22:
        promptPUB= '''
    *********************** Биткойн-адреса из файла в инструмент открытого ключа ***********************
    *                                                                                                  *
    *    ** Этому инструменту нужен файл с именем btc.txt со списком биткойн-адресов.                  *
    *    ** Ваш список адресов будет проверен на наличие известных открытых ключей [требуется Интернет]*
    *    ** ЛЮБОЙ БИТКОИН-АДРЕС С ОТКРЫТЫМ КЛЮЧЕМ БУДЕТ СОХРАНЕН В (pubkeys.txt)                       *
    *                                                                                                  *
    *********************** Биткойн-адреса из файла в инструмент открытого ключа ***********************
        '''
        print(promptPUB)
        time.sleep(0.5)
        print('Биткойн-адреса загружаются для проверки открытых ключей, пожалуйста, подождите................:')
        with open('btc.txt', newline='', encoding='utf-8') as f:
            for line in f:
                mylist.append(line.strip())
        print('Биткойн-адреса загружены сейчас Проверка открытых ключей ')
        myfile = open('pubkeys.txt', 'w')

        for i in range(0,len(mylist)):
            address = mylist[i]
            link = f"https://blockchain.info/q/pubkeyaddr/{address}"
            time.sleep(0.5)
            f = requests.get(link)
            if(f.text == ''):
                pass
            else:
                myfile.write("%s\n" % f.text)
                print(f.text)

        myfile.close()
    elif start == 23:
        promptADD2PUB= '''
    *********************** Публичный ключ из файла в инструмент биткойн-адресов **************
    *                                                                                         *
    *    ** Этому инструменту нужен файл с именем pubkeys.txt со списком открытых ключей.     *
    *    ** Ваш список открытых ключей будет перенесен на адреса Bitcion [OFF Line]           *
    *    ** Вся информация о публичном ключе будет сохранена в (add_info.txt)                 *
    *                                                                                         *
    *********************** Публичный ключ из файла в инструмент биткойн-адресов **************
        '''
        print(promptADD2PUB)
        time.sleep(0.5)
        print('открытые ключи загружаются в адреса Bitcion, пожалуйста, подождите ................:')
        import hashlib, base58
        with open('pubkeys.txt', newline='', encoding='utf-8') as f:
            for line in f:
                mylist.append(line.strip())

        for i in range(0,len(mylist)):
            pubkey = mylist[i]
            compress_pubkey = False
            if (compress_pubkey):
                if (ord(bytearray.fromhex(pubkey[-2:])) % 2 == 0):
                    pubkey_compressed = '02'
                else:
                    pubkey_compressed = '03'
                pubkey_compressed += pubkey[2:66]
                hex_str = bytearray.fromhex(pubkey_compressed)
            else:
                hex_str = bytearray.fromhex(pubkey)
            key_hash = '00' + hash160pub(hex_str)
            sha = hashlib.sha256()
            sha.update( bytearray.fromhex(key_hash) )
            checksum = sha.digest()
            sha = hashlib.sha256()
            sha.update(checksum)
            checksum = sha.hexdigest()[0:8]

            print ( "checksum = \t" + sha.hexdigest() )
            print ( "key_hash + checksum = \t" + key_hash + ' ' + checksum )
            print ( "bitcoin address = \t" + (base58.b58encode( bytes(bytearray.fromhex(key_hash + checksum)) )).decode('utf-8') )
            f=open('add_info.txt','a')
            f.write( "\nchecksum = \t" + sha.hexdigest() )
            f.write( "\nkey_hash + checksum = \t" + key_hash + ' ' + checksum )
            f.write( "\nbitcoin address = \t" + (base58.b58encode( bytes(bytearray.fromhex(key_hash + checksum)) )).decode('utf-8') + '\n')
            f.close()

    elif start == 24:
        promptETH= '''
    ******************** Инструмент проверки баланса адреса и информации Ethereum ******************
    *                                                                                              *
    *    1-Ethereum Address Balance and Info Check Tool Single [требуется Интернет]                *
    *    2-Баланс адреса Ethereum и инструмент проверки информации из файла [требуется Интернет]   *
    *     Введите 1-2, чтобы начать                                                                *
    *                                                                                              *
    ******************** Инструмент проверки баланса адреса и информации Ethereum ******************
        '''
        startETH=int(input(promptETH))
        if startETH == 1:
            print ('Ethereum Address Balance and Info Check Tool')
            ethadd = str(input('Enter Your ETH Address Here : '))
            blocs=requests.get("https://api.ethplorer.io/getAddressInfo/" + ethadd +apikeys)
            ress = blocs.json()
            address = dict(ress)['address']
            countTxs = dict(ress)['countTxs']
            ETHbalance = dict(ress)['ETH']['balance']
            print(f''' 
             |==============================================|=======|=====================|
             | Эфириум (ETH) Адрес                       |No. TXS|Остаток средств              |
             |==============================================|=======|=====================|
             | ''', address, ''' | ''', countTxs, '''   | ''', ETHbalance, '''   |
             |==============================================|============|=======|=================================|
             | Эфириум (ETH) Адрес                       |HoldersCount|Symbol |Name of Token                    |
             |==============================================|============|=======|=================================|''')

            time.sleep(3)
            tokens = dict(ress)['tokens']
            for row in tokens:
                tokenInfo= row['tokenInfo']
                taddress = tokenInfo['address']
                symbol = tokenInfo['symbol']
                holdersCount= tokenInfo['holdersCount']
                name =tokenInfo['name']
                print (' | ', taddress, ' | ', holdersCount, ' | ', symbol, '|', name, '|')
            time.sleep(3.0)
        if startETH == 2:
            with open('eth.txt', newline='', encoding='utf-8') as f:
                for line in f:
                    mylist.append(line.strip())
            for i in range(0,len(mylist)):
                count+=1
                ethadd = mylist[i]
                time.sleep(0.5)
                blocs=requests.get("https://api.ethplorer.io/getAddressInfo/" + ethadd +apikeys)
                ress = blocs.json()
                address = dict(ress)['address']
                countTxs = dict(ress)['countTxs']
                ETHbalance = dict(ress)['ETH']['balance']
                print(f''' 
                 |==============================================|=======|=========|
                 | Эфириум (ETH) Адрес                       |No. TXS|Остаток средств  |
                 |==============================================|=======|=========|
                 | ''', address, ''' | ''', countTxs, '''   | ''', ETHbalance, '''    | ''')
                if countTxs > 0:
                    with open("winner.txt", "a") as f:
                        f.write('\nEthereum (ETH) Address : ' + address + ' : No. TXS = ' + str(countTxs) + ' : Balance = ' + str(ETHbalance))
                        f.close
    elif start == 25:
        print('Инструмент преобразования шестнадцатеричного в десятичный')
        HEX = str(input('Введите свой шестнадцатеричный HEX здесь : '))
        dec = int(HEX, 16)
        length = len(bin(dec))
        length -=2
        PRIVATE_KEY = "%064x" % dec
        hdwallet: HDWallet = HDWallet(symbol=SYMBOL)
        hdwallet.from_private_key(private_key=PRIVATE_KEY)
        ethadd = hdwallet.p2pkh_address()
        print('\nHexadecimal = ',HEX, '\nTo Decimal = ', dec, '  bits ', length)
        print("Cryptocurrency:", hdwallet.cryptocurrency())
        print("Symbol:", hdwallet.symbol())
        print("Network:", hdwallet.network())
        print("Uncompressed:", hdwallet.uncompressed())
        print("Compressed:", hdwallet.compressed())
        print("Private Key:", hdwallet.private_key())
        print("Public Key:", hdwallet.public_key())
        print("Finger Print:", hdwallet.finger_print())
        print("Hash:", hdwallet.hash())
        blocs=requests.get("https://api.ethplorer.io/getAddressInfo/" + ethadd +apikeys)
        ress = blocs.json()
        address = dict(ress)['address']
        countTxs = dict(ress)['countTxs']
        ETHbalance = dict(ress)['ETH']['balance']
        print(f''' 
         |==============================================|=======|=========|
         | Эфириум (ETH) Адрес                       |No. TXS|Остаток средств  |
         |==============================================|=======|=========|
         | ''', address, ''' | ''', countTxs, '''   | ''', ETHbalance, '''    | ''')
        time.sleep(3.0)
    elif start == 26:
        print('Decimal to Hexadecimal Tool')
        dec = int(input('Enter Your Decimal DEC Here : '))
        HEX = "%064x" % dec
        length = len(bin(dec))
        length -=2
        hdwallet: HDWallet = HDWallet(symbol=SYMBOL)
        hdwallet.from_private_key(private_key=HEX)
        ethadd = hdwallet.p2pkh_address()
        print('\nDecimal = ', dec, '  bits ', length, '\nTo Hexadecimal = ', HEX)
        print("Cryptocurrency:", hdwallet.cryptocurrency())
        print("Symbol:", hdwallet.symbol())
        print("Network:", hdwallet.network())
        print("Uncompressed:", hdwallet.uncompressed())
        print("Compressed:", hdwallet.compressed())
        print("Private Key:", hdwallet.private_key())
        print("Public Key:", hdwallet.public_key())
        print("Finger Print:", hdwallet.finger_print())
        print("Hash:", hdwallet.hash())
        blocs=requests.get("https://api.ethplorer.io/getAddressInfo/" + ethadd +apikeys)
        ress = blocs.json()
        address = dict(ress)['address']
        countTxs = dict(ress)['countTxs']
        ETHbalance = dict(ress)['ETH']['balance']
        print(f''' 
         |==============================================|=======|=========|
         | Эфириум (ETH) Адрес                       |No. TXS|Остаток средств  |
         |==============================================|=======|=========|
         | ''', address, ''' | ''', countTxs, '''   | ''', ETHbalance, '''    | ''')
        time.sleep(3.0)
    elif start ==27:
        promptword= '''
    ************************* Инструмент Мнемонические слова 12/15/18/21/24 ************************* 
    *                                                                                    *
    *    1-СОБСТВЕННЫЕ СЛОВА в DEC и HEX с проверкой TX [требуется Интернет]                      *
    *    2-Сгенерированные СЛОВА в DEC и HEX с проверкой TX [требуется Интернет]                *
    *    Type 1-2 to Start                                                               *
    *                                                                                    *
    ************************* Инструмент Мнемонические слова 12/15/18/21/24 *************************
        '''
        startwords=int(input(promptword))
        if startwords == 1:
            MNEMONIC: str = input(' Введите свои собственные слова здесь = ')
            Lang = int(input(' Choose language 1.english, 2.french, 3.italian, 4.spanish, 5.chinese_simplified, 6.chinese_traditional, 7.japanese or 8.korean '))
            if Lang == 1:
                Lang1 = "english"
            elif Lang == 2:
                Lang1 = "french"
            elif Lang == 3:
                Lang1 = "italian"
            elif Lang == 4:
                Lang1 = "spanish"
            elif Lang == 5:
                Lang1 = "chinese_simplified"
            elif Lang == 6:
                Lang1 = "chinese_traditional"
            elif Lang == 7:
                Lang1 = "japanese"
            elif Lang == 8:
                Lang1 = "korean"
            else:
                print("WRONG NUMBER!!! Starting with english")
                Lang1 = "english"
            PASSPHRASE: Optional[str] = None
            bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
            bip44_hdwallet.from_mnemonic(
                mnemonic=MNEMONIC, language=Lang1, passphrase=PASSPHRASE
            )
            bip44_hdwallet.clean_derivation()
            mnemonic_words = bip44_hdwallet.mnemonic()
            ethadd = bip44_hdwallet.address()
            HEX = bip44_hdwallet.private_key()
            dec = int(bip44_hdwallet.private_key(), 16)
            length = len(bin(dec))
            length -=2
            print('\nmnemonic_words  : ', mnemonic_words)
            print('\nPrivatekey (dec): ', dec, '  bits ', length, '\nPrivatekey (hex): ', HEX)
            blocs=requests.get("https://api.ethplorer.io/getAddressInfo/" + ethadd +apikeys)
            ress = blocs.json()
            address = dict(ress)['address']
            countTxs = dict(ress)['countTxs']
            ETHbalance = dict(ress)['ETH']['balance']
            print(f''' 
             |==============================================|=======|=========|
             | Эфириум (ETH) Адрес                       |No. TXS|Остаток средств  |
             |==============================================|=======|=========|
             | ''', address, ''' | ''', countTxs, '''   | ''', ETHbalance, '''    | ''')
            time.sleep(3.0)

        if startwords == 2:
            print('Мнемоника 12/15/18/21/24 слов для адресного инструмента ETH')
            R = int(input('Введите количество мнемонических слов 12/15/18/21/24 : '))
            if R == 12:
                s1 = 128
            elif R == 15:
                s1 = 160
            elif R == 18:
                s1 = 192
            elif R == 21:
                s1 = 224
            elif R == 24:
                s1 = 256
            else:
                print("НЕПРАВИЛЬНЫЙ НОМЕР!!! Начиная с 24 слов")
                s1 = 256
            Lang = int(input(' Choose language 1.english, 2.french, 3.italian, 4.spanish, 5.chinese_simplified, 6.chinese_traditional, 7.japanese or 8.korean '))
            if Lang == 1:
                Lang1 = "english"
            elif Lang == 2:
                Lang1 = "french"
            elif Lang == 3:
                Lang1 = "italian"
            elif Lang == 4:
                Lang1 = "spanish"
            elif Lang == 5:
                Lang1 = "chinese_simplified"
            elif Lang == 6:
                Lang1 = "chinese_traditional"
            elif Lang == 7:
                Lang1 = "japanese"
            elif Lang == 8:
                Lang1 = "korean"
            else:
                print("WRONG NUMBER!!! Starting with english")
                Lang1 = "english"
            MNEMONIC: str = generate_mnemonic(language=Lang1, strength=s1)
            PASSPHRASE: Optional[str] = None
            bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
            bip44_hdwallet.from_mnemonic(
                mnemonic=MNEMONIC, language=Lang1, passphrase=PASSPHRASE
            )
            bip44_hdwallet.clean_derivation()
            mnemonic_words = bip44_hdwallet.mnemonic()
            ethadd = bip44_hdwallet.address()
            HEX = bip44_hdwallet.private_key()
            dec = int(bip44_hdwallet.private_key(), 16)
            length = len(bin(dec))
            length -=2
            print('\nmnemonic_words  : ', mnemonic_words)
            print('\nPrivatekey (dec): ', dec, '  bits ', length, '\nPrivatekey (hex): ', HEX)
            blocs=requests.get("https://api.ethplorer.io/getAddressInfo/" + ethadd +apikeys)
            ress = blocs.json()
            address = dict(ress)['address']
            countTxs = dict(ress)['countTxs']
            ETHbalance = dict(ress)['ETH']['balance']
            print(f''' 
             |==============================================|=======|=========|
             | Эфириум (ETH) Адрес                       |No. TXS|Остаток средств  |
             |==============================================|=======|=========|
             | ''', address, ''' | ''', countTxs, '''   | ''', ETHbalance, '''    | ''')
            time.sleep(3.0)
        
    elif start ==28:
        filename ='eth.txt'
        with open(filename) as f:
            line_count = 0
            for line in f:
                line != "\n"
                line_count += 1
        eth_list = [line.split()[0].lower() for line in open(filename,'r')]
        eth_list = set(eth_list)
        print('Мнемоника 12/15/18/21/24 слов для адресного инструмента ETH')
        R = int(input('Введите количество мнемонических слов 12/15/18/21/24 : '))
        if R == 12:
            s1 = 128
        elif R == 15:
            s1 = 160
        elif R == 18:
            s1 = 192
        elif R == 21:
            s1 = 224
        elif R == 24:
            s1 = 256
        else:
            print("НЕПРАВИЛЬНЫЙ НОМЕР!!! Начиная с 24 слов")
            s1 = 256
        divs = int(input("Сколько путей вывода? m/44'/60'/0'/0/0/ to m/44'/60'/0'/0/???? -> "))
        Lang = int(input(' Choose language 1.english, 2.french, 3.italian, 4.spanish, 5.chinese_simplified, 6.chinese_traditional, 7.japanese or 8.korean '))
        if Lang == 1:
            Lang1 = "english"
        elif Lang == 2:
            Lang1 = "french"
        elif Lang == 3:
            Lang1 = "italian"
        elif Lang == 4:
            Lang1 = "spanish"
        elif Lang == 5:
            Lang1 = "chinese_simplified"
        elif Lang == 6:
            Lang1 = "chinese_traditional"
        elif Lang == 7:
            Lang1 = "japanese"
        elif Lang == 8:
            Lang1 = "korean"
        else:
            print("WRONG NUMBER!!! Starting with english")
            Lang1 = "english"
        display = int(input('1=Full Display (Slower) 2=Slient Mode (Faster) : '))
        while True:
            data=[]
            count += 1
            total += divs
            MNEMONIC: str = generate_mnemonic(language=Lang1, strength=s1)
            PASSPHRASE: Optional[str] = None
            bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
            bip44_hdwallet.from_mnemonic(
                mnemonic=MNEMONIC, language=Lang1, passphrase=PASSPHRASE
            )
            bip44_hdwallet.clean_derivation()
            mnemonic_words = bip44_hdwallet.mnemonic()
            data_eth()
            for target_wallet in data:
                address = target_wallet['address'].lower()
                if address in eth_list:
                    print('\nMatch Found')
                    print('\nmnemonic_words  : ', mnemonic_words)
                    print('Derivation Path : ', target_wallet['path'], ' : ETH Address : ', target_wallet['address'])
                    print('Privatekey  : ', target_wallet['privatekey'])
                    print('Privatekey DEC : ', target_wallet['privatedec'])
                    with open("winner.txt", "a") as f:
                        f.write(f"""\nMnemonic_words:  {mnemonic_words}
                        Derivation Path:  {target_wallet['path']}
                        Privatekey : {target_wallet['privatekey']}
                        Public Address ETH:  {target_wallet['address']}""")
            else:
                if display == 1:
                    print(' [' + str(count) + '] ------------------------')
                    print('Total Checked [' + str(total) + '] ')
                    print('\nmnemonic_words  : ', mnemonic_words)
                    for bad_wallet in data:
                        print('Derivation Path : ', bad_wallet['path'], ' : ETH Address : ', bad_wallet['address'])
                        print('Privatekey : ', bad_wallet['privatekey'])
                        print('Privatekey DEC : ', bad_wallet['privatedec'])
                if display == 2:
                    print(' [' + str(count) + '] ------', 'Total Checked [' + str(total) + '] ', end='\r')
    elif start ==29:
        print('Мнемоника 12/15/18/21/24 слов для адресного инструмента ETH')
        R = int(input('Введите количество мнемонических слов 12/15/18/21/24 : '))
        if R == 12:
            s1 = 128
        elif R == 15:
            s1 = 160
        elif R == 18:
            s1 = 192
        elif R == 21:
            s1 = 224
        elif R == 24:
            s1 = 256
        else:
            print("WRONG NUMBER!!! Starting with 24 Words")
            s1 = 256
        divs = int(input("Сколько путей вывода? m/44'/60'/0'/0/0/ to m/44'/60'/0'/0/???? -> "))
        Lang = int(input(' Choose language 1.english, 2.french, 3.italian, 4.spanish, 5.chinese_simplified, 6.chinese_traditional, 7.japanese or 8.korean '))
        if Lang == 1:
            Lang1 = "english"
        elif Lang == 2:
            Lang1 = "french"
        elif Lang == 3:
            Lang1 = "italian"
        elif Lang == 4:
            Lang1 = "spanish"
        elif Lang == 5:
            Lang1 = "chinese_simplified"
        elif Lang == 6:
            Lang1 = "chinese_traditional"
        elif Lang == 7:
            Lang1 = "japanese"
        elif Lang == 8:
            Lang1 = "korean"
        else:
            print("WRONG NUMBER!!! Starting with english")
            Lang1 = "english"
        display = int(input('1=Full Display (Slower) 2=Slient Mode (Faster) : '))
        while True:
            data=[]
            count += 1
            total += divs
            MNEMONIC: str = generate_mnemonic(language=Lang1, strength=s1)
            PASSPHRASE: Optional[str] = None
            bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
            bip44_hdwallet.from_mnemonic(
                mnemonic=MNEMONIC, language=Lang1, passphrase=PASSPHRASE
            )
            bip44_hdwallet.clean_derivation()
            mnemonic_words = bip44_hdwallet.mnemonic()
            data_eth()
            for target_wallet in data:
                ethadd = target_wallet['address']
                blocs=requests.get("https://api.ethplorer.io/getAddressInfo/" + ethadd +apikeys)
                ress = blocs.json()
                address = dict(ress)['address']
                countTxs = dict(ress)['countTxs']
                ETHbalance = dict(ress)['ETH']['balance']
                print(f''' 
                 |==============================================|=======|=========|
                 | Эфириум (ETH) Адрес                       |No. TXS|Остаток средств  |
                 |==============================================|=======|=========|
                 | ''', address, ''' | ''', countTxs, '''   | ''', ETHbalance, '''     | ''')
                time.sleep(0.20)
                if countTxs > 0:
                    with open("winner.txt", "a") as f:
                        f.write(f"""\nMnemonic_words:  {mnemonic_words}
                        Derivation Path:  {target_wallet['path']}
                        Privatekey : {target_wallet['privatekey']}
                        Public Address ETH:  {target_wallet['address']}""")
    
    elif start ==30:
        promptdoge= '''
    *********************** Инструмент проверки баланса последовательности Doge *****************************
    *                                                                                                       *
    *    ** Последовательность Dogecoin Инструмент проверки баланса Требуется интернет                      *
    *    ** ЛЮБЫЕ СОЗДАННЫЕ СООТВЕТСТВУЮЩИЕ БАЛАНТЫ БУДУТ СОХРАНЯТЬСЯ В (winner.txt)                        *
    *                                                                                                       *
    *********************** Инструмент проверки баланса последовательности Doge *****************************
        '''
        print(promptdoge)
        time.sleep(1)
        print("Начать поиск... Выберите диапазон для начала (Мин=0 Макс=256)")
        x=int(input("Начальный диапазон в битах 0 или 255 (макс. 255) -> "))
        a = 2**x
        y=int(input("Диапазон останова Макс. в битах 256 Макс. (StopNumber)-> "))
        b = 2**y
        m=int(input("Magnitude Jump Stride -> "))
        print("Starting search... Please Wait min range: " + str(a))
        print("️Max range: " + str(b))
        P = a
        while P<b:
            P+=m
            ran= P
            seed = int(ran)
            HEX = "%064x" % ran
            dogeaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, True, seed) #DOGE
            dogeuaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, False, seed) #DOGE
            balanceDoge = get_doge(dogeaddr)
            balanceDoge1 = get_doge(dogeuaddr)
            time.sleep(1.0) #Can be removed
            if float(balanceDoge) > float(ammount) or float(balanceDoge1) < ammount:
                print('\n Match Found')
                print('\nPrivatekey (dec): ', seed,'\nPrivatekey (hex): ', HEX, '\nPublic Address DOGE Uncompressed : ', dogeuaddr, '  Balance = ',  str(balanceDoge1), '\nPublic Address DOGE Compressed   : ', dogeaddr, '  Balance = ',  str(balanceDoge))
                f=open("winner.txt","a")
                f.write('\nPrivatekey (dec): ' + str(seed))
                f.write('\nPrivatekey (hex): ' + HEX)
                f.write('\nPublic Address DOGE Compressed: ' + dogeaddr  + ' : ' +  str(balanceDoge))
                f.write('\nPublic Address DOGE Uncompressed: ' + dogeuaddr  + ' : ' +  str(balanceDoge1))
                f.write('\n============================================================')
                f.close()
            else:
                print('\nPrivatekey (dec): ', seed,'\nPrivatekey (hex): ', HEX, '\nPublic Address DOGE Uncompressed : ', dogeuaddr, '  Balance = ',  str(balanceDoge1), '\nPublic Address DOGE Compressed   : ', dogeaddr, '  Balance = ',  str(balanceDoge))
    
    elif start ==31:
        promptdoger= '''
    *********************** Инструмент случайной проверки баланса Doge *****************************
    *                                                                                              *
    *    ** Инструмент случайной проверки баланса Dogecoin требует интернета                       *
    *    ** ЮБЫЕ СОЗДАННЫЕ СООТВЕТСТВУЮЩИЕ БАЛАНТЫ БУДУТ СОХРАНЯТЬСЯ В (winner.txt)                *
    *                                                                                              *
    *********************** Инструмент случайной проверки баланса Doge *****************************
        '''
        print(promptdoger)
        time.sleep(1)
        print("Начать поиск... Выберите диапазон для начала (Мин=0 Макс=256)")
        x=int(input("Начальный диапазон в битах 0 или 255 (макс. 255) -> "))
        start = 2**x
        y=int(input("Диапазон останова Макс. в битах 256 Макс. (StopNumber)-> "))
        stop = 2**y
        print("Начинается поиск... Пожалуйста, подождите мин. диапазон: " + str(start))
        print("️Максимальный диапазон: " + str(stop))
        while True:
            ran=random.randrange(start,stop)
            seed = int(ran)
            HEX = "%064x" % ran
            dogeaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, True, seed) #DOGE
            dogeuaddr = ice.privatekey_to_coinaddress(ice.COIN_DOGE, 0, False, seed) #DOGE
            balanceDoge = get_doge(dogeaddr)
            balanceDoge1 = get_doge(dogeuaddr)
            time.sleep(1.0) #Can be removed
            if float(balanceDoge) > float(ammount) or float(balanceDoge1) < ammount:
                print('\n Match Found')
                print('\nPrivatekey (dec): ', seed,'\nPrivatekey (hex): ', HEX, '\nPublic Address DOGE Uncompressed : ', dogeuaddr, '  Balance = ',  str(balanceDoge1), '\nPublic Address DOGE Compressed   : ', dogeaddr, '  Balance = ',  str(balanceDoge))
                f=open("winner.txt","a")
                f.write('\nPrivatekey (dec): ' + str(seed))
                f.write('\nPrivatekey (hex): ' + HEX)
                f.write('\nPublic Address DOGE Compressed: ' + dogeaddr  + ' : ' +  str(balanceDoge))
                f.write('\nPublic Address DOGE Uncompressed: ' + dogeuaddr  + ' : ' +  str(balanceDoge1))
                f.write('\n============================================================')
                f.close()
            else:
                print('\nPrivatekey (dec): ', seed,'\nPrivatekey (hex): ', HEX, '\nPublic Address DOGE Uncompressed : ', dogeuaddr, '  Balance = ',  str(balanceDoge1), '\nPublic Address DOGE Compressed   : ', dogeaddr, '  Balance = ',  str(balanceDoge))

    else:
        print("НЕПРАВИЛЬНЫЙ НОМЕР!!! ДОЛЖЕН ВЫБРАТЬ 1 - 31 ")
