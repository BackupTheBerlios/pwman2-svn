"""Module deals with the handling of passwords."""

class Password:
    """The password class."""
    def __init__(self):
        """Initialise everything to null."""
        self._username = None
        self._password = None
        self._url = None
        self._notes = None
    
    def getUsername(self):
        """Return the username."""
        return self._username

    def setUsername(self, username):
        """Set the username."""
        self._username = username

    def getPassword(self):
        """Return the password."""
        return self._password

    def setPassword(self, password):
        """Set the password."""
        self._password = password

    def getUrl(self):
        """Return the URL."""
        return self._url

    def setUrl(self, url):
        """Set the URL."""
        self._url = url

    def getNotes(self):
        """Return the Notes."""
        return self._notes

    def setNotes(self, notes):
        """Set the Notes."""
        self._notes = notes
