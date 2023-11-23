# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from post_processor import PostProcessor
import logger_config

class DummyGpt:
  def __init__(self):
    self.question = None
    self.response = None

  def ask(self, question):
    self.question = question
    return self.response

class Spy:
  def __init__(self):
    self.content = []
    self.fenced = False

  def onResult(self, result):
    self.content.append(result)

  def onFence(self):
    self.fenced = True

def make():
  gpt = DummyGpt()
  spy = Spy()
  post_processor = PostProcessor(gpt)
  post_processor.events.result += spy.onResult
  post_processor.events.fence += spy.onFence

  return (gpt, spy, post_processor)

def test_forwards_text_onResult():
  gpt, spy, post_processor = make()

  post_processor.onResult('text1')

  assert spy.content == [ 'text1' ]
  assert not spy.fenced

def test_does_not_retain_text_onResult():
  gpt, spy, post_processor = make()

  post_processor.onResult('text1')
  post_processor.onResult('text2')

  assert spy.content == [ 'text1', 'text2' ]
  assert not spy.fenced

def test_calls_chat_gpt_onFence():
  gpt, spy, post_processor = make()
  gpt.response = { 'ok': 'foo' }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()

  assert gpt.question == 'text2'

@pytest.mark.parametrize("coherent", [
  { 'coherent': True },
  { 'coherent': False },
  {},
])
def test_fence_produces_result_on_ok_response(coherent):
  gpt, spy, post_processor = make()
  gpt.response = { 'ok': 'foo', **coherent }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()

  assert spy.content[-1] == 'foo'

def test_fence_produces_no_result_on_err_response():
  gpt, spy, post_processor = make()
  gpt.response = { 'err': 'foo' }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()

  assert spy.content[-1] == 'text2'

def test_fences_on_coherent_ok_response():
  gpt, spy, post_processor = make()
  gpt.response = { 'ok': 'foo', 'coherent': True }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()

  assert spy.fenced

@pytest.mark.parametrize("coherent", [
  { 'coherent': False },
  {},
])
def test_does_not_fence_on_non_coherent_ok_response(coherent):
  gpt, spy, post_processor = make()
  gpt.response = { 'ok': 'foo', **coherent }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()

  assert not spy.fenced

def test_does_not_fence_on_err_response():
  gpt, spy, post_processor = make()
  gpt.response = { 'err': 'foo' }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()

  assert not spy.fenced

def test_fencing_clears_internal_buffer():
  gpt, spy, post_processor = make()
  gpt.response = { 'ok': 'foo', 'coherent': True }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()
  post_processor.onResult('text3')

  assert spy.content[-1] == 'text3'

@pytest.mark.parametrize("key, coherent", [
  ( 'ok', { 'coherent': False } ),
  ( 'ok', {} ),
  ( 'err', {} )
])
def test_not_fencing_stores_internal_buffer(key, coherent):
  gpt, spy, post_processor = make()
  gpt.response = { key: 'foo', **coherent }

  post_processor.onResult('text1')
  post_processor.onResult('text2')
  post_processor.onFence()
  post_processor.onResult('text3')

  assert spy.content[-1] == 'text2 text3'
