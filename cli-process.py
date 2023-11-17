# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse

from chat_gpt import ChatGpt
from model.Conversation import Conversation
from read_context import readContext

parser = argparse.ArgumentParser(description='gpt-prompt cli')
parser.add_argument('--context', type = str, required = True, help = 'context')
parser.add_argument('--topic', type = str, default = '', help = 'topic')
parser.add_argument('--input', type = str, required = True, help = 'input filename')
parser.add_argument('--output', type = str, default = None, help = 'output filename')
args = parser.parse_args()

gpt = ChatGpt()
conversation = Conversation(
  context = readContext(args.context),
  topic = args.topic,
  history = []
)
with open(args.input, 'rt') as file:
  input = file.read()
result = gpt.ask(conversation, input)
if 'ok' in result:
  if args.output:
    with open(args.output, 'wt') as file:
      file.write(result['ok'])
  else:
    print(result['ok'])
elif 'err' in result:
  print(f'Error: {result["err"]}')
else:
  print('Error')
