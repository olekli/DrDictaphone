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
import logger_config
import logger

if __name__ == '__main__':
  logger = logger.get(__name__)

  parser = argparse.ArgumentParser(description='dictate')
  parser.add_argument('--context', type=str, required=True, help='context')
  parser.add_argument('--topic', type=str, default='', help='topic')
  parser.add_argument('--input', type=str, default=None, help='input file')
  parser.add_argument('--output', type=str, default=None, help='output file')
  args = parser.parse_args()

  context = readContext(args.context)
  chat_gpt = ChatGpt(context)

  if args.input:
    logger.info(f'Processing audio file: {args.input} ...')
    audio_segment = AudioSegment.from_file(args.input)
    audio_segment = normaliseFormat(audio_segment)
    assert False
  else:
    logger.info(f'Starting listening...')
    status_line = StatusLine()
    with Display(status_line) as display:
      with Pipeline(
        [
          partial(Microphone, 1),
          Vad,
          FenceBeep,
          partial(Transcriber, context.language),
          partial(PostProcessor, chat_gpt),
          partial(Output, args.output)
        ],
        display
      ):
        input()
      logger.info(f'total costs incurred: {display.total_cost / 100:.2f}$')
  logger.info(f'done')
