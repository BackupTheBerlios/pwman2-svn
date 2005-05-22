"""
Main PwmanDatabase Module. Defines the PwmanDatabase abstract class that
all drivers must implement.
A PwmanDatabase is a heirarchal database, like a file system. Instances
should not be created directly but through PwmanDatabaseFactory.
PwmanDatabaseNode contains the path. It can be either a password or a list.
PwmanDatabaseData contains the data which is actually stored.
"""
import os.path
import pwdb.CryptoEngine as CryptoEngine

"""Constants used to define the node types"""
PW = 'PASSWORD'
LIST = 'LIST'

class PwmanDatabaseException(Exception):
    """Generic PwmanDatabase Exception"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "PwmanDatabaseException: " + self.message

class PwmanDatabaseNode:
    """
    PwmanDatabaseNode contains the path to a node, and its type.
    The type can be a password or a list.
    """
    def __init__(self, name, parent, type=PW, crypted=False):
        """Initialise a PwmanDatabaseNode instance.
        name is the name of the node. parent is another PwmanDatabaseNode.
        type is either PW or LIST. If it is neither a PwmanDatabaseException
        is raised.
        crypted specifies whether the name is ciphertext or plaintext.
        Defaults to False"""
        self._crypto = CryptoEngine.get()
        self._parent = parent
        if (crypted == True):
            self._setCryptedName(name)
        else:
            self._setName(name)
        if (type == PW or type == LIST):
            self._type = type
        else:
            raise PwmanDatabaseException(
                "Invalid Node type ["+type+"]")
    
    def _setName(self, name):
        self._cryptname = self._crypto.encrypt(name)
        self._name = name

    def _setCryptedName(self, name):
        self._cryptname = name
        self._name = self._crypto.decrypt(name)
        
    def getParent(self):
        """Return the parent PwmanDatabaseNode."""
        return self._parent

    def getName(self):
        """Return the name of the node in plaintext form."""
        return self._name

    def getType(self):
        """Return the type of the node."""
        return self._type
    
    def getCryptedName(self):
        """Return the name of the node in ciphertext form."""
        return self._cryptname

    def __str__(self):
        """Return a string representation of the node."""
        if (self._parent == None):
            return os.path.join("/", self._name)
        else:
            return os.path.join(self._parent.__str__(), self._name)

class PwmanDatabaseData:
    """PwmanDatabase contains the data for a node. Only password nodes
    have data."""
    def __init__(self, data, crypted=False):
        """Initialise a data instance. data can be any picklable object
        if crypted is false. If crypted is true, then data must be an
        object thats been previously encrypted."""        
        self._crypto = CryptoEngine.get()
        if crypted == True:
            self._setCryptedData(data)
        else:
            self._setData(data)

    def getData(self):
        """getData() -> obj
        Return data obj in plaintext."""
        return self._data

    def getCryptedData(self):
        """getCryptedData() -> ciphertext
        Return data obj in ciphertext."""
        return self._cryptdata

    def _setData(self, data):
        self._data = data
        self._cryptdata = self._crypto.encrypt(data)

    def _setCryptedData(self, data):
        self._cryptdata = data
        self._data = self._crypto.decrypt(data)
        
class PwmanDatabase:
    """PWDB Database interface. Methods convert paths to
    PwmanDatabaseNodes and pass these to the driver implementations.
    All methods can raise PwmanDatabaseException.
    
    Drivers must implement:
    PwmanDatabase._open()
    PwmanDatabase._put(node, data)
    PwmanDatabase._get(node)
    PwmanDatabase._delete(node)
    PwmanDatabase._close()
    PwmanDatabase._makeList(node)
    PwmanDatabase._removeList(node)
    PwmanDatabase._listEmpty(node)
    PwmanDatabase._list(node)
    PwmanDatabase._exists(node)
    """
    
    def __init__(self, params):
        """Initial crypto engine. Also sets the current list to "/"."""
        CryptoEngine.init(params)
        self.changeList("/") # starts at root

    def open(self):
        """Open the database."""
        self._open()

    def put(self, path, dataobj):
        """Encrypt dataobj and put it into database under path."""
        node = self._buildNode(path)
        data = PwmanDatabaseData(dataobj)
        self._put(node, data)

    def get(self, path):
        """Get and decrypt data associated with path."""
        node = self._buildNode(path)
        data = self._get(node)
        return data.getData()

    def delete(self, path):
        """Delete path and associated data from database."""
        node = self._buildNode(path)
        self._delete(node)

    def close(self):
        """Close the database."""
        self._close()

    def makeList(self, path):
        """Make list 'path' in current list."""
        node = self._buildNode(path, LIST)
        if (not self._exists(node)):
            self._makeList(node)

    def removeList(self, path):
        """Remove list 'path' from current list.
        Will raise PwmanDatabaseException if list not empty."""
        node = self._buildNode(path, LIST)
        # check if list has children
        if (not self._listEmpty(node)):
            raise PwmanDatabaseException(
                    "Cannot remove list, not empty")
        self._removeList(node)
        
    def list(self, path=None):
        """Returns a array of PwmanDatabaseNode objects in list 'path'.
        If path is None, list current."""
        if (path == None):
            node = self.getCurrentList()
        else:
            node = self._buildNode(path, LIST)
        return self._list(node)

    def exists(self, path, type=PW):
        """exists(path, type=PW) -> bool
        Check if `path` exists."""
        node = self._buildNode(path, type)
        return self._exists(node)

    def changeList(self, path):
        """Change to list 'path'."""
        node = self._buildNode(path, LIST)
        if (node == None or self._exists(node)):
            self._clist = node
        else:
            raise PwmanDatabaseException("changeList: List does not exist")
    
    def getCurrentList(self):
        """Returns current list."""
        return self._clist

    def move(self, oldpath, newpath):
        """Move object from oldpath to newpath"""
        oldpath = DatabasePath(self.getcwd(), oldpath)
        newpath = DatabasePath(self.getcwd(), newpath)
        self._move(oldpath, newpath)

    def copy(self, oldpath, newpath):
        """Copy object from oldpath to newpath"""
        oldpath = DatabasePath(self.getcwd(), oldpath)
        newpath = DatabasePath(self.getcwd(), newpath)
        self._copy(oldpath, newpath)

    def _buildNode(self, path, type=PW):
        if (path == ""):
            return None
        if (not path.startswith("/")):
            clist = self.getCurrentList()
            if (clist == None):
                path = os.path.join("/", path)
            else:
                path = os.path.join(self.getCurrentList().__str__(), path)
            path = os.path.normpath(path)
        if (path == "/"):
            return None
        (path, name) = path.rsplit("/", 1)
        parent = self._buildNode(path, LIST)
        node = PwmanDatabaseNode(name, parent, type)
        return node

    ##
    ## methods that need to be implemented by subclasses
    ##
    def _open(self):
        pass        

    def _put(self, node, data):
        pass
    
    def _get(self, node):
        pass
    
    def _delete(self, node):
        pass
        
    def _close(self):
        pass

    def _makeList(self, node):
        pass
    
    def _removeList(self, node):
        pass
        
    def _listEmpty(self, node):
        pass
        
    def _list(self, node):
        pass

    def _exists(self, node):
        pass

        
        
    
