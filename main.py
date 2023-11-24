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

  #status_line = StatusLine()
  with Pipeline(
    [
      partial(Microphone, 1),
      Vad,
      FenceBeep,
      partial(Transcriber, context.language),
      partial(PostProcessor, chat_gpt),
      partial(Output, args.output),
      Aggregator
    ],
    None
  ) as pipeline:
    app = App()
    pipeline['Aggregator'].result += app.updateText
    app.run()
  logger.info(f'total costs incurred: {display.total_cost / 100:.2f}$')
  logger.info(f'done')
