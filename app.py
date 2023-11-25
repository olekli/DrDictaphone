# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from events import Events
import logger

logger = logger.get(__name__)

class App:
  def __init__(self):
    self.bindings = self.makeKeyBinds()
    self.text_area = TextArea(focusable = False, read_only = True)
    self.status_bar = Window(content = FormattedTextControl('LOADING'), height=1)
    self.layout = Layout(HSplit([self.text_area, self.status_bar]))
    self.app = Application(layout = self.layout, key_bindings = self.bindings, full_screen = True)

  def makeKeyBinds(self):
    bindings = KeyBindings()
    bindings.add('q')(lambda event: self.exit())
    return bindings

  def exit(self):
    self.app.exit()

  def updateText_(self, new_text):
    logger.debug(f'onUpdateText_: {new_text}')
    self.text_area.text = new_text
    self.app.invalidate()

  def onUpdateText(self, new_text):
    logger.debug(f'onUpdateText: {new_text}')
    self.app.loop.call_soon_threadsafe(lambda: self.updateText_(new_text))

  def updateStatus_(self, new_status):
    logger.debug(f'updateStatus_: {new_status}')
    self.status_bar.content = FormattedTextControl(new_status)
    self.app.invalidate()

  def onUpdateStatus(self, new_status):
    logger.debug(f'onUpdateStatus: {new_status}')
    self.app.loop.call_soon_threadsafe(lambda: self.updateStatus_(new_status))

  def run(self):
    self.app.run()
