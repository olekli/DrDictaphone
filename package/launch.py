import os
import sys

command = f'{sys._MEIPASS}/app/drdictaphone-internal'

os.execlp('open', 'open', command)
