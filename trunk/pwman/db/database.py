"""
Main Database Module. Defines the Database abstract class that
all drivers must implement.
A Database is a heirarchal database, like a file system. Instances
should not be created directly but through DatabaseFactory.
DatabaseNode contains the path. It can be either a password or a list.
DatabaseData contains the data which is actually stored.
"""
import os.path
from pwman.util.crypto import CryptoEngine, CryptoNoKeyException

"""Constants used to define the node types"""
PW = 'PASSWORD'
LIST = 'LIST'

class DatabaseException(Exception):
    """Generic Database Exception"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "DatabaseException: %s" % (self.message)

class DatabaseCopyException(DatabaseException):
    """Exception copying in database"""
    def __str__(self):
        return "DatabaseCopyException: %s" % (self.message)
    
class DatabaseNodeException(DatabaseException):
    """Exception raised by node operation"""
    def __init__(self, message, node):
        self.message = message
        self.node = node
        
    def getnode():
        return self.node

    def __str__(self):
        return "DatabaseNodeException: %s (%s)" % (self.message, self.node)

class DatabaseNoSuchNodeException(DatabaseNodeException):
    """Exception raised when node does not exist"""
    def __str__(self):
        return "DatabaseNoSuchNodeException: %s (%s)" % (self.message, self.node)

class DatabaseInvalidNodeException(DatabaseNodeException):
    """Exception raised when invalid node is used"""
    def __str__(self):
        return "DatabaseInvalidNodeException: %s (%s)" % (self.message, self.node)

class DatabaseListNotEmptyException(DatabaseNodeException):
    """Exception raised when a list is not empty"""
    def __str__(self):
        return "DatabaseListNotEmptyException: %s (%s)" % (self.message, self.node)
    
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
            self._set_cryptedname(name)
        else:
            self._set_name(name)
        if (type == PW or type == LIST):
            self._type = type
        else:
            raise DatabaseInvalidNodeException(
                "Trying to create an invalid node", None)
        
    def _set_name(self, name):
        self._cryptname = self._crypto.encrypt(name)
        self._name = name

    def _set_cryptedname(self, name):
        self._cryptname = name
        self._name = self._crypto.decrypt(name)
        
    def get_parent(self):
        """Return the parent DatabaseNode."""
        return self._parent

    def get_name(self):
        """Return the name of the node in plaintext form."""
        return self._name

    def get_type(self):
        """Return the type of the node."""
        return self._type
    
    def get_cryptedname(self):
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
            self._set_crypteddata(data)
        else:
            self._set_data(data)

    def get_data(self):
        """getData() -> obj
        Return data obj in plaintext."""
        return self._data

    def get_crypteddata(self):
        """getCryptedData() -> ciphertext
        Return data obj in ciphertext."""
        return self._cryptdata

    def _set_data(self, data):
        self._data = data
        self._cryptdata = self._crypto.encrypt(data)

    def _set_crypteddata(self, data):
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
    Database._makelist(node)
    Database._removelist(node)
    Database._listempty(node)
    Database._list(node)
    Database._exists(node)
    Database._loadkey()
    Database._savekey(key)
    """

    def __init__(self, params):
        self._crypto = CryptoEngine.get(params)
        self.changelist("/") # starts at root
    
    def open(self):
        """Open the database."""
        self._open()
        key = self._loadkey()
        if (key != None):
            self._crypto.set_cryptedkey(key)
        else:
            self.changepassword()

    def put(self, path, dataobj):
        """Encrypt dataobj and put it into database under path."""
        node = self._buildnode(path)
        data = DatabaseData(dataobj)
        self._put(node, data)
        
    def get(self, path):
        """Get and decrypt data associated with path."""
        node = self._buildnode(path)
        data = self._get(node)
        return data.get_data()
        
    def delete(self, path):
        """Delete path and associated data from database."""
        node = self._buildnode(path)
        self._delete(node)
        
    def close(self):
        """Close the database."""
        self._close()

    def makelist(self, path):
        """Make list 'path' in current list."""
        node = self._buildnode(path, LIST)
        if (not self._exists(node)):
            self._makelist(node)

    def removelist(self, path, recursive=False):
        """Remove list 'path' from current list.
        Will raise DatabaseException if list not empty."""
        node = self._buildnode(path, LIST)
        # check if list has children
        if (not self._listempty(node) and not recursive):
            raise DatabaseListNotEmptyException(
                "Cannot remove list", node)
        else:
            self._recursive_removelist(node)

    def _recursive_removelist(self, node):
        nodelist = self._list(node)
        for i in nodelist:
            if (i.get_type() == LIST):
                self._recursive_removelist(i)
            else:
                self._delete(i)
        self._removelist(node)
        
    def list(self, path=None):
        """Returns a array of DatabaseNode objects in list 'path'.
        If path is None, list current."""
        if (path == None):
            node = self._clist
        else:
            node = self._buildnode(path, LIST)
        return self._list(node)
        
    def exists(self, path, type=PW):
        """exists(path, type=PW) -> bool
        Check if `path` exists."""
        # / always exists, but the node is None
        # so shortcut it here
        if (path == "/"):
            return True
        node = self._buildnode(path, type)

        return self._exists(node)
        
    def changelist(self, path):
        """Change to list 'path'."""
        node = self._buildnode(path, LIST)
        if (node == None or self._exists(node)):
            self._clist = node
        else:
            raise DatabaseNoSuchNodeException("List does not exist", node)

    def get_currentlist(self):
        """Returns current list."""
        if (self._clist == None):
            return "/"
        else:
            return self._clist

    def move(self, source, dest):
        """Move object from source to dest."""
        self.copy(source, dest)
        if (self.exists(source, PW)):
            self.delete(source)
        elif (self.exists(source, LIST)):
            self.removelist(source, True)

    def copy(self, source, dest):
        """Copy object from source to dest."""
        # check the type of source if it exists
        if (self.exists(source, PW)):
            snode = self._buildnode(source, PW)
        elif (self.exists(source, LIST)):
            snode = self._buildnode(source, LIST)
        else:
            raise DatabaseNoSuchNodeException("Source does not exist", None)

        # someone is trying to copy the root node, can't be doing that
        if (snode == None):
            raise DatabaseCopyException("Cannot copy root list")
            
        # if dest is a list and exists, move into it with old name
        # else move it to dest with new name
        if (self.exists(dest, LIST)):
            path = os.path.join(dest, snode.get_name())
            dnode = self._buildnode(path, snode.get_type())
        elif (self.exists(dest, PW)):
            raise DatabaseCopyException("Cannot overwrite destination")
        else:
            dnode = self._buildnode(dest, snode.get_type())

        self._copy(snode, dnode)

    def _copy(self, snode, dnode):
        if (snode.get_type() == PW):
            data = self._get(snode)
            self._put(dnode, data)
        else:
            if (not self._exists(dnode)):
                self._makelist(dnode)
                nodelist = self._list(snode)
                for i in nodelist:
                    newdnode = DatabaseNode(i.get_name(), dnode, i.get_type())
                    self._copy(i, newdnode)

    def changepassword(self):
        """Change the databases password."""
        newkey = self._crypto.changepassword()
        return self._savekey(newkey)

    def get_cryptocallback(self):
        return self._crypto.get_callback()

    def set_cryptocallback(self, callback):
        self._crypto.set_callback(callback)
        
    def _buildnode(self, path, type=PW):
        if (path == ""):
            return None
        if (not path.startswith("/")):
            clist = self._clist
            if (clist == None):
                path = os.path.join("/", path)
            else:
                path = os.path.join(str(clist), path)
            path = os.path.normpath(path)
        if (path == "/"):
            return None
        (path, name) = path.rsplit("/", 1)
        parent = self._buildnode(path, LIST)
        try:
            node = DatabaseNode(name, parent, type)
            return node
        except CryptoNoKeyException:
            self.changepassword()
            print type
            return self._buildnode(path, type)

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

    def _makelist(self, node):
        pass
    
    def _removelist(self, node):
        pass
        
    def _listempty(self, node):
        pass
        
    def _list(self, node):
        pass

    def _exists(self, node):
        pass

    def _savekey(self, key):
        pass
        
    def _loadkey(self):
        pass
    
