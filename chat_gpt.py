# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import json
import logger

logger = logger.get(__name__)

class ChatGpt:
  cost_prompt = 1
  cost_completion = 3

  def __init__(self):
    self._last_completion = None
    self.prompt_tokens = 0
    self.completion_tokens = 0
    self.total_tokens = 0
    self.total_cost = 0

  @staticmethod
  def _makeMessage(role, content):
    return {
      'role': role,
      'content': content
    }

  def makeMessages(self, conversation):
    return \
      [ self._makeMessage('system', m) for m in conversation.context.system ] + \
      ([ self._makeMessage('system', conversation.topic) ] if conversation.topic else []) + \
      [
        item
        for exchange in conversation.history
        for item in [
          self._makeMessage('user', exchange.user_message),
          self._makeMessage('assistant', exchange.assistant_message)
        ]
      ]

  def ask(self, conversation, question):
    messages = self.makeMessages(conversation) + [ self._makeMessage('user', question) ]

    options = conversation.context.options.model_dump()
    options.setdefault('model', 'gpt-3.5-turbo')
    options.setdefault('temperature', 0.5)
    options.setdefault('max_tokens', 1000)
    options['stream'] = False
    if conversation.context.tools:
      options['tools'] = conversation.context.tools
    options['n'] = 1

    logger.debug(f'options: {options}')
    logger.debug(f'messages: {messages}')

    if 'messages' in conversation.context.options:
      del conversation.context.options['messages']

    client = OpenAI(api_key = os.environ.get('API_KEY', ''))
    self._last_completion = client.chat.completions.create(
      messages = messages,
      **options
    )
    usage = self._last_completion.usage
    self.prompt_tokens += usage.prompt_tokens
    self.completion_tokens += usage.completion_tokens
    self.total_tokens += usage.total_tokens
    self.total_cost = ((self.completion_tokens * ChatGpt.cost_completion) + \
      (self.prompt_tokens * ChatGpt.cost_prompt)) / 1000
    logger.debug(f'total cost: {round(self.total_cost)}')

    tool_calls = self._last_completion.choices[0].message.tool_calls
    if not tool_calls:
      return { 'err': 'No function called' }
    else:
      func = tool_calls[0].function
      return json.loads(func.arguments)

  def getLast(self):
    return self._last_completion
