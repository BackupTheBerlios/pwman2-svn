import pwdb.CryptoEngine

class foo:
    def bar(self):
        print "woo yay!"

def callback():
    return "foobar"

params = {'encryptionAlgorithm': 'AES',
          'encryptionCallback': callback}

pwdb.CryptoEngine.init(params)

crypto = pwdb.CryptoEngine.get()

x = foo()
x.bar()

str = crypto.encrypt(x)

print str

y = crypto.decrypt(str)

y.bar()
