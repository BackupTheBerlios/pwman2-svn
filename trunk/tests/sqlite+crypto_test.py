#!/usr/bin/python

from pwman.db.database import DatabaseException
import pwman.db.factory
import getpass
from pwman.util.crypto import CryptoBadKeyException, CryptoPasswordMismatchException

class callback(pwman.util.crypto.Callback):
    def execute(self, question):
        return getpass.getpass(question + '> ')

params = {'Database' : {'type': 'SQLite', 'filename':'/tmp/test.db'},
          'Encryption' : {'algorithm': 'AES', 'callback': callback() }}


def printlist(node, prefix=""):
    nodelist = db.list(node.__str__())
    for node in nodelist:
        print prefix+"Name: " + node.get_name() + "\tType: " + node.get_type()
        if (node.get_type() == pwman.db.database.LIST):
            printlist(node, prefix+"\t")

db = pwman.db.factory.create(params)
try:
    db.open()
except CryptoPasswordMismatchException, e:
    print "Passwords do not match"
except CryptoBadKeyException, e:
    print "Bad password"

try:
    try:
        db.put("Foobar", "Foobar1Data")
        db.put("Foobar1", "Foobar2Data")
        db.put("Foobar2", "Foobar3Data")
        db.put("Foobar3", "Foobar4Data")
        db.put("Foobar4", "Foobar5Data")
        db.put("Foobar5", "Foobar6Data")
        
        data = db.get("Foobar")
        print "Data: " + data.__str__()
        data = db.get("Foobar4")
        print "Data: " + data.__str__()
        data = db.get("Foobar2")
        print "Data: " + data.__str__()
        
        db.delete("Foobar1")
        db.delete("Foobar3")
        db.delete("FoobarX")
        
        db.makelist("FoobarList1")
        db.makelist("FoobarList2")
        db.makelist("FoobarList3")
        
        db.changelist("FoobarList1")
        db.put("FoobarSub", "FoobarSubData")
        db.put("FoobarSub2", "FoobarSub2Data")
        db.put("../FoobarSub", "Foobar")
        db.makelist("SubSublist")
        db.changelist("..")
        db.changelist("/FoobarList1/SubSublist")
        db.put("FoobarSub3", "FoobarSubData")
        db.put("FoobarSub4", "FoobarSub2Data")
        db.copy("FoobarSub4", "..")
        db.copy("FoobarSub4", "/")
        db.copy("/", "/FoobarList3/root")
        db.copy("/FoobarList1", "/FoobarList3")
        
        db.move("/FoobarList3", "/RenamedFoobarlist3")
        
        try:
            db.changepassword()
        except CryptoPasswordMismatchException, e:
            print "Passwords do not match"
        except CryptoBadKeyException, e:
            print "Bad password entered, cannot change password"
            
            db.removelist("/FoobarList2")
            
            printlist("/")
    except CryptoBadKeyException, e:
        print "Bad password entered, cannot change password"
finally:
    db.close()
