"""Factory to create Database instances

Usage:

import pwlib.db.DatabaseFactory as DBFactory

db = DBFactory.create(params)
db.open()
.....
"""
from pwman.db.Database import Database, DatabaseException
from pwman.db.drivers import SQLiteDatabase

def create(params):
    """
    create(params) -> Database
    Create a Database instance. `params` is a dictionary.
    The only key used by this function is 'type'. All others are passed
    on to the __init__ method of the Database instance.
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
        db = SQLiteDatabase.SQLiteDatabase(params)
    else:
        raise DatabaseException("Unknown database type specified")
    return db
