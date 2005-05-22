from pwdb.PwmanDatabase import PwmanDatabase,PwmanDatabaseException,\
     PwmanDatabaseNode,PwmanDatabaseData, PW, LIST
from pysqlite2 import dbapi2 as sqlite

class SQLitePwmanDatabase(PwmanDatabase):
    """SQLite Database implementation"""
    
    def __init__(self, params):
        PwmanDatabase.__init__(self, params)

        self._nodetable = 'NODES';
        self._datatable = 'DATA';
        
        try:
            self._filename = params['filename']
        except KeyError, e:
            raise PwmanDatabaseException(
                "SQLite: missing parameter ["+e+"]")

    def _open(self):
        try:
            self._con = sqlite.connect(self._filename)
            self._cur = self._con.cursor()
            self._checkTables()
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException("SQLite: " + e.__str__())
        

    def _put(self, node, data):
        if (node.getType() != PW):
            raise PwmanDatabaseException(
                "SQLite: Invalid node, not a password");

        if self._exists(node):
            id = self._getNodeId(node)
        else:
            id = 0

        # create statements for adding the nodes to the database
        if id == 0:
            sql = "INSERT INTO "+self._nodetable \
                  +"(DATATYPE, NODENAME, PARENT)  VALUES(?, ?, ?)"
            values = (node.getType(), node.getCryptedName(),
                      self._getParentId(node))
            try:
                self._cur.execute(sql, values)
            except sqlite.DatabaseError, e:
                raise PwmanDatabaseException(
                    "SQLite: Error creating node in db ["+e.__str__()+"]")

            sql = "INSERT INTO "+self._datatable+" VALUES(?, ?)"
            values = (self._cur.lastrowid, data.getCryptedData());

            # insert the data into the database
            try:
                self._cur.execute(sql, values)
            except sqlite.DatabaseError, e:
                raise PwmanDatabaseException(
                    "SQLite: Error creating data in db ["+e+"]")
        else:
            sql = "UPDATE "+self._datatable+" SET DATA=? WHERE ID=?"
            values = (data.getCryptedData(), id)

            # update database with new data
            try:
                self._cur.execute(sql, values)
            except sqlite.DatabaseError, e:
                raise PwmanDatabaseException(
                    "SQLite: Error updating data in db ["+e+"]")
        try:
            self._con.commit()
        except DatabaseError, e:
            self._con.rollback()
            raise PwmanDatabaseException(
                "SQLite: Error commiting data to db ["+e+"]")

    def _get(self, node):
        if (node.getType() != PW):
            raise PwmanDatabaseException(
                "SQLite: Invalid node, not password");

        sql = "SELECT DATA FROM "+self._nodetable \
              +" INNER JOIN "+self._datatable+" ON " \
              +self._nodetable+".ID = "+self._datatable+".ID " \
              +"WHERE DATATYPE = ? AND NODENAME = ? AND PARENT = ?"
        values = (node.getType(), node.getCryptedName(), \
                  self._getParentId(node))
        try:
            self._cur.execute(sql, values)
            data = self._cur.fetchone()
            if (data == None):
                raise PwmanDatabaseException(
                    "SQLite: Node does not exist in database")
            else:
                nodedata = PwmanDatabaseData(data[0], True)
                return nodedata
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException(
                "SQLite: Error reading node from db ["+e+"]")

    def _delete(self, node):
        if (node.getType() != PW):
            raise PwmanDatabaseException(
                "SQLite: Invalid node, not password");
        
        # get the id
        id = self._getNodeId(node)

        # delete the node from the db
        try:
            self._cur.execute("DELETE FROM "+self._nodetable 
                              + " WHERE ID = ?", [id])
            self._cur.execute("DELETE FROM "+self._datatable
                              + " WHERE ID = ?", [id])
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException(
                "SQLite: Error deleting from db ["+e.__str__()+"]")

        # commit the delete to the database
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:
            self._con.rollback()
            raise PwmanDatabaseException(
                "SQLite: Error committing delete to db ["+e.__str__()+"]")
        
    def _close(self):
        self._cur.close()
        self._con.close()

    def _makeList(self, node):
        if (node.getType() != LIST):
            raise PwmanDatabaseException(
                "SQLite: Invalid node, not a list");
        sql = "INSERT INTO "+self._nodetable \
              +"(DATATYPE, NODENAME, PARENT)  VALUES(?, ?, ?)"
        values = (node.getType(), node.getCryptedName(),
                  self._getParentId(node))
        try:
            self._cur.execute(sql, values)
            self._con.commit()
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException(
                "SQLite: Error creating list ["+e.__str__()+"]")

    def _removeList(self, node):
        if (node.getType() != LIST):
            raise PwmanDatabaseException(
                "SQLite: Invalid node, not a list");
        
        # Find id of list to be deleted
        id = self._getNodeId(node)

        # check if list has children
        if (not self._listEmpty(node)):
            raise PwmanDatabaseException(
                    "SQLite: Cannot remove list, not empty")
                
        # finally, we delete the list from the database is all is ok
        try:
            self._cur.execute("DELETE FROM "+self._nodetable
                              +" WHERE ID = ?", [id])
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException(
                "SQLite: Error deleting list from database ["+e.__str__()+"]")

        # now commit the changes and bob's your uncle
        try:
            self._con.commit()
        except sqlite.DatabaseError, e:
            self._con.rollback()
            raise PwmanDatabaseException(
                "SQLite: Error committing list removal ["+e.__str__()+"]")
        
    def _listEmpty(self, node):
        # Find id of list to be deleted
        id = self._getNodeId(node)
        
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
            raise PwmanDatabaseException(
                "SQLite: Error checking for list children ["+e.__str__()+"]")
        
    def _list(self, node):
        try:
            id = self._getNodeId(node)
            sql = "SELECT NODENAME, DATATYPE FROM "+self._nodetable \
                  +" WHERE PARENT = ?";
            self._cur.execute(sql, [id])
            
            nodes = []
            row = self._cur.fetchone()
            while (row != None):
                nodes.append(PwmanDatabaseNode(row[0], node, row[1], True))
                row = self._cur.fetchone()
            return nodes
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException("SQLite: " + e)

    def _exists(self, node):
        try:
            sql = "SELECT COUNT(*) FROM "+self._nodetable \
                  +" WHERE DATATYPE=? AND NODENAME=? AND PARENT=?"
            values = (node.getType(), node.getCryptedName(),
                      self._getParentId(node))
            self._cur.execute(sql, values)
            row = self._cur.fetchone()
            if (row[0] == 0):
                return False
            else:
                return True
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException(
                "SQLite: Error checking existance of node ["+e.__str__()+"]")

    def _checkTables(self):
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
            try:
                self._con.commit()
            except DatabaseError, e:
                self._con.rollback()
                raise e

    def _getNodeId(self, node):
        """Returns the id of a node"""
        if (node == None):
            return 0
        
        sql = "SELECT ID FROM "+self._nodetable \
              +" WHERE DATATYPE = ? AND NODENAME = ? AND PARENT = ?"
        values = (node.getType(), node.getCryptedName(),
                  self._getParentId(node))
        try:
            self._cur.execute(sql, values)
            id = self._cur.fetchone()
            if (id == None):
                raise PwmanDatabaseException(
                    "SQLite: Node does not exist")
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException(
                "SQLite: Error getting node id ["+e.__str__()+"]")
        return id

    def _getParentId(self, node):
        """Returns the id of a list which this is path points to"""
        parent = node.getParent()
        if (parent == None):
            return 0
        parentid = self._getParentId(parent)
        try:
            self._cur.execute("SELECT ID FROM "+self._nodetable+" WHERE"
                              +" DATATYPE = ? AND NODENAME=? AND PARENT=?",
                              (parent.getType(), parent.getCryptedName(), parentid))
            row = self._cur.fetchone()
            if (row == None):
                raise PwmanDatabaseException(
                    "SQLite: Path does not exist")
            parentid = row[0]
        except sqlite.DatabaseError, e:
            raise PwmanDatabaseException(
                "SQLite: Error finding parent id ["+e.__str__()+"]")
        return parentid
            
