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
from Crypto.Util.randpool import RandomPool
import cPickle,base64,time

_instance = None

# Use this to tell if crypto is successful or not
_TAG = "PWMANCRYPTO"


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

class CryptoNoKeyException(CryptoException):
    """No key has been initalised."""
    def __str__(self):
        return "CryptoNoKeyException: " + self.message
    
class Callback:
    """Callback interface. Callback classes must implement this."""
    def execute(self, question):
        """Return key"""
        pass
    
class CryptoEngine:
    """Cryptographic Engine"""
    _timeoutCount = 0
    _instance = None

    @classmethod
    def get(cls, params=None):
        """
        get() -> CryptoEngine
        Return an instance of CryptoEngine.
        If no instance is found, a CryptoException is raised.
        """
        if (CryptoEngine._instance == None and params == None):
            raise CryptoException("No instance found, init not called?")
        elif (CryptoEngine._instance == None):
            CryptoEngine._instance = CryptoEngine(params)
        return CryptoEngine._instance
    
    def __init__(self, params):
        """Initialise the Cryptographic Engine

        params is a dictionary. Valid keys are:
        encryptionAlgorithm: Which cipher to use
        encryptionCallback:  Callback class.
        encryptionKeyCrypted: This should be set by the database layer.
        encryptionTimeout:   Time after which key will be forgotten.
                             Default is -1 (disabled).
        """

        try:
            self._algo = params['encryptionAlgorithm']
            self._callback = params['encryptionCallback']
        except KeyError, e:
            raise CryptoException("Parameters missing ["+str(e)+"]")
        
        try:
            self._keyCrypted = params['encryptionKeyCrypted']
        except KeyError:
            self._keyCrypted = None
            
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
        print ciphertext
        b64u_ciphertext = base64.b64decode(ciphertext)
        plaintext = cipher.decrypt(b64u_ciphertext)
        if (plaintext.startswith(_TAG)):
            plaintext = plaintext[len(_TAG):]
        else:
            raise CryptoBadKeyException("Error decrypting, bad key")
        return cPickle.loads(plaintext)

    def changePassword(self):
        """
        Creates a new key. The key itself is actually stored in
        the database in crypted form. This key is encrypted using the
        password that the user provides. This makes it easy to change the
        password for the database.
        If oldKeyCrypted is none, then a new password is generated."""
        if (self._keyCrypted == None):
            # Generate a new key, 32 bits in length, if that's
            # too long for the Cipher, _getCipherReal will sort it out
            random = RandomPool()
            key = random.get_bytes(32)
        else:
            password = self._callback.execute("Please enter your current password")
            cipher = self._getCipherReal(password, self._algo)
            key = cipher.decrypt(base64.b64decode(self._keyCrypted))
        newpassword1 = self._callback.execute("Please enter your new password");
        newpassword2 = self._callback.execute("Please enter your new password again");
        if (newpassword1 != newpassword2):
            raise CryptoException("Passwords do not match")
        newcipher = self._getCipherReal(newpassword1, self._algo)
        self._keyCrypted = base64.b64encode(newcipher.encrypt(key))

        # we also want to create the cipher if there isn't one already
        # so this CryptoEngine can be used from now on
        if (self._cipher == None):
            self._cipher = self._getCipherReal(key, self._algo)

        return self._keyCrypted

    def _getCipher(self):
        if (self._cipher != None and self._timeout != -1
            and (time.time() - CryptoEngine._timeoutCount) < self._timeout):
            return self._cipher

        if (self._keyCrypted == None):
            raise CryptoNoKeyException("Encryption key has not been generated")
        
        password = self._callback.execute("Please enter your password")
        tmpcipher = self._getCipherReal(password, self._algo)
        key = tmpcipher.decrypt(base64.b64decode(self._keyCrypted))
        
        self._cipher = self._getCipherReal(key, self._algo)
        return self._cipher
        

    def _getCipherReal(self, key, algo):
        if (algo == "AES"):
            key = self._padKey(key, [16, 24, 32])
            cipher = AES.new(key, AES.MODE_ECB)
        elif (algo == 'ARC2'):
            cipher = ARC2.new(key, ARC2.MODE_ECB)
        elif (algo == 'ARC4'):
            raise CryptoUnsupportedException("ARC4 is currently unsupported")
        elif (algo == 'Blowfish'):
            cipher = Blowfish.new(key, Blowfish.MODE_ECB)
        elif (algo == 'CAST'):
            cipher = CAST.new(key, CAST.MODE_ECB)
        elif (algo == 'DES'):
            self._padKey(key, [8])
            cipher = DES.new(key, DES.MODE_ECB)
        elif (algo == 'DES3'):
            key = self._padKey(key, [16, 24])
            cipher = DES3.new(key, DES3.MODE_ECB)
        elif (algo == 'IDEA'):
            key = self._padKey(key, [16])
            cipher = IDEA.new(key, IDEA.MODE_ECB)
        elif (algo == 'RC5'):
            cipher = RC5.new(key, RC5.MODE_ECB)
        elif (algo == 'XOR'):
            raise CryptoUnsupportedException("XOR is currently unsupported")
        else:
            raise CryptoException("Invalid algorithm specified")        
        CryptoEngine._timeoutCount = time.time()
        
        return cipher

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
        

