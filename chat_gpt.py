# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import json

client = OpenAI(api_key = os.environ.get('API_KEY', ''))

tools = [
  {
    "type": "function",
    "function": {
      "name": "ok_result",
      "description": "Use this function with your result if you could follow the instructions given to you.",
      "parameters": {
        "type": "object",
        "properties": {
          "ok": {
            "type": "string",
            "description": "Your result from following the instructions.",
          }
        },
        "required": [ "ok" ]
      },
    }
  },
  {
    "type": "function",
    "function": {
      "name": "err_result",
      "description": "Use this function to give feedback in case you could not follow the instructions given to you.",
      "parameters": {
        "type": "object",
        "properties": {
          "err": {
            "type": "string",
            "description": "Your description of the problem with the instructions.",
          }
        },
        "required": [ "err" ]
      },
    }
  },
]

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
    options['tools'] = tools
    options['n'] = 1

    if 'messages' in conversation.context.options:
      del conversation.context.options['messages']

    self._last_completion = client.chat.completions.create(
      messages = messages,
      **options
    )
    func = self._last_completion.choices[0].message.tool_calls[0].function
    return json.loads(func.arguments)

  def getLast(self):
    return self._last_completion
