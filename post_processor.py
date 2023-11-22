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
    conversation = Conversation(context = self.context, topic = self.topic, history = [])
    input = ' '.join(self.text_buffer + [text])
    response = self.chat_gpt.ask(conversation, input)
    if 'ok' in response:
      logger.debug(f'post replied full: {response["ok"]}')
      logger.debug(f'input was: {input}')
      self.text_buffer = []
      self.events.final_result(response['ok'])
    elif 'partial' in response:
      logger.debug(f'post replied partial: {response["partial"]}')
      logger.debug(f'input was: {input}')
      self.text_buffer.append(response['partial'])
    else:
      logger.debug(f'post replied with error: {response["err"]}')
      logger.debug(f'input was: {input}')
      self.text_buffer.append(text)

  def onTemporaryResult(self, audio_segment):
    assert False
