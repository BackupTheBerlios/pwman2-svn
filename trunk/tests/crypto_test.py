import pwdb.CryptoEngine

class foo:
    def bar(self):
        print "woo yay!"

class callback(pwdb.CryptoEngine.Callback):
    def execute(self):
        return "foobar!"

algo = "AES"

params = {'encryptionAlgorithm': algo,
          'encryptionCallback': callback()}

pwdb.CryptoEngine.init(params)

crypto = pwdb.CryptoEngine.get()

x = foo()
x.bar()

str = crypto.encrypt(x)

print str

y = crypto.decrypt(str)

y.bar()
