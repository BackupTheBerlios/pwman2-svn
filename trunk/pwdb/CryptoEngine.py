from Crypto.Cipher import *
import cPickle
import base64

_instance = None

# Use this to tell if crypto is successful or not
TAG = "PWMANCRYPTO"

def init(params):
    global _instance
    _instance = _CryptoEngine(params)

def get():
    if (_instance == None):
        raise CryptoException("No instance found, init not called?")
    return _instance

class CryptoException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "CryptoException: " + self.message

class CryptoTimeoutException(CryptoException):
    def __str__(self):
        return "CryptoTimeoutException: " + self.message

class _CryptoEngine:
    def __init__(self, params):
        self._algo = params['encryptionAlgorithm']
        self._callback = params['encryptionCallback']
        self._cipher = None
##         if (self._algo == 'AES'):
##             self._cipher = AES.new(""
##         elif (self._algo == 'ARC2'):
##             pass
##         elif (self._algo == 'ARC4'):
##             pass
##         elif (self._algo == 'Blowfish'):
##             pass
##         elif (self._algo == 'CAST'):
##             pass
##         elif (self._algo == 'DES'):
##             pass
##         elif (self._algo == 'DES3'):
##             pass
##         elif (self._algo == 'IDEA'):
##             pass
##         elif (self._algo == 'RC5'):
##             pass
##         elif (self._algo == 'XOR'):
##             pass
##         else:
##             raise CryptoException("Invalid algorithm specified")        
    
    def encrypt(self, obj):
        cipher = self._getCipher()
        plaintext = cPickle.dumps(obj)
        plaintext = self._padData(plaintext, cipher.block_size)
        ciphertext = cipher.encrypt(plaintext)
        return base64.b64encode(ciphertext)
        
    def decrypt(self, b64_ciphertext):
        cipher = self._getCipher()
        ciphertext = base64.b64decode(b64_ciphertext)
        plaintext = cipher.decrypt(ciphertext)
        if (plaintext.startswith(TAG)):
            plaintext = plaintext[len(TAG):]
        else:
            raise CryptoException("Error decrypting, bad key")
        return cPickle.loads(plaintext)

    def _getCipher(self):
        if (self._cipher != None):
            return self._cipher
        key = self._callback()
        if (self._algo == "AES"):
            key = self._padKey(key, [16, 24, 32])
            self._cipher = AES.new(key, AES.MODE_ECB)
        return self._cipher

    def _padKey(self, key, acceptable_lengths):
        maxlen = max(acceptable_lengths)
        keylen = len(key)
        if (keylen > maxlen):
            return key[0:maxlen]
        acceptable_lengths.sort()
        acceptable_lengths.reverse()
        newkeylen = None
        for i in acceptable_lengths:
            if (i < keylen):
                break
            newkeylen = i
        return key.ljust(newkeylen)

    def _padData(self, data, blocksize):
        data = TAG + data
        numblocks = (len(data)/blocksize) + 1
        newdatasize = blocksize*numblocks
        return data.ljust(newdatasize)
        

