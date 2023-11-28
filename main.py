# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import sys
import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from transcriber import Transcriber
from post_processor import PostProcessor
from pipeline import Pipeline
from audio_tools import normaliseFormat
from pydub import AudioSegment
from output import Output
from config import readProfile, makeOutputFilename, getProfilePath, createSkel
from microphone import Microphone
from beep import Beep
from status_line import StatusLine
from display import Display
from chat_gpt import ChatGpt
from aggregator import Aggregator
from app import App
from event_loop import EventLoop, connect, associateWithEventLoop
from cost_counter import CostCounter
import logger_config
import logger

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

  createSkel()

  if len(sys.argv) > 1:
    parser = argparse.ArgumentParser(description = 'DrDictaphone')
    parser.add_argument('profile', type = str, default = 'default', help = 'profile to use')
    parser.add_argument('--output', type = str, default = None, help = 'output file')
    args = parser.parse_args()

    profile = readProfile(getProfilePath(args.profile))

    if args.output == None:
      output = makeOutputFilename(profile.output)
    else:
      output = args.output
  else:
    profile_path = getProfilePath(promptForProfile())
    os.utime(profile_path, None)
    profile = readProfile(profile_path)
    output = makeOutputFilename(profile.output)

  print('running...')

  chat_gpt = ChatGpt(profile.post_processor)

  microphone = Microphone()
  pipeline_assembly = [ microphone ]
  if profile.enable_vad:
    from vad import Vad
    vad = Vad()
    pipeline_assembly.append(vad)
  transcriber = Transcriber(profile.language)
  pipeline_assembly.append(transcriber)
  post_processor = PostProcessor(chat_gpt)
  pipeline_assembly.append(post_processor)
  pipeline_assembly.append(Output(output))
  aggregator = Aggregator()
  pipeline_assembly.append(aggregator)
  cost_counter = CostCounter()
  with Pipeline(pipeline_assembly) as pipeline:
    with EventLoop() as main_loop, EventLoop() as beep_loop:
      associateWithEventLoop(pipeline, main_loop)
      associateWithEventLoop(cost_counter, main_loop)

      app = App()
      associateWithEventLoop(app, main_loop)

      status_line = StatusLine()
      associateWithEventLoop(status_line, main_loop)
      connect(microphone, 'active', status_line, 'onMICactive')
      connect(microphone, 'idle', status_line, 'onMICidle')
      connect(transcriber.__event_loop__, 'active', status_line, 'onTRANSactive')
      connect(transcriber.__event_loop__, 'idle', status_line, 'onTRANSidle')
      connect(post_processor.__event_loop__, 'active', status_line, 'onPOSTactive')
      connect(post_processor.__event_loop__, 'idle', status_line, 'onPOSTidle')

      connect(status_line, 'status_update_left', app, 'updateStatusLeft')
      connect(status_line, 'status_update_center', app, 'updateStatusCenter')
      connect(status_line, 'status_update_right', app, 'updateStatusRight')
      connect(aggregator, 'result', app, 'updateText')

      connect(app, 'start_rec', pipeline, 'onStartRec')
      connect(app, 'stop_rec', pipeline, 'onStopRec')
      connect(app, 'pause_mic', pipeline, 'onPauseMic')
      connect(app, 'unpause_mic', pipeline, 'onUnpauseMic')

      beep = Beep()
      associateWithEventLoop(beep, beep_loop)

      if profile.enable_vad:
        connect(vad, 'active', status_line, 'onVADactive')
        connect(vad, 'idle', status_line, 'onVADidle')
        connect(app, 'start_vad', pipeline, 'onStartVad')
        connect(app, 'stop_vad', pipeline, 'onStopVad')
        connect(app, 'start_vad', beep, 'beepHighLong')
        connect(app, 'stop_vad', beep, 'beepLowLong')

      connect(app, 'start_rec', beep, 'beepHighLong')
      connect(app, 'stop_rec', beep, 'beepLowLong')
      connect(app, 'pause_mic', beep, 'beepLowShort')
      connect(app, 'unpause_mic', beep, 'beepHighShort')

      connect(transcriber, 'costs', cost_counter, 'addCosts')
      connect(post_processor, 'costs', cost_counter, 'addCosts')
      connect(cost_counter, 'updated', status_line, 'onUpdateCosts')

      connect(microphone, 'time_recorded', status_line, 'onUpdateTimeRecorded')

      app.updateStatusLeft(status_line.getStatusLineLeft())
      app.updateStatusCenter(status_line.getStatusLineCenter())
      app.updateStatusRight(status_line.getStatusLineRight())

      app.run()
  print('exited.')
