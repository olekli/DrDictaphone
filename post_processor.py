# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from chat_gpt import ChatGpt
from model.Conversation import Conversation
from events import Events
import logger

logger = logger.get(__name__)

tools = [
  {
    "type": "function",
    "function": {
      "name": "partial_result",
      "description": "Use this function with your result if you could follow the instructions given to you, but feel like the input may have been incomplete or the result does not make sense.",
      "parameters": {
        "type": "object",
        "properties": {
          "partial": {
            "type": "string",
            "description": "Your result from following the instructions on an incomplete input.",
          }
        },
        "required": [ "partial" ]
      },
    }
  },
  {
    "type": "function",
    "function": {
      "name": "ok_result",
      "description": "Use this function with your result if you could follow the instructions given to you and you feel like the input was complete.",
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

class PostProcessor:
  def __init__(self, context, topic = ''):
    self.context = context
    self.topic = topic
    self.events = Events(( 'result' ))
    self.text_buffer = []

    self.chat_gpt = ChatGpt()

  def __call__(self, text):
    conversation = Conversation(context = self.context, topic = self.topic, history = [])
    input = ' '.join(self.text_buffer + [text])
    response = self.chat_gpt.ask(conversation, input, tools)
    if 'ok' in response:
      logger.debug(f'post replied full: {response["ok"]}')
      logger.debug(f'input was: {input}')
      self.text_buffer = []
      self.events.result(response['ok'])
    elif 'partial' in response:
      logger.debug(f'post replied partial: {response["partial"]}')
      logger.debug(f'input was: {input}')
      self.text_buffer.append(response['partial'])
    else:
      logger.debug(f'post replied with error: {response["err"]}')
      logger.debug(f'input was: {input}')
      self.text_buffer.append(text)
