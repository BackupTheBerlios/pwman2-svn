"""Factory to create PwmanDatabase instances

Usage:

import pwdb.PwmanDatabaseFactory as DBFactory

db = DBFactory.create(params)
db.open()
.....
"""
from pwdb.PwmanDatabase import PwmanDatabase, PwmanDatabaseException
from pwdb.drivers import SQLiteDatabase

def create(params):
    """
    create(params) -> PwmanDatabase
    Create a PwmanDatabase instance. `params` is a dictionary.
    The only key used by this function is 'type'. All others are passed
    on to the __init__ method of the PwmanDatabase instance.
    'type' can only be 'SQLite' at the moment
    """
    try:
        type = params['type']
    except KeyError:
        raise DatabaseException("No Database type specified")

    if type == "BerkeleyDB":
        pass
#        db = BerkeleyDatabase.BerkeleyDatabase(params)
    elif (type == "SQLite"):
        db = SQLiteDatabase.SQLitePwmanDatabase(params)
    else:
        raise DatabaseException("Unknown database type specified")
    return db
