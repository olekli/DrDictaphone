# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from mreventloop import emits
from events import Events
from functools import partial
from drdictaphone import logger

logger = logger.get(__name__)

def call_in_event_loop(method):
  def wrapper(self, *args, **kwargs):
    if self.app.loop:
      self.app.loop.call_soon_threadsafe(partial(method, self, *args, **kwargs))
    else:
      method(self, *args, **kwargs)
  return wrapper

@emits('events', [ 'start_rec', 'stop_rec', 'pause_mic', 'unpause_mic', 'clear_buffer' ])
class App:
  def __init__(self):
    self.bindings = self.makeKeyBinds()
    self.text_area = TextArea(focusable = False, read_only = True)
    self.status_bar_left = Window(
      content = FormattedTextControl('loading...'),
      height=1,
      align=WindowAlign.LEFT,
    )
    self.status_bar_center = Window(
      height=1,
      align=WindowAlign.CENTER,
    )
    self.status_bar_right = Window(
      height=1,
      align=WindowAlign.RIGHT,
    )
    self.layout = Layout(
      HSplit([
        self.text_area,
        VSplit([
          self.status_bar_left,
          self.status_bar_center,
          self.status_bar_right
        ])
      ])
    )
    self.app = Application(
      layout = self.layout,
      key_bindings = self.bindings,
      full_screen = True,
      mouse_support = False
    )

    self.is_recording = False
    self.is_paused = False

  def makeKeyBinds(self):
    bindings = KeyBindings()

    bindings.add(' ')(lambda event: self.togglePauseMic())
    bindings.add('p')(lambda event: self.toggleRecording())
    bindings.add('q')(lambda event: self.exit())
    bindings.add(Keys.Vt100MouseEvent)(self.onMouseEvent)
    bindings.add('c')(lambda event: self.events.clear_buffer())

    return bindings

  def onMouseEvent(self, event):
    data = event.key_sequence[0].data.split(';')
    if data[0] == '\x1b[<0' and data[2][-1] == 'm': # dafuq...
      self.togglePauseMic()
    elif data[0] == '\x1b[<2' and data[2][-1] == 'm': # dafuq...
      self.toggleRecording()

  def togglePauseMic(self):
    if self.is_recording:
      if not self.is_paused:
        self.events.pause_mic()
        self.is_paused = True
      else:
        self.events.unpause_mic()
        self.is_paused = False

  def toggleRecording(self):
    self.is_paused = False
    if self.is_recording:
      self.events.stop_rec()
      self.is_recording = False
    else:
      self.events.start_rec()
      self.is_recording = True

  def exit(self):
    self.app.exit()

  @call_in_event_loop
  def updateText(self, new_text):
    self.text_area.text = new_text
    self.app.invalidate()

  @call_in_event_loop
  def updateStatusLeft(self, new_status):
    self.status_bar_left.content = FormattedTextControl(new_status)
    self.app.invalidate()

  @call_in_event_loop
  def updateStatusCenter(self, new_status):
    self.status_bar_center.content = FormattedTextControl(new_status)
    self.app.invalidate()

  @call_in_event_loop
  def updateStatusRight(self, new_status):
    self.status_bar_right.content = FormattedTextControl(new_status)
    self.app.invalidate()

  def run(self):
    self.app.run()
