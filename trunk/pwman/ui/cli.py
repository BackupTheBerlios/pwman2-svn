import pwman
import pwman.db.factory as factory
from pwman.db.database import LIST,PW
from pwman.db.password import Password

from pwman.util.crypto import Callback, CryptoBadKeyException, \
     CryptoPasswordMismatchException

import sys
import tty
import os
import getpass
import cmd

try:
    import readline
    _readline_available = True
except ImportError, e:
    _readline_available = False


class CLICallback(Callback):
    def execute(self, question):
        return getpass.getpass(question + ":")

class ANSI(object):
    Reset = 0
    Bold = 1
    Underscore = 2

    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Magenta = 35
    Cyan = 36
    White = 37

class PwmanCli(cmd.Cmd):
    def error(self, exception):
        print "Error: %s" % (exception)
    
    def do_EOF(self, args):
        self.do_exit(args)

    def do_quit(self, args):
        self.do_exit(args)
        
    def do_exit(self, args):
        print
        self._db.close()
        sys.exit(0)

    def get_username(self, default=""):
        return getinput("Username: ", default)

    def get_password(self, default=""):
        return getinput("Password: ", default)

    def get_url(self, default=""):
        return getinput("Url: ", default)

    def get_notes(self, default=""):
        return getinput("Notes: ", default)

    def get_nodename(self, default=""):
        return getinput("Save As: ", default)

    def print_node(self, node):
        width = str(_defaultwidth)
        print ("%"+width+"s %s") % (typeset("Username:", ANSI.Red),
                                    node.get_username())
        print ("%"+width+"s %s") % (typeset("Password:", ANSI.Red),
                                    node.get_password())
        print ("%"+width+"s %s") % (typeset("Url:", ANSI.Red),
                                    node.get_url())
        print ("%"+width+"s %s") % (typeset("Notes:", ANSI.Red),
                                    node.get_notes())
        
    def do_edit(self, arg):
        try:
            password = self._db.get(arg)
            if (not isinstance(password, Password)):
                return
            menu = CliMenu()
            menu.add(CliMenuItem("Username", self.get_username,
                                 password.get_username,
                                 password.set_username))
            menu.add(CliMenuItem("Password", self.get_password,
                                 password.get_password,
                                 password.set_password))
            menu.add(CliMenuItem("Url", self.get_url,
                                 password.get_url,
                                 password.set_url))
            menu.add(CliMenuItem("Notes", self.get_notes,
                                 password.get_notes,
                                 password.set_notes))
            menu.run()
            self._db.put(arg, password)
        except Exception, e:
            self.error(e)
    
    def do_new(self, arg):
        try:
            username = self.get_username()
            password = self.get_password()
            url = self.get_url()
            notes = self.get_notes()
            nodename = self.get_nodename()
            
            password = Password(username, password, url, notes)
            if (self._db.exists(nodename)):
                if (not getyesno("Password already exists. Overwrite?")):
                    return
            self._db.put(nodename, password)
        except EOFError:
            self.do_exit()
        except Exception, e:
            self.error(e)
        
    def do_show(self, arg):
        try:
            node = self._db.get(arg)
            if (isinstance(node, Password)):
                self.print_node(node)
            else:
                print node
        except Exception, e:
            self.error(e)
        
    def do_chlist(self, args):
        try:
            self._db.changelist(args)
        except Exception, e:
            self.error(e)
        
    def do_list(self, args):
        try:
            nodelist = self._db.list()
            for i in nodelist:
                if (i.get_type() == LIST):
                    print typeset("%s/" % (i.get_name()),
                                       ANSI.Blue, True)
            for i in nodelist:
                if (i.get_type() == PW):
                    print typeset("%s" % (i.get_name()),
                                       ANSI.Yellow, False)
        except CryptoBadKeyException, e:
            self.error(e)

    def postcmd(self, stop, line):
        self.updateprompt()
        return False

    def updateprompt(self):
        self.prompt = "%s:%s> " % ("pwman", 
                                   self._db.get_currentlist())
        
    def __init__(self, params, db):
        cmd.Cmd.__init__(self)
        self.intro = "%s %s (c) %s <%s>" % (pwman.appname, pwman.version,
                                            pwman.author, pwman.authoremail)
        self._db = db
        self._db.set_cryptocallback(CLICallback())
        self._db.open()
        self.updateprompt()

        _colors = True


_defaultwidth = 10
_colors = False

def getonechar(question, width=_defaultwidth):
    question = "%s " % (question)
    print question.ljust(width),
    sys.stdout.flush()
        
    fd = sys.stdin.fileno()
    tty_mode = tty.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        ch = os.read(fd, 1)
    finally:
        tty.tcsetattr(fd, tty.TCSAFLUSH, tty_mode)
    print ch
    return ch
    
def getyesno(defaultyes=False, width=_defaultwidth):
    if (defaultyes):
        default = "[Y/n]"
    else:
        default = "[y/N]"
    ch = getonechar("%s %s" % (question, default), width)
    if (ch == '\n'):
        if (defaultyes):
            print "Y"
            return True
        else:
            print "N"
            return False
    elif (ch == 'y' or ch == 'Y'):
        return True
    elif (ch == 'n' or ch == 'N'):
        return False
    else:
        return getyesno(question, defaultyes, width)
            
def getinput(question, default="", width=_defaultwidth):
    if (not _readline_available):
        return raw_input(question.ljust(width))
    else:
        def defaulter(): readline.insert_text(default)
        readline.set_startup_hook(defaulter)
        x = raw_input(question.ljust(width))
        readline.set_startup_hook()
        return x

def getpassword(question, width=_defaultwidth):
    return getpass.getpass(question.ljust(width))
        
def typeset(text, color, bold=False, underline=False):
    if (not _colors):
        return text
    if (bold):
        bold = "%d;" %(ANSI.Bold)
    else:
        bold = ""
    if (underline):
        underline = "%d;" % (ANSI.Underline)
    else:
        underline = ""
    return "\033[%s%s%sm%s\033[%sm" % (bold, underline, color,
                                       text, ANSI.Reset)

class CliMenu(object):
    def __init__(self):
        self.items = []
        
    def add(self, item):
        if (isinstance(item, CliMenuItem)):
            self.items.append(item)
        else:
            print item.__class__

    def run(self):
        while True:
            i = 0
            for x in self.items:
                i = i + 1
                print ("%d - %-"+str(_defaultwidth)+"s %s") % (i, x.name+":",
                                                               x.getter())
            print "%c - Finish editing" % ('X')
            option = getonechar("Enter your choice:")
            try:
                # substract 1 because array subscripts start at 1
                selection = int(option) - 1 
                value = self.items[selection].editor(self.items[selection].getter())
                self.items[selection].setter(value)
            except (ValueError,IndexError):
                if (option.upper() == 'X'):
                    break
                print "Invalid selection"
                
class CliMenuItem(object):
    def __init__(self, name, editor, getter, setter):
        self.name = name
        self.editor = editor
        self.getter = getter
        self.setter = setter
