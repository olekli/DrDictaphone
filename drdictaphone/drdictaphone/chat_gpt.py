# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
from openai import OpenAI
from drdictaphone.config import config
import json
from drdictaphone import logger

logger = logger.get(__name__)

def makeMessage(role, content):
  return {
    'role': role,
    'content': content
  }

class ChatGpt:
  def __init__(self, context):
    self.context = context

    self.last_completion = None
    self.prompt_tokens = 0
    self.completion_tokens = 0
    self.total_tokens = 0
    self.total_cost = 0
    self.last_cost = 0

    self.messages = [ makeMessage('system', m) for m in self.context.instructions ]
    if self.context.topic:
      self.messages += [ makeMessage('system', m) for m in self.context.topic ]

  async def ask(self, question):
    this_messages = list(self.messages)
    this_messages += [ makeMessage('user', question) ]

    options = dict(self.context.options)
    options['model'] = self.context.gpt_model.name
    options['stream'] = False
    if self.context.tools:
      options['tools'] = self.context.tools
    options['n'] = 1

    logger.debug(f'options: {options}')
    logger.debug(f'messages: {this_messages}')

    client = OpenAI(api_key = config['openai_api_key'])
    self.last_completion = await asyncio.get_event_loop().run_in_executor(
      None,
      lambda: client.chat.completions.create(messages = this_messages, **options)
    )
    usage = self.last_completion.usage
    self.prompt_tokens += usage.prompt_tokens
    self.completion_tokens += usage.completion_tokens
    self.total_tokens += usage.total_tokens
    self.total_cost = ((self.completion_tokens * self.context.gpt_model.output_cost) + \
      (self.prompt_tokens * self.context.gpt_model.input_cost)) / 1000
    self.last_cost = ((usage.completion_tokens * self.context.gpt_model.output_cost) + \
      (usage.prompt_tokens * self.context.gpt_model.input_cost)) / 1000
    logger.debug(f'total cost: {round(self.total_cost)}')

    tool_calls = self.last_completion.choices[0].message.tool_calls
    if not tool_calls:
      return { 'err': 'No function called' }
    else:
      func = tool_calls[0].function
      return json.loads(func.arguments)
