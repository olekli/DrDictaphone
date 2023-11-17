# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from chat_gpt import ChatGpt
from model.Conversation import Conversation

class PostProcessor:
  def __init__(self, context, topic = ''):
    self.context = context
    self.topic = topic
    self.chat_gpt = ChatGpt()

  def __call__(self, textual_context, text):
    conversation = Conversation(context = self.context, topic = self.topic, history = [])
    response = self.chat_gpt.ask(conversation, text)
    if 'ok' in response:
      return response['ok']
    else:
      return text
