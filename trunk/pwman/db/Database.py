"""
Main Database Module. Defines the Database abstract class that
all drivers must implement.
A Database is a heirarchal database, like a file system. Instances
should not be created directly but through DatabaseFactory.
DatabaseNode contains the path. It can be either a password or a list.
DatabaseData contains the data which is actually stored.
"""
import os.path
import pwman.util.CryptoEngine as CryptoEngine

"""Constants used to define the node types"""
PW = 'PASSWORD'
LIST = 'LIST'

class DatabaseException(Exception):
    """Generic Database Exception"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "DatabaseException: " + self.message

class DatabaseNode:
    """
    DatabaseNode contains the path to a node, and its type.
    The type can be a password or a list.
    """
    def __init__(self, name, parent, type=PW, crypted=False):
        """Initialise a DatabaseNode instance.
        name is the name of the node. parent is another DatabaseNode.
        type is either PW or LIST. If it is neither a DatabaseException
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
            raise DatabaseException(
                "Invalid Node type ["+type+"]")
    
    def _setName(self, name):
        self._cryptname = self._crypto.encrypt(name)
        self._name = name

    def _setCryptedName(self, name):
        self._cryptname = name
        self._name = self._crypto.decrypt(name)
        
    def getParent(self):
        """Return the parent DatabaseNode."""
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

class DatabaseData:
    """Database contains the data for a node. Only password nodes
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
        
class Database:
    """Database interface. Methods convert paths to
    DatabaseNodes and pass these to the driver implementations.
    All methods can raise DatabaseException.
    
    Drivers must implement:
    Database._open()
    Database._put(node, data)
    Database._get(node)
    Database._delete(node)
    Database._close()
    Database._makeList(node)
    Database._removeList(node)
    Database._listEmpty(node)
    Database._list(node)
    Database._exists(node)
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
        data = DatabaseData(dataobj)
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

    def removeList(self, path, recursive=False):
        """Remove list 'path' from current list.
        Will raise DatabaseException if list not empty."""
        node = self._buildNode(path, LIST)
        # check if list has children
        if (not self._listEmpty(node) and not recursive):
            raise DatabaseException(
                    "Cannot remove list, not empty")
        else:
            self._recursiveRemoveList(node)

    def _recursiveRemoveList(self, node):
        nodelist = self._list(node)
        for i in nodelist:
            if (i.getType() == LIST):
                self._recursiveRemoveList(i)
            else:
                self._delete(i)
        self._removeList(node)
        
    def list(self, path=None):
        """Returns a array of DatabaseNode objects in list 'path'.
        If path is None, list current."""
        if (path == None):
            node = self.getCurrentList()
        else:
            node = self._buildNode(path, LIST)
        return self._list(node)

    def exists(self, path, type=PW):
        """exists(path, type=PW) -> bool
        Check if `path` exists."""
        # / always exists, but the node is None
        # so shortcut it here
        if (path == "/"):
            return True
        node = self._buildNode(path, type)
        return self._exists(node)

    def changeList(self, path):
        """Change to list 'path'."""
        node = self._buildNode(path, LIST)
        if (node == None or self._exists(node)):
            self._clist = node
        else:
            raise DatabaseException("changeList: List does not exist")
    
    def getCurrentList(self):
        """Returns current list."""
        return self._clist

    def move(self, source, dest):
        """Move object from source to dest."""
        self.copy(source, dest)
        if (self.exists(source, PW)):
            self.delete(source)
        elif (self.exists(source, LIST)):
            self.removeList(source, True)

    def copy(self, source, dest):
        """Copy object from source to dest."""
        # check the type of source if it exists
        if (self.exists(source, PW)):
            snode = self._buildNode(source, PW)
        elif (self.exists(source, LIST)):
            snode = self._buildNode(source, LIST)
        else:
            raise DatabaseException("copy: source does not exist")

        # someone is trying to copy the root node, can't be doing that
        if (snode == None):
            raise DatabaseException("copy: cannot copy root list")
            
        # if dest is a list and exists, move into it with old name
        # else move it to dest with new name
        if (self.exists(dest, LIST)):
            path = os.path.join(dest, snode.getName())
            dnode = self._buildNode(path, snode.getType())
        elif (self.exists(dest, PW)):
            raise DatabaseException("copy: cannot overwrite dest")
        else:
            dnode = self._buildNode(dest, snode.getType())

        self._copy(snode, dnode)

    def _copy(self, snode, dnode):
        if (snode.getType() == PW):
            data = self._get(snode)
            self._put(dnode, data)
        else:
            if (not self._exists(dnode)):
                self._makeList(dnode)
                nodelist = self._list(snode)
                for i in nodelist:
                    newdnode = DatabaseNode(i.getName(), dnode, i.getType())
                    self._copy(i, newdnode)

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
        node = DatabaseNode(name, parent, type)
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

        
        
    
