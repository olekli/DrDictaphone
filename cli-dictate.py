# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from transcriber import Transcriber
from post_processor import PostProcessor
from pipeline import Pipeline
from audio_tools import normaliseFormat
from pydub import AudioSegment
from output import Output
from read_context import readContext
from microphone import Microphone
from vad import Vad
import logger_config
import logger

logger = logger.get(__name__)

parser = argparse.ArgumentParser(description='dictate')
parser.add_argument('--context', type=str, required=True, help='context')
parser.add_argument('--topic', type=str, default='', help='topic')
parser.add_argument('--input', type=str, default=None, help='input file')
parser.add_argument('--output', type=str, default=None, help='output file')
args = parser.parse_args()

context = readContext(args.context)
vad = Vad()
transcriber = Transcriber(context.language)
post_processor = PostProcessor(context, args.topic)
output = Output(args.output)

if args.input:
  logger.info(f'Processing audio file: {args.input} ...')
  audio_segment = AudioSegment.from_file(args.input)
  audio_segment = normaliseFormat(audio_segment)
  with Pipeline([transcriber, post_processor, output]) as pipeline:
    pipeline(audio_segment)
else:
  logger.info(f'Starting listening...')
  with Pipeline([vad, transcriber, post_processor, output]) as pipeline:
    with Microphone(segment_length = 1, result_callback = pipeline):
      input()
logger.info(f'done')
logger.info(f'total costs incurred: {(transcriber.total_cost + post_processor.chat_gpt.total_cost) / 100}$')
