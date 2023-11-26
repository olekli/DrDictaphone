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
from fence_beep import FenceBeep
from status_line import StatusLine
from display import Display
from chat_gpt import ChatGpt
from aggregator import Aggregator
from app import App
from event_loop import EventLoop, connect, associateWithEventLoop
import logger_config
import logger

if __name__ == '__main__':
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
  pipeline_assembly.append(FenceBeep())
  transcriber = Transcriber(context.language)
  pipeline_assembly.append(transcriber)
  post_processor = PostProcessor(chat_gpt)
  pipeline_assembly.append(post_processor)
  pipeline_assembly.append(Output(args.output))
  aggregator = Aggregator()
  pipeline_assembly.append(aggregator)
  with Pipeline(pipeline_assembly) as pipeline:
    with EventLoop() as main_loop:
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

      connect(status_line, 'status_update', app, 'onUpdateStatus')
      connect(aggregator, 'result', app, 'onUpdateText')

      connect(app, 'start_recording', microphone, 'startRecording')
      connect(app, 'stop_recording', microphone, 'stop')

      if args.enable_vad:
        connect(vad, 'active', status_line, 'onVADactive')
        connect(vad, 'idle', status_line, 'onVADidle')
        connect(app, 'start_vad', vad, 'enable')
        connect(app, 'start_stream', microphone, 'startStream')
        connect(app, 'stop_stream', microphone, 'stop')

      app.run()
  #logger.info(f'total costs incurred: {display.total_cost / 100:.2f}$')
  logger.info(f'done')
