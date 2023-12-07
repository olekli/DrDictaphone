# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import sys
import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import set_title
from mreventloop import EventLoop, connect, setEventLoop, getEventLoop
from drdictaphone.config import getProfilePath
from drdictaphone.beep import Beep
from drdictaphone.status_line import StatusLine
from drdictaphone.app import App
from drdictaphone.main import Main
import drdictaphone.logger_config
from drdictaphone import logger

def promptForProfile():
  profile_path = getProfilePath(None)
  available_profiles = os.listdir(profile_path)
  available_profiles.sort(
    key = lambda x: os.path.getatime(os.path.join(profile_path, x)),
    reverse = True
  )
  available_profiles = [
    x for x, y in [
      os.path.splitext(entry) for entry in available_profiles
    ]
  ]
  completer = WordCompleter(available_profiles)
  print('Available profiles:\n')
  for profile in available_profiles:
    print(f'{profile}')
  print('')
  user_input = prompt(f'Select profile ({available_profiles[0]}): ', completer = completer)
  if user_input == '':
    user_input = available_profiles[0]
  print(f'selected {user_input}')
  return user_input

if __name__ == '__main__':
  logger = logger.get(__name__)

  set_title('DrDictaphone')

  profile_name = promptForProfile()
  set_title(profile_name)

  print('running...')

  with Main(profile_name) as main:
    with EventLoop() as beep_loop:
      app = App()
      setEventLoop(app, main.event_loop)

      status_line = StatusLine(profile_name)
      setEventLoop(status_line, main.event_loop)
      connect(main.microphone, 'active', status_line, 'onMICactive')
      connect(main.microphone, 'idle', status_line, 'onMICidle')
      connect(getEventLoop(main.transcriber), 'active', status_line, 'onTRANSactive')
      connect(getEventLoop(main.transcriber), 'idle', status_line, 'onTRANSidle')
      connect(getEventLoop(main.post_processor), 'active', status_line, 'onPOSTactive')
      connect(getEventLoop(main.post_processor), 'idle', status_line, 'onPOSTidle')

      connect(status_line, 'status_update_left', app, 'updateStatusLeft')
      connect(status_line, 'status_update_center', app, 'updateStatusCenter')
      connect(status_line, 'status_update_right', app, 'updateStatusRight')
      connect(main.aggregator, 'result', app, 'updateText')

      connect(app, 'start_rec', main.pipeline, 'onStartRec')
      connect(app, 'stop_rec', main.pipeline, 'onStopRec')
      connect(app, 'pause_mic', main.pipeline, 'onPauseMic')
      connect(app, 'unpause_mic', main.pipeline, 'onUnpauseMic')

      connect(app, 'clear_buffer', main.pipeline, 'onClearBuffer')

      beep = Beep()
      setEventLoop(beep, beep_loop)

      if main.profile.enable_vad:
        connect(getEventLoop(main.vad), 'active', status_line, 'onVADactive')
        connect(getEventLoop(main.vad), 'idle', status_line, 'onVADidle')

      connect(app, 'start_rec', beep, 'beepHighLong')
      connect(app, 'stop_rec', beep, 'beepLowLong')
      connect(app, 'pause_mic', beep, 'beepLowShort')
      connect(app, 'unpause_mic', beep, 'beepHighShort')

      connect(main.cost_counter, 'costs', status_line, 'onUpdateCosts')

      connect(main.microphone, 'time_recorded', status_line, 'onUpdateTimeRecorded')

      app.updateStatusLeft(status_line.getStatusLineLeft())
      app.updateStatusCenter(status_line.getStatusLineCenter())
      app.updateStatusRight(status_line.getStatusLineRight())

      app.run()
  print('exited.')
