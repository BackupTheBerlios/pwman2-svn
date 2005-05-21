import os.path

import pwdb.CryptoEngine

# CONSTANTS
PW = 'PASSWORD'
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
    def __init__(self, name, parent, type=PW):
        self._parent = parent
        self._setName(name)
        if (type == PW or type == LIST):
            self._type = type
        else:
            raise PwmanDatabaseException(
                "Invalid Node type ["+type+"]")
##         if (filename == None):
##             self.setPath(self, pathstr)
##         elif (filename.startswith('/')):
##             self.setPath(self, filename)
##         else:
##             path = os.path.join(pathstr, filename)
##             self.setPath(path)
    
    def _setName(self, name):
        self._name = name
        
    def getParent(self):
        return self._parent

    def getName(self):
        return self._name

    def getType(self):
        return self._type
    
    def getCryptedName(self):
        return self._name

    def __str__(self):
        if (self._parent == None):
            return os.path.join("/", self._name)
        else:
            return os.path.join(self._parent.__str__(), self._name)

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
        CryptoEngine.init(params)
        self.changeList("/") # starts at root

    def open(self):
        """Open the database"""
        self._open()

    def put(self, path, dataobj):
        """Encrypt data and put it into database under name"""
        node = self._buildNode(path)
        data = PwmanDatabaseData(dataobj)
        self._put(node, data)

    def get(self, path):
        """Get and decrypt data associated with name"""
        node = self._buildNode(path)
        data = self._get(node)
        return data.getData()

    def delete(self, path):
        """Delete name and associated data from database"""
        node = self._buildNode(path)
        self._delete(node)

    def close(self):
        """Close the database"""
        self._close()

    def makeList(self, path):
        """Make directory 'path' in current directory"""
        node = self._buildNode(path, LIST)
        if (not self._exists(node)):
            self._makeList(node)

    def removeList(self, path):
        """Remove directory 'path' from current directory"""
        node = self._buildNode(path, LIST)
        self._removeList(node)
        
    def list(self, path=None):
        """Returns a list object in directory 'path'"""
        if (path == None):
            node = self.getCurrentList()
        else:
            node = self._buildNode(path, LIST)
        return self._list(node)

    def exists(self, path, type=PW):
        """Return bool whether an object exists"""
        node = self._buildNode(path, type)
        return self._exists(node)

    def changeList(self, path):
        """Change to directory 'path'"""
        node = self._buildNode(path, LIST)
        if (node == None or self._exists(node)):
            self._clist = node
        else:
            raise PwmanDatabaseException("changeList: List does not exist")
    
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

        
        
    
