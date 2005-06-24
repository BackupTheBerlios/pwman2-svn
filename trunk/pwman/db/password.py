"""Module deals with the handling of passwords."""

class Password:
    """The password class."""
    def __init__(self,username="",password="",url="",notes=""):
        """Initialise everything to null."""
        self._username = username
        self._password = password
        self._url = url
        self._notes = notes
    
    def get_username(self):
        """Return the username."""
        return self._username

    def set_username(self, username):
        """Set the username."""
        self._username = username

    def get_password(self):
        """Return the password."""
        return self._password

    def set_password(self, password):
        """Set the password."""
        self._password = password

    def get_url(self):
        """Return the URL."""
        return self._url

    def set_url(self, url):
        """Set the URL."""
        self._url = url

    def get_notes(self):
        """Return the Notes."""
        return self._notes

    def set_notes(self, notes):
        """Set the Notes."""
        self._notes = notes
