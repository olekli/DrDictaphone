# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from chat_gpt import ChatGpt
from model.Conversation import Conversation
from events import Events
import yaml
import logger

logger = logger.get(__name__)

class PostProcessor:
  def __init__(self, context, topic = '', more_pp = False):
    self.context = context
    self.topic = topic
    self.more_pp = more_pp
    self.events = Events(('result', 'fence'))
    self.text_buffer = ''
    self.conversation = Conversation(context = self.context, topic = self.topic, history = [])

    with open('instructions/post_process.yaml', 'rt') as file:
      instructions = yaml.safe_load(file)
    self.context.system = instructions + self.context.system
    self.chat_gpt = ChatGpt()

  def onResult(self, text):
    self.text_buffer = text
    self.events.result(text)

    if self.more_pp:
      response = self.chat_gpt.ask(self.conversation, text)
      if 'ok' in response:
        logger.debug(f'post replied ok: {response["ok"]}')
        logger.debug(f'input was: {text}')
        self.events.result(response['ok'])
      else:
        logger.warning(f'post replied with error: {response["err"]}')
        logger.warning(f'input was: {text}')

  def onFence(self):
    if len(self.text_buffer) > 0:
      response = self.chat_gpt.ask(self.conversation, self.text_buffer)
      if 'ok' in response:
        logger.debug(f'post replied ok: {response["ok"]}')
        logger.debug(f'input was: {self.text_buffer}')
        self.text_buffer = ''
        self.events.result(response['ok'])
      else:
        logger.warning(f'post replied with error: {response["err"]}')
        logger.warning(f'input was: {self.text_buffer}')
      self.events.fence()
