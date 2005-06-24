"""SQLite PwmanDatabase implementation."""
from pwman.db.database import Database, DatabaseNode, DatabaseData, PW, LIST
from pwman.db.database import DatabaseException, DatabaseNoSuchNodeException,\
     DatabaseInvalidNodeException

from pysqlite2 import dbapi2 as sqlite

class SQLiteDatabase(Database):
    """SQLite Database implementation"""
    
    def __init__(self, params):
        """Initialise SQLitePwmanDatabase instance.
        Currently, the only SQLite specific param is 'filename'.
        This points to the database file which we should use."""
        Database.__init__(self, params)

        self._nodetable = 'NODES';
        self._datatable = 'DATA';
        self._keytable = 'KEYS';
        try:
            self._filename = params['Database']['filename']
        except KeyError, e:
            raise DatabaseException(
                "SQLite: missing parameter [%s]" % (e))

    def _open(self):
        try:
            self._con = sqlite.connect(self._filename)
            self._cur = self._con.cursor()
            self._checktables()
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (s))
        

    def _put(self, node, data):
        if (node.get_type() != PW):
            raise DatabaseInvalidNodeException("Not a password", node);

        if self._exists(node):
            id = self._get_nodeid(node)
        else:
            id = 0

        # create statements for adding the nodes to the database
        if id == 0:
            sql = "INSERT INTO "+self._nodetable \
                  +"(DATATYPE, NODENAME, PARENT)  VALUES(?, ?, ?)"
            values = (node.get_type(), node.get_cryptedname(),
                      self._get_parentid(node))
            try:
                self._cur.execute(sql, values)
            except sqlite.DatabaseError, e:
                raise DatabaseException(
                    "SQLite: Error creating node in db [%s]" % (e))

            sql = "INSERT INTO "+self._datatable+" VALUES(?, ?)"
            values = (self._cur.lastrowid, data.get_crypteddata());

            # insert the data into the database
            try:
                self._cur.execute(sql, values)
            except sqlite.DatabaseError, e:
                raise DatabaseException(
                    "SQLite: Error creating data in db [%s]" % (e))
        else:
            sql = "UPDATE "+self._datatable+" SET DATA=? WHERE ID=?"
            values = (data.get_crypteddata(), id)

            # update database with new data
            try:
                self._cur.execute(sql, values)
            except sqlite.DatabaseError, e:
                raise DatabaseException(
                    "SQLite: Error updating data in db [%s]" % (e))
        try:
            self._con.commit()
        except DatabaseError, e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error commiting data to db [%s]" % (e))

    def _get(self, node):
        if (node.get_type() != PW):
            raise DatabaseInvalidNodeException(
                "Not a password", node);

        sql = "SELECT DATA FROM "+self._nodetable \
              +" INNER JOIN "+self._datatable+" ON " \
              +self._nodetable+".ID = "+self._datatable+".ID " \
              +"WHERE DATATYPE = ? AND NODENAME = ? AND PARENT = ?"
        values = (node.get_type(), node.get_cryptedname(), \
                  self._get_parentid(node))
        try:
            self._cur.execute(sql, values)
            data = self._cur.fetchone()
            if (data == None):
                raise DatabaseNoSuchNodeException(
                    "Node does not exist in database", node)
            else:
                nodedata = DatabaseData(data[0], True)
                return nodedata
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error reading node from db [%s]" % (e))

    def _delete(self, node):
        if (node.get_type() != PW):
            raise DatabaseInvalidNodeException("Not a password");
        
        # get the id
        id = self._get_nodeid(node)

        # delete the node from the db
        try:
            self._cur.execute("DELETE FROM "+self._nodetable 
                              + " WHERE ID = ?", [id])
            self._cur.execute("DELETE FROM "+self._datatable
                              + " WHERE ID = ?", [id])
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error deleting from db [%s]" % (e))

        # commit the delete to the database
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error committing delete to db [%s]" % (e))
        
    def _close(self):
        self._cur.close()
        self._con.close()

    def _makelist(self, node):
        if (node.get_type() != LIST):
            raise DatabaseInvalidNodeException(
                "Not a list", node);
        sql = "INSERT INTO "+self._nodetable \
              +"(DATATYPE, NODENAME, PARENT)  VALUES(?, ?, ?)"
        values = (node.get_type(), node.get_cryptedname(),
                  self._get_parentid(node))
        try:
            self._cur.execute(sql, values)
            self._con.commit()
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error creating list [%s]" % (e))

    def _removelist(self, node):
        if (node.get_type() != LIST):
            raise DatabaseInvalidNodeException(
                "Not a list", node);
        
        # Find id of list to be deleted
        id = self._get_nodeid(node)

        # we delete the list from the database
        try:
            self._cur.execute("DELETE FROM "+self._nodetable
                              +" WHERE ID = ?", [id])
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error deleting list from database [%s]" % (e))

        # now commit the changes and bob's your uncle
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:
            self._con.rollback()
            raise DatabaseException(
                "SQLite: Error committing list removal [%s]" % (e))
        
    def _listempty(self, node):
        # Find id of list to be deleted
        id = self._get_nodeid(node)
        
        # check if list has children
        sql = "SELECT COUNT(*) FROM "+self._nodetable+" WHERE PARENT = ?"
        values = [id]
        try:
            self._cur.execute(sql, values)
            row = self._cur.fetchone()
            if (row[0] == 0):
                return True
            else:
                return False
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error checking for list children [%s]" % (e))
        
    def _list(self, node):
        try:
            id = self._get_nodeid(node)
            sql = "SELECT NODENAME, DATATYPE FROM "+self._nodetable \
                  +" WHERE PARENT = ?";
            self._cur.execute(sql, [id])
            
            nodes = []
            row = self._cur.fetchone()
            while (row != None):
                nodes.append(DatabaseNode(row[0], node, row[1], True))
                row = self._cur.fetchone()
            return nodes
        except sqlite.DatabaseError, e:
            raise DatabaseException("SQLite: %s" % (e))

    def _exists(self, node):
        try:
            sql = "SELECT COUNT(*) FROM "+self._nodetable \
                  +" WHERE DATATYPE=? AND NODENAME=? AND PARENT=?"
            values = (node.get_type(), node.get_cryptedname(),
                      self._get_parentid(node))
            self._cur.execute(sql, values)
            row = self._cur.fetchone()
            if (row[0] == 0):
                return False
            else:
                return True
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error checking existance of node [%s]" % (e))

    def _savekey(self, key):
        sql = "UPDATE " + self._keytable + " SET THEKEY = ?"
        values = [key]
        self._cur.execute(sql, values)

    def _loadkey(self):
        self._cur.execute("SELECT THEKEY FROM " + self._keytable);
        keyrow = self._cur.fetchone()
        if (keyrow[0] == ''):
            return None
        else:
            return keyrow[0]
    
    def _checktables(self):
        """ Check if the Pwman tables exist """
        self._cur.execute("PRAGMA TABLE_INFO("+self._nodetable+")")
        if (self._cur.fetchone() == None):
            # table doesn't exist, create it
            # SQLite does have constraints implemented at the moment
            # so datatype will just be a string
            self._cur.execute("CREATE TABLE " + self._nodetable
                             + "(ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                             + "NODENAME TEXT NOT NULL,"
                             + "DATATYPE TEXT,"
                             + "PARENT INT NOT NULL DEFAULT 0)")
            self._cur.execute("CREATE TABLE " + self._datatable
                              + "(ID INTEGER NOT NULL PRIMARY KEY,"
                              + " DATA BLOB NOT NULL)")
            self._cur.execute("CREATE TABLE " + self._keytable
                              + "(THEKEY TEXT NOT NULL DEFAULT '')");
            self._cur.execute("INSERT INTO " + self._keytable
                              + " VALUES('')");
            try:
                self._con.commit()
            except DatabaseError, e:
                self._con.rollback()
                raise e

    def _get_nodeid(self, node):
        """Returns the id of a node"""
        if (node == None):
            return 0
        
        sql = "SELECT ID FROM "+self._nodetable \
              +" WHERE DATATYPE = ? AND NODENAME = ? AND PARENT = ?"
        values = (node.get_type(), node.get_cryptedname(),
                  self._get_parentid(node))
        try:
            self._cur.execute(sql, values)
            id = self._cur.fetchone()
            if (id == None):
                raise DatabaseNoSuchNodeException(
                    "Node does not exist", node)
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error getting node id [%s]" % (e))
        return id

    def _get_parentid(self, node):
        """Returns the id of a list which this is path points to"""
        parent = node.get_parent()
        if (parent == None):
            return 0
        parentid = self._get_parentid(parent)
        try:
            self._cur.execute("SELECT ID FROM "+self._nodetable+" WHERE"
                              +" DATATYPE = ? AND NODENAME=? AND PARENT=?",
                              (parent.get_type(), parent.get_cryptedname(), parentid))
            row = self._cur.fetchone()
            if (row == None):
                raise DatabaseNoSuchNodeException(
                    "Path does not exist", node)
            parentid = row[0]
        except sqlite.DatabaseError, e:
            raise DatabaseException(
                "SQLite: Error finding parent id [%s]" %(e))
        return parentid
            
