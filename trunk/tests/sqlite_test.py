#!/usr/bin/python

from pwdb.PwmanDatabase import PwmanDatabaseException
import pwdb.PwmanDatabaseFactory

params = {'type': 'SQLite', 'filename':'/tmp/test.db'}

db = pwdb.PwmanDatabaseFactory.create(params)
db.open()

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
#db.delete("FoobarX")

db.makeList("FoobarList1")
db.makeList("FoobarList2")
db.makeList("FoobarList3")

db.changeList("FoobarList1")
db.put("FoobarSub", "FoobarSubData")
db.put("FoobarSub2", "FoobarSub2Data")
db.put("../FoobarSub", "Foobar")
db.makeList("SubSublist")
db.changeList("..")
db.changeList("/FoobarList1/SubSublist")
db.put("FoobarSub3", "FoobarSubData")
db.put("FoobarSub4", "FoobarSub2Data")

db.removeList("/FoobarList2")

def printlist(node, prefix=""):
    nodelist = db.list(node.__str__())
    for node in nodelist:
        print prefix+"Name: " + node.getName() + "\tType: " + node.getType()
        if (node.getType() == pwdb.PwmanDatabase.LIST):
            printlist(node, prefix+"\t")

printlist("/")

db.close()
