# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from event_loop import EventLoop, connect, associateWithEventLoop, forwardEvents
from events import Events
from event_spy import EventSpy

class DummyClass:
  def __init__(self):
    self.events = Events(('new_result', 'updated', 'forward1', 'forward2'))
    self.new_result = []
    self.updated = []

  def onNewResult(self, item):
    self.new_result.append(item)

  def onUpdated(self, item):
    self.updated.append(item)

class Spy:
  def __init__(self):
    self.forward1 = []
    self.forward2 = []

  def onForward1(self, item):
    logger.debug(item)
    self.forward1.append(item)

  def onForward2(self, item):
    logger.debug(item)
    self.forward2.append(item)

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
    sender.events.forward1('123')
    sender.events.new_result('baz')
    sender.events.forward2('456')

  assert getattr(receiver, 'new_result') == [ 'foo', 'baz' ]
  assert getattr(receiver, 'updated') == [ 'bar', 'lol' ]

def test_forward_works():
  sender = DummyClass()
  spy = EventSpy([ 'forward1', 'forward2' ])

  with EventLoop() as event_loop:
    associateWithEventLoop(sender, event_loop)
    associateWithEventLoop(spy, event_loop)
    forwardEvents(sender, [ 'forward1', 'forward2' ])
    connect(sender, 'forward1', spy, 'onForward1')
    connect(sender, 'forward2', spy, 'onForward2')

    sender.events.forward1('123')
    sender.events.forward2('456')

  assert getattr(spy, 'forward1') == [ '123' ]
  assert getattr(spy, 'forward2') == [ '456' ]
