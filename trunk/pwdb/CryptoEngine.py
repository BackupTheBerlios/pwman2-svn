"""Encryption Module used by PwmanDatabase

Supports AES, ARC2, Blowfish, CAST, DES, DES3, IDEA, RC5.

Usage:
import pwdb.CryptoEngine as CryptoEngine

class myCallback(CryptoEngine.Callback):
    def execute(self):
        return "mykey"

params = {'encryptionAlgorithm': 'AES',
          'encryptionCallback': callbackFunction}

CryptoEngine.init(params)

crypto = CryptoEngine.get()
ciphertext = crypto.encrypt("plaintext")
plaintext = cyypto.decrypt(ciphertext)

"""
from Crypto.Cipher import *
import cPickle,base64,time

_instance = None

# Use this to tell if crypto is successful or not
_TAG = "PWMANCRYPTO"

def init(params):
    """
    Initialise an instance of CryptoEngine. Must be called before get().
    """
    global _instance
    _instance = CryptoEngine(params)

def get():
    """
    get() -> CryptoEngine
    Return an instance of CryptoEngine.
    If no instance is found, a CryptoException is raised.
    """
    if (_instance == None):
        raise CryptoException("No instance found, init not called?")
    return _instance

class CryptoException(Exception):
    """Generic Crypto Exception."""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "CryptoException: " + self.message

class CryptoUnsupportedException(CryptoException):
    """Unsupported feature requested."""
    def __str__(self):
        return "CryptoUnsupportedException: " +self.message

class CryptoBadKeyException(CryptoException):
    """Encryption key is incorrect."""
    def __str__(self):
        return "CryptoBadKeyException: " + self.message

class Callback:
    """Callback interface. Callback classes must implement this."""
    def execute(self):
        """Return key"""
        pass
    
class CryptoEngine:
    """Cryptographic Engine"""
    _timeoutCount = 0
    def __init__(self, params):
        """Initialise the Cryptographic Engine

        params is a dictionary. Valid keys are:
        encryptionAlgorithm: Which cipher to use
        encryptionCallback:  Callback class. 
        encryptionTimeout:   Time after which key will be forgotten.
                             Default is -1 (disabled).
        """
        
        self._algo = params['encryptionAlgorithm']
        self._callback = params['encryptionCallback']
        try:
            self._timeout = params['encryptionTimeout']
        except KeyError:
            self._timeout = -1
        self._cipher = None
    
    def encrypt(self, obj):
        """
        encrypt(obj) -> ciphertext
        Encrypt obj and return its ciphertext. obj must be a picklable class.
        Can raise a CryptoException and CryptoUnsupportedException"""
        cipher = self._getCipher()
        plaintext = cPickle.dumps(obj)
        plaintext = self._padData(plaintext, cipher.block_size)
        ciphertext = cipher.encrypt(plaintext)
        return base64.b64encode(ciphertext)
        
    def decrypt(self, ciphertext):
        """
        decrypt(ciphertext) -> obj
        Decrypt ciphertext and returns the obj that was encrypted.
        If key is bad, a CryptoBadKeyException is raised
        Can also raise a CryptoException and CryptoUnsupportedException"""
        cipher = self._getCipher()
        b64u_ciphertext = base64.b64decode(ciphertext)
        plaintext = cipher.decrypt(b64u_ciphertext)
        if (plaintext.startswith(_TAG)):
            plaintext = plaintext[len(_TAG):]
        else:
            raise CryptoBadKeyException("Error decrypting, bad key")
        return cPickle.loads(plaintext)

    def _getCipher(self):
        if (self._cipher != None and self._timeout != -1
            and (time.time() - CryptoEngine._timeoutCount) < self._timeout):
            return self._cipher
        key = self._callback.execute()
        if (self._algo == "AES"):
            key = self._padKey(key, [16, 24, 32])
            self._cipher = AES.new(key, AES.MODE_ECB)
        elif (self._algo == 'ARC2'):
            self._cipher = ARC2.new(key, ARC2.MODE_ECB)
        elif (self._algo == 'ARC4'):
            raise CryptoUnsupportedException("ARC4 is currently unsupported")
        elif (self._algo == 'Blowfish'):
            self._cipher = Blowfish.new(key, Blowfish.MODE_ECB)
        elif (self._algo == 'CAST'):
            self._cipher = CAST.new(key, CAST.MODE_ECB)
        elif (self._algo == 'DES'):
            key = self._padKey(key, [8])
            self._cipher = DES.new(key, DES.MODE_ECB)
        elif (self._algo == 'DES3'):
            key = self._padKey(key, [16, 24])
            self._cipher = DES3.new(key, DES3.MODE_ECB)
        elif (self._algo == 'IDEA'):
            key = self._padKey(key, [16])
            self._cipher = IDEA.new(key, IDEA.MODE_ECB)
        elif (self._algo == 'RC5'):
            self._cipher = RC5.new(key, RC5.MODE_ECB)
        elif (self._algo == 'XOR'):
            raise CryptoUnsupportedException("XOR is currently unsupported")
        else:
            raise CryptoException("Invalid algorithm specified")        
        CryptoEngine._timeoutCount = time.time()
        
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
        data = _TAG + data
        numblocks = (len(data)/blocksize) + 1
        newdatasize = blocksize*numblocks
        return data.ljust(newdatasize)
        

