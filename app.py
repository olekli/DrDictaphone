# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from events import Events
import logger

logger = logger.get(__name__)

class App:
  def __init__(self):
    self.events = Events(('start_recording', 'stop_recording', 'start_stream', 'stop_stream', 'start_vad', 'stop_vad'))
    self.bindings = self.makeKeyBinds()
    self.text_area = TextArea(focusable = False, read_only = True)
    self.status_bar = Window(content = FormattedTextControl('LOADING'), height=1)
    self.layout = Layout(HSplit([self.text_area, self.status_bar]))
    self.app = Application(layout = self.layout, key_bindings = self.bindings, full_screen = True)

    self.is_recording = False
    self.is_vad = False

  def makeKeyBinds(self):
    bindings = KeyBindings()

    bindings.add('q')(lambda event: self.exit())
    bindings.add('v')(lambda event: self.toggleVad())
    bindings.add(' ')(lambda event: self.toggleRecording())

    return bindings

  def toggleRecording(self):
    if not self.is_vad:
      if self.is_recording:
        self.events.stop_recording()
        self.is_recording = False
      else:
        self.events.start_recording()
        self.is_recording = True

  def toggleVad(self):
    if not self.is_recording:
      if self.is_vad:
        self.events.stop_stream()
        self.is_vad = False
      else:
        self.events.start_vad()
        self.events.start_stream()
        self.is_vad = True

  def exit(self):
    self.app.exit()

  def updateText_(self, new_text):
    self.text_area.text = new_text
    self.app.invalidate()

  def onUpdateText(self, new_text):
    self.app.loop.call_soon_threadsafe(lambda: self.updateText_(new_text))

  def updateStatus_(self, new_status):
    self.status_bar.content = FormattedTextControl(new_status)
    self.app.invalidate()

  def onUpdateStatus(self, new_status):
    self.app.loop.call_soon_threadsafe(lambda: self.updateStatus_(new_status))

  def run(self):
    self.app.run()
