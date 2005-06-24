from pwman.ui.cli import PwmanCli
from pwman.db import factory

params = {'Database' : {'type': 'SQLite', 'filename':'/tmp/test.db'},
          'Encryption' : {'algorithm': 'AES'}}

db = factory.create(params)

cli = PwmanCli(params, db)
cli.cmdloop()
