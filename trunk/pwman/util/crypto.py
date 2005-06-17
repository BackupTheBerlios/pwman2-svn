"""Encryption Module used by PwmanDatabase

Supports AES, ARC2, Blowfish, CAST, DES, DES3, IDEA, RC5.

Usage:
import pwman.util.crypto.CryptoEngine as CryptoEngine

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
import cPickle
import time

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
    _timeoutcount = 0
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
            if params.has_key('Encryption'):
                CryptoEngine._instance = CryptoEngine(params)
            else:
                CryptoEngine._instance = DummyCryptoEngine(params)
        return CryptoEngine._instance
    
    def __init__(self, params):
        """Initialise the Cryptographic Engine

        params is a dictionary. Valid keys are:
        algorithm: Which cipher to use
        callback:  Callback class.
        keycrypted: This should be set by the database layer.
        timeout:   Time after which key will be forgotten.
                             Default is -1 (disabled).
        """
        encparams = None
        try:
            encparams =  params['Encryption']
            self._algo = encparams['algorithm']
            self._callback = encparams['callback']
        except KeyError, e:
            raise CryptoException("Parameters missing [%s]" % (e) )
        
        try:
            self._keycrypted = encparams['keycrypted']
        except KeyError:
            self._keycrypted = None
            
        try:
            self._timeout = encparams['timeout']
        except KeyError:
            self._timeout = -1
        self._cipher = None
    
    def encrypt(self, obj):
        """
        encrypt(obj) -> ciphertext
        Encrypt obj and return its ciphertext. obj must be a picklable class.
        Can raise a CryptoException and CryptoUnsupportedException"""
        cipher = self._getcipher()
        plaintext = self._preparedata(obj, cipher.block_size)
        ciphertext = cipher.encrypt(plaintext)
        return ciphertext.encode('base64')
        
    def decrypt(self, ciphertext):
        """
        decrypt(ciphertext) -> obj
        Decrypt ciphertext and returns the obj that was encrypted.
        If key is bad, a CryptoBadKeyException is raised
        Can also raise a CryptoException and CryptoUnsupportedException"""
        cipher = self._getcipher()
        ciphertext = ciphertext.decode('base64')
        plaintext = cipher.decrypt(ciphertext)
        return self._retrievedata(plaintext)

    def set_cryptedkey(self, key):
        self._keycrypted = key

    def get_cryptedkey(self):
        return self._keycrypted
    
    def changepassword(self):
        """
        Creates a new key. The key itself is actually stored in
        the database in crypted form. This key is encrypted using the
        password that the user provides. This makes it easy to change the
        password for the database.
        If oldKeyCrypted is none, then a new password is generated."""
        if (self._keycrypted == None):
            # Generate a new key, 32 bits in length, if that's
            # too long for the Cipher, _getCipherReal will sort it out
            random = RandomPool()
            key = random.get_bytes(32).encode('base64')
        else:
            password = self._callback.execute("Please enter your current password")
            cipher = self._getcipher_real(password, self._algo)
            plainkey = cipher.decrypt(self._keycrypted.decode('base64'))
            key = self._retrievedata(plainkey)
        newpassword1 = self._callback.execute("Please enter your new password");
        newpassword2 = self._callback.execute("Please enter your new password again");
        if (newpassword1 != newpassword2):
            raise CryptoException("Passwords do not match")
        newcipher = self._getcipher_real(newpassword1, self._algo)
        self._keycrypted = newcipher.encrypt(self._preparedata(key, newcipher.block_size)).encode('base64')
        
        # we also want to create the cipher if there isn't one already
        # so this CryptoEngine can be used from now on
        if (self._cipher == None):
            self._cipher = self._getcipher_real(key.decode('base64'), self._algo)
            CryptoEngine._timeoutcount = time.time()        
            
        return self._keycrypted

    def _getcipher(self):
        if (self._cipher != None
            and (self._timeout == -1
                 or (time.time() - CryptoEngine._timeoutcount) < self._timeout)):
            return self._cipher
            
        if (self._keycrypted == None):
            raise CryptoNoKeyException("Encryption key has not been generated")
        
        password = self._callback.execute("Please enter your password")
        tmpcipher = self._getcipher_real(password, self._algo)
        plainkey = tmpcipher.decrypt(self._keycrypted.decode('base64'))
        key = self._retrievedata(plainkey)
        
        self._cipher = self._getcipher_real(key.decode('base64'), self._algo)

        CryptoEngine._timeoutcount = time.time()
        return self._cipher
        

    def _getcipher_real(self, key, algo):
        if (algo == "AES"):
            key = self._padkey(key, [16, 24, 32])
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
            self._padkey(key, [8])
            cipher = DES.new(key, DES.MODE_ECB)
        elif (algo == 'DES3'):
            key = self._padkey(key, [16, 24])
            cipher = DES3.new(key, DES3.MODE_ECB)
        elif (algo == 'IDEA'):
            key = self._padkey(key, [16])
            cipher = IDEA.new(key, IDEA.MODE_ECB)
        elif (algo == 'RC5'):
            cipher = RC5.new(key, RC5.MODE_ECB)
        elif (algo == 'XOR'):
            raise CryptoUnsupportedException("XOR is currently unsupported")
        else:
            raise CryptoException("Invalid algorithm specified")        
        return cipher

    def _padkey(self, key, acceptable_lengths):
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

    def _preparedata(self, obj, blocksize):
        plaintext = cPickle.dumps(obj)
        plaintext = _TAG + plaintext
        numblocks = (len(plaintext)/blocksize) + 1
        newdatasize = blocksize*numblocks
        return plaintext.ljust(newdatasize)

    def _retrievedata(self, plaintext):
        if (plaintext.startswith(_TAG)):
            plaintext = plaintext[len(_TAG):]
        else:
            raise CryptoBadKeyException("Error decrypting, bad key")
        return cPickle.loads(plaintext)


class DummyCryptoEngine(CryptoEngine):
    """Dummy CryptoEngine used when database doesn't ask for encryption.
    Only for testing and debugging the DB drivers really."""
    def __init__(self, params):
        pass
    
    def encrypt(self, obj):
        """Return the object pickled."""
        return cPickle.dumps(obj)

    def decrypt(self, ciphertext):
        """Unpickle the object."""
        return cPickle.loads(str(ciphertext))
