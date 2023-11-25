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
from vad import Vad
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
  args = parser.parse_args()

  context = readContext(args.context)
  chat_gpt = ChatGpt(context)
  aggregator = Aggregator()

  vad = Vad()
  transcriber = Transcriber(context.language)
  post_processor = PostProcessor(chat_gpt)
  with Microphone(1) as microphone:
    with Pipeline(
      [
        microphone,
        vad,
        FenceBeep(),
        transcriber,
        post_processor,
        Output(args.output),
        aggregator
      ]
    ) as pipeline:
      with EventLoop() as main_loop:
        app = App()
        associateWithEventLoop(app, main_loop)

        status_line = StatusLine()
        associateWithEventLoop(status_line, main_loop)
        connect(vad.__event_loop__, 'active', status_line, 'onVADactive')
        connect(vad.__event_loop__, 'idle', status_line, 'onVADidle')
        connect(transcriber.__event_loop__, 'active', status_line, 'onTRANSactive')
        connect(transcriber.__event_loop__, 'idle', status_line, 'onTRANSidle')
        connect(post_processor.__event_loop__, 'active', status_line, 'onPOSTactive')
        connect(post_processor.__event_loop__, 'idle', status_line, 'onPOSTidle')

        connect(status_line, 'status_update', app, 'onUpdateStatus')
        connect(aggregator, 'result', app, 'onUpdateText')

        app.run()
  #logger.info(f'total costs incurred: {display.total_cost / 100:.2f}$')
  logger.info(f'done')
