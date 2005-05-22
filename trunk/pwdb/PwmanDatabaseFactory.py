from pwdb.PwmanDatabase import PwmanDatabase, PwmanDatabaseException
from pwdb.drivers import SQLiteDatabase

def create(params):
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
