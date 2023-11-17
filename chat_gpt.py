# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os

client = OpenAI(api_key = os.environ.get('API_KEY', ''))

class ChatGpt:
  def __init__(self):
    self._last_completion = None

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
    options['n'] = 1

    if 'messages' in conversation.context.options:
      del conversation.context.options['messages']

    self._last_completion = client.chat.completions.create(
      messages = messages,
      **options
    )
    return self._last_completion

  def getResult(self):
    return self._last_completion
