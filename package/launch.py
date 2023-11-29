import applescript
import sys

command = f'{sys._MEIPASS}/app/drdictaphone-internal'

script = f'''
tell application "Terminal"
  do script "{command}"
  activate
end tell
'''

applescript.AppleScript(script).run()
