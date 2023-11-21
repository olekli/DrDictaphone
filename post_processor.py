# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from chat_gpt import ChatGpt
from model.Conversation import Conversation
from events import Events
import logger

logger = logger.get(__name__)

class PostProcessor:
  def __init__(self, context, topic = ''):
    self.context = context
    self.topic = topic

    self.events = Events(( 'result' ))
    self.chat_gpt = ChatGpt()

  def __call__(self, textual_context, text):
    conversation = Conversation(context = self.context, topic = self.topic, history = [])
    response = self.chat_gpt.ask(conversation, text)
    if 'ok' in response:
      logger.debug(f'post replied: {response["ok"]}')
      logger.debug(f'input was: {text}')
      self.events.result(response['ok'])
    else:
      logger.debug(f'post replied with error: {response["err"]}')
      logger.debug(f'input was: {text}')
      self.events.result(text)
