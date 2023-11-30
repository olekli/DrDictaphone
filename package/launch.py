import os
import sys

kitty_command = f'/Applications/kitty.app/Contents/MacOS/kitty'
dr_command = f'{sys._MEIPASS}/app/drdictaphone-internal'
config_path = f'{os.path.expanduser("~/DrDictaphone")}/config/.assembled-kitty.conf'
default_config_path = f'{sys._MEIPASS}/kitty-default.conf'
user_config_path = f'{os.path.expanduser("~/DrDictaphone")}/config/kitty.conf'

if not os.path.exists(user_config_path):
  with open(default_config_path, 'rt') as source:
    with open(user_config_path, 'wt') as target:
      target.write(source.read())

with open(user_config_path, 'rt') as file:
  user_config = file.read()

with open(config_path, 'wt') as file:
  file.write(user_config)
  file.write('\n')
  file.write(f'shell "{dr_command}"')

os.execl(
  kitty_command, 'kitty',
  '--instance-group=DRDICTAPHONE',
  '--single-instance',
  '-c', config_path
)
