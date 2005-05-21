import pwdb.Encryptor

_instance = None

def create(params):
    # dont bother with params at the moment
    if (_instance == None):
        _instance = Cryptor(params)
    return _instance
