# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from functools import partial
from transcriber import Transcriber
from post_processor import PostProcessor
from pipeline import Pipeline
from audio_tools import normaliseFormat
from pydub import AudioSegment
from output import Output
from read_context import readContext
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

if __name__ == '__main__':
  print('running...')

  logger = logger.get(__name__)

  parser = argparse.ArgumentParser(description='dictate')
  parser.add_argument('--context', type=str, required=True, help='context')
  parser.add_argument('--output', type=str, default=None, help='output file')
  parser.add_argument('--enable-vad', action='store_true', default=False, help='enable VAD')
  args = parser.parse_args()

  context = readContext(args.context)
  chat_gpt = ChatGpt(context)

  microphone = Microphone()
  pipeline_assembly = [ microphone ]
  if args.enable_vad:
    from vad import Vad
    vad = Vad()
    pipeline_assembly.append(vad)
  transcriber = Transcriber(context.language)
  pipeline_assembly.append(transcriber)
  post_processor = PostProcessor(chat_gpt)
  pipeline_assembly.append(post_processor)
  pipeline_assembly.append(Output(args.output))
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

      if args.enable_vad:
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
