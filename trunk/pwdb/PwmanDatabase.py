import os.path

import pwdb.Encryptor

# CONSTANTS
NODE = 'NODE'
LIST = 'LIST'

class PwmanDatabaseException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return "PwmanDatabaseException: " + self.message

## class PwmanDatabaseList:
##     def __init__(self, path):
##         self._setPath(path)

##     def _setPath(self, path):
##         # encryption will be done here was well
##         self._path = os.path.normpath(path)
        
##     def getPath(self):
##         return self._path

##     def getCryptedPath(self):
##         return self._path

##     def __str__(self):
##         return self._path
        

class PwmanDatabaseNode:
    def __init__(self, name, parent, type=NODE):
        self._parent = parent
        self._setName(name)
        self._type = type
##         if (filename == None):
##             self.setPath(self, pathstr)
##         elif (filename.startswith('/')):
##             self.setPath(self, filename)
##         else:
##             path = os.path.join(pathstr, filename)
##             self.setPath(path)
    
    def _setName(self, node):
        self._node = node
        
    def getParent(self):
        return self._parent

    def getName(self):
        return self._node

    def getCryptedName(self):
        return self._node

    def __str__(self):
        return os.path.join(self._parent.__str__(), self._node)

class PwmanDatabaseData:
    def __init__(self, data, crypted=False):
        if crypted == True:
            self.setCryptedData(data)
        else:
            self.setData(data)

    def getData(self):
        return self._data

    def getCryptedData(self):
        return self._cryptdata

    def setData(self, data):
        self._data = data
        self._cryptdata = data #Cryptor.encrypt(data)

    def setCryptedData(self, data):
        self._data = data
        
class PwmanDatabase:
    """PWDB Database interface"""
    
    def __init__(self, params):
        """Initialised encrytion used by all"""
        self.changeList("/") # starts at root

    def open(self):
        """Open the database"""
        self._open()

    def _open(self):
        pass 

    def put(self, path, dataobj):
        """Encrypt data and put it into database under name"""
        node = self._buildNode(path)
        data = PwmanDatabaseData(dataobj)
        self._put(node, data)
        
    def _put(self, node, data):
        pass

    def get(self, path):
        """Get and decrypt data associated with name"""
        if (nodename.startswith("/")):
            raise PwmanDatabaseException("Implement relative in get")
        node = self._buildNode(path)
        data = self._get(node)
        return data.getData()

    def _get(self, node):
        pass

    def delete(self, path):
        """Delete name and associated data from database"""
        node = self._buildNode(path)
        self._delete(node)

    def _delete(self, node):
        pass

    def close(self):
        """Close the database"""
        self._close()

    def _close(self):
        pass

    def makeList(self, path):
        """Make directory 'path' in current directory"""
        path = DatabasePath(self.getcwd(), name)
        self._mkdir(path)

    def _makeList(self, path):
        pass

    def removeList(self, path):
        """Remove directory 'path' from current directory"""
        path = DatabasePath(self.getcwd(), name)
        self._rmdir(name)
        
    def _removeList(self, path):
        pass

    
    def list(self, path=None):
        """Returns a list object in directory 'path'"""
        if (path == None):
            path = DatabasePath(self.getcwd())
        return self._list(path)

    def _list(self, path):
        pass

    def changeList(self, path):
        """Change to directory 'path'"""
        self._clist = self._buildNode(path, LIST)
##         if (path.startswith("/")):
##             self._clist = PwmanDatabaseList(path)
##         else:
##             raise PwmanDatabaseException("Relative paths not implemented yet")
    
    def getCurrentList(self):
        """Returns current working directory"""
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

    def exists(self, path):
        """Return bool whether an object exists"""
        path = DatabasePath(self.getcwd(), path)
        return self._exists(path)

    def _exists(self, path):
        pass

    def isList(self, path):
        """Return bool whether an object is a directory"""
        path = DatabasePath(self.getcwd(), path)
        return self._isdir(path)

    def _isList(self, path):
        pass

    def isNode(self, path):
        """Return bool whether an object is a password"""
        path = DatabasePath(self.getcwd(), path)
        return self._ispw(path)

    def _isNode(self, path):
        pass

    def _buildNode(self, path, type=NODE):
        if (path == ""):
            return PwmanDatabaseNode(
        if (not path.startswith("/")):
            path = os.path.join(self.getCurrentList(), path)
            path = os.path.normpath(path)
        (path, name) = path.rsplit("/", 1)
        parent = self._buildNode(path, LIST)
        node = PwmanDatabaseNode(name, parent, type)
        return node
        
        
    
