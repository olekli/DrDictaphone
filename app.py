# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import threading
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea

class App:
  def __init__(self):
    self.bindings = self.makeKeyBinds()
    self.text_area = TextArea(focusable = True)
    self.layout = Layout(HSplit([self.text_area]))
    self.app = Application(layout = self.layout, key_bindings = self.bindings, full_screen = True)

  def makeKeyBinds(self):
    bindings = KeyBindings()
    bindings.add('q')(lambda event: self.exit(event))

  def exit(event):
    event.app.exit()

  def updateText_(self, new_text):
    self.text_area.text = new_text

  def updateText(self, new_text):
    app.loop.call_from_executor(lambda: self.updateText_(new_text))

  def run(self):
    self.app.run()
