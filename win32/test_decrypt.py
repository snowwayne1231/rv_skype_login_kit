import sys, os, re, time, getopt
import win32gui
import win32api
import win32con
from Crypto.Cipher import AES
# from binascii import hexlify, unhexlify
import hashlib

BS = AES.block_size

def padding_pkcs5(value):
    return str.encode(value + (BS - len(value) % BS) * chr(BS - len(value) % BS))

def aes_ecb_encrypt(key, value):
    # cryptor = AES.new(bytes.fromhex(key), AES.MODE_ECB)
    cryptor = AES.new(key, AES.MODE_ECB)
    padding_value = padding_pkcs5(value)    # padding content with pkcs5
    ciphertext = cryptor.encrypt(padding_value)
    return ''.join(['%02x' % i for i in ciphertext])

def aes_ecb_decrypt(key, value):
    # key = bytes.fromhex(key)
    cryptor = AES.new(key, AES.MODE_ECB)
    ciphertext = cryptor.decrypt(bytes.fromhex(value))
    return ciphertext.decode('utf-8')


aes_key = b't1tSr6B1RGHvujeW'
split_character = ' | '

# expect_result = 'c1ee1f3f2d74e02706be9af78aa79ba4'.upper()
# aes128string = aes_ecb_encrypt(aes_key, 'ABcdefGHIJ123456789KlmnopQ')
# decrypted = aes_ecb_decrypt(aes_key, '62ea45d3499cf41e424373b145ce44dc0033609d0e989338807656ef6abcc96f')

def handle_skype():

    acc = ''
    pwd = ''
    code = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:p:c:", [])
        for o, a in opts:
            if o in ("-a", "--acc"):
                acc = a
            elif o in ("-p", "--pwd"):
                pwd = a
            elif o in ("-c", '--code'):
                _code = a
                _ap = aes_ecb_decrypt(aes_key, _code)
                _ap_list = _ap.split(split_character, 1)
                if len(_ap_list) == 2:
                    print(_ap)
                    acc = _ap_list[0]
                    pwd = _ap_list[1]
                else:
                    raise Exception("Wrong of Split Account and Password")

        if acc:
            _result = aes_ecb_encrypt(aes_key, '{} | {}'.format(acc, pwd))
            print('_result: ', _result)
    
        
    except getopt.GetoptError as err:
        print(err)



if __name__ == '__main__':
        
    try:

        print('Start Skype Test.')
        handle_skype()

        
    except KeyboardInterrupt as ke:
        print('stop.')
    except Exception as ee:
        print(ee)

    