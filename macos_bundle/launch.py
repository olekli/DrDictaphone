import os

user_dir = os.path.expanduser('~/DrDictaphone')
terminal_command = f'{user_dir}/config/terminal.sh'
dr_command = f'{user_dir}/app/run'

os.execl(terminal_command, 'terminal.sh', dr_command)
