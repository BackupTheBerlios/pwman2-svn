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

db.close()
