from pwman.ui.cli import PwmanCLI
from pwman.db import factory

params = {'Database' : {'type': 'SQLite', 'filename':'/tmp/test.db'},
          'Encryption' : {'algorithm': 'AES'}}

db = factory.create(params)

cli = PwmanCLI(db)
cli.cmdloop()
