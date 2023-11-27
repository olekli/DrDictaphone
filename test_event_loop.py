# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from event_loop import EventLoop, connect, associateWithEventLoop
from events import Events

class DummyClass:
  def __init__(self):
    self.events = Events(('new_result', 'updated'))
    self.new_result = []
    self.updated = []

  def onNewResult(self, item):
    self.new_result.append(item)

  def onUpdated(self, item):
    self.updated.append(item)

@pytest.mark.parametrize("event_name, slot_name, other", [
  ( 'new_result', 'onNewResult', 'updated' ),
  ( 'updated', 'onUpdated', 'new_result' )
])
def test_single_connect_works(event_name, slot_name, other):
  sender = DummyClass()
  receiver = DummyClass()

  with EventLoop() as event_loop:
    associateWithEventLoop(sender, event_loop)
    associateWithEventLoop(receiver, event_loop)
    connect(sender, event_name, receiver, slot_name)

    getattr(sender.events, event_name)('foo')
    getattr(sender.events, event_name)('bar')
    getattr(sender.events, event_name)('baz')

  assert getattr(receiver, event_name) == [ 'foo', 'bar', 'baz' ]
  assert getattr(receiver, other) == []

def test_double_connect_works():
  sender = DummyClass()
  receiver = DummyClass()

  with EventLoop() as event_loop:
    associateWithEventLoop(sender, event_loop)
    associateWithEventLoop(receiver, event_loop)
    connect(sender, 'new_result', receiver, 'onNewResult')
    connect(sender, 'updated', receiver, 'onUpdated')

    sender.events.new_result('foo')
    sender.events.updated('bar')
    sender.events.updated('lol')
    sender.events.new_result('baz')

  assert getattr(receiver, 'new_result') == [ 'foo', 'baz' ]
  assert getattr(receiver, 'updated') == [ 'bar', 'lol' ]

def test_full_connect_works():
  sender = DummyClass()
  receiver = DummyClass()

  with EventLoop() as event_loop:
    associateWithEventLoop(sender, event_loop)
    associateWithEventLoop(receiver, event_loop)
    connect(sender, None, receiver, None)

    sender.events.new_result('foo')
    sender.events.updated('bar')
    sender.events.updated('lol')
    sender.events.new_result('baz')

  assert getattr(receiver, 'new_result') == [ 'foo', 'baz' ]
  assert getattr(receiver, 'updated') == [ 'bar', 'lol' ]
