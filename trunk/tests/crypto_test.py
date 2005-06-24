from pwman.util.crypto import CryptoEngine, Callback, CryptoNoKeyException
import getpass
import sys

class foo:
    def bar(self):
        print "woo yay!"

class callback(Callback):
    def execute(self, question):
        return getpass.getpass(question + ":")

algo = "AES"

params = {'Encryption': { 'algorithm': algo,
                          'callback': callback() }
          }

crypto = CryptoEngine.get(params)

x = foo()
x.bar()

key = None
ciphertext = None

try:
    ciphertext = crypto.encrypt(x)
except CryptoNoKeyException, e:
    key = crypto.changepassword()
    ciphertext = crypto.encrypt(x)

print 'Change the password'
key = crypto.changepassword()

if (key != None):
    print "Key: %s" % (key)
print "CipherText: %s" % (ciphertext)

y = crypto.decrypt(ciphertext)
y.bar()
