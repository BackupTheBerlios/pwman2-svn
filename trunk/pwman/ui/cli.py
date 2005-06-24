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

class ANSI:
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

class PwmanCLI(cmd.Cmd):
    _defaultwidth = 10
        
    def getonechar(self, question, width=_defaultwidth):
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
    
    def getyesno(self, question, defaultyes=False, width=_defaultwidth):
        if (defaultyes):
            default = "[Y/n]"
        else:
            default = "[y/N]"
        ch = self.getonechar("%s %s" % (question, default), width)
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
            return self.getyesno(question, defaultyes, width)
            
    def getinput(self, question, default="", width=_defaultwidth):
        if (!_readline_available):
            return raw_input(question.ljust(width))
        else:
            def defaulter(): readline.insert_text(default)
            readline.set_startup_hook(defaulter)
            x = raw_input(question.ljust(width))
            readline.set_startup_hook()
            return x

    def getpass(self, question, width=_defaultwidth):
        return getpass.getpass(question.ljust(width))

    def error(self, exception):
        print "Error: %s" % (exception)
        
    def typeset(self, text, color, bold=False, underline=False):
        if (!self._colors):
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
    
    def do_EOF(self, args):
        self.do_exit(args)

    def do_quit(self, args):
        self.do_exit(args)
        
    def do_exit(self, args):
        print
        self._db.close()
        sys.exit(0)

    def get_username(self, default=""):
        return self.getinput("Username: ", default)

    def get_password(self, default=""):
        return self.getinput("Password: ", default)

    def 
    
    def editmenu(self, password):
        print "Select item to edit:"
        print "1 - Username:".ljust(self._defaultwidth) + password.getUsername()
        print "2 - Password:".
    
    def do_edit(self, arg):
        try:
            pass
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
                self._db.put(nodename, password)
        except EOFError:
            self.do_exit()
        except Exception, e:
            self.error(e)
        
    def do_show(self, arg):
        try:
            node = self._db.get(arg)
            if type(node) == Password:
                self.print_password(node)
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
                    print self.typeset("%s/" % (i.get_name()),
                                       ANSI.Blue, True)
            for i in nodelist:
                if (i.get_type() == PW):
                    print self.typeset("%s" % (i.get_name()),
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

        self.colors = True

class CliMenu:
    pass

class CliMenuItem:
    def __init__(name, ):
        pass
