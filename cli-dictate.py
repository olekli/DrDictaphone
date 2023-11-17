# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from transcriber import Transcriber
from post_processor import PostProcessor
from pipeline import Pipeline
from collector import Collector
from dispatcher import Dispatcher
from recorder import Recorder
from audio_tools import normaliseFormat
from pydub import AudioSegment
from output import Output
from read_context import readContext

parser = argparse.ArgumentParser(description='dictate')
parser.add_argument('--context', type=str, required=True, help='context')
parser.add_argument('--topic', type=str, default='', help='topic')
parser.add_argument('--input', type=str, default=None, help='input file')
parser.add_argument('--output', type=str, default=None, help='output file')
args = parser.parse_args()

context = readContext(args.context)
transcriber = Transcriber(context.language)
post_processor = PostProcessor(context, args.topic)
collector = Collector(Pipeline(transcriber, post_processor))
output = Output(args.output)

if args.input:
  audio_segment = AudioSegment.from_file(args.input)
  audio_segment = normaliseFormat(audio_segment)
  with Dispatcher(collector) as dispatcher:
    dispatcher(audio_segment)
else:
  with Dispatcher(collector) as dispatcher:
    with Recorder(dispatcher):
      input()
output(collector.content)
