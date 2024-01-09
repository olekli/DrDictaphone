# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
import argparse
from drdictaphone.chat_gpt import ChatGpt
from drdictaphone.read_context import readContext

parser = argparse.ArgumentParser(description='gpt-prompt cli')
parser.add_argument('--context', type = str, required = True, help = 'context')
parser.add_argument('--input', type = str, required = True, help = 'input filename')
parser.add_argument('--output', type = str, default = None, help = 'output filename')
args = parser.parse_args()

async def main():
  gpt = ChatGpt(readContext(args.context))
  with open(args.input, 'rt') as file:
    input = file.read()
  result = await gpt.ask(input)
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

asyncio.run(main())
