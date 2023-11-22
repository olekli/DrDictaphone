# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from chat_gpt import ChatGpt
from model.Conversation import Conversation
from events import Events
import yaml
import logger

logger = logger.get(__name__)

class PostProcessor:
  def __init__(self, context, topic = ''):
    self.context = context
    self.topic = topic
    self.events = Events(('final_result', 'temporary_result'))
    self.text_buffer = []

    with open('instructions/post_process.yaml', 'rt') as file:
      instructions = yaml.safe_load(file)
    self.context.system = instructions + self.context.system
    self.chat_gpt = ChatGpt()

  def onFinalResult(self, text):
    self.text_buffer.append(text)
    input = ' '.join(self.text_buffer)

    self.events.temporary_result(input)

    conversation = Conversation(context = self.context, topic = self.topic, history = [])
    if input[-1] == '.' and len(input) > 300:
      response = self.chat_gpt.ask(conversation, input)
      if 'ok' in response:
        logger.debug(f'post replied ok: {response["ok"]}')
        logger.debug(f'input was: {input}')
        if len(input) > 300:
          self.text_buffer = []
          self.events.final_result(response['ok'])
        else:
          self.events.temporary_result(response['ok'])
      else:
        logger.warning(f'post replied with error: {response["err"]}')
        logger.warning(f'input was: {input}')

  def onTemporaryResult(self, audio_segment):
    assert False
