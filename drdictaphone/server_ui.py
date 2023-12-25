# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from mreventloop import slot, emits, has_event_loop
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
class ServerUi:
  def __init__(self):
    self.status_bar_left = Window(
      content = FormattedTextControl('loading...'),
      height=1,
      align=WindowAlign.LEFT,
    )
    self.status_bar_right = Window(
      height=1,
      align=WindowAlign.RIGHT,
    )
    self.layout = Layout(
      HSplit([
        VSplit([
          self.status_bar_left,
          self.status_bar_right
        ])
      ])
    )
    self.app = Application(
      layout = self.layout,
      full_screen = False,
      mouse_support = False
    )
    task = None

  @slot
  def onStatusUpdate(self, new_status):
    self.status_bar_left.content = FormattedTextControl(new_status['left'])
    self.status_bar_right.content = FormattedTextControl(new_status['right'])
    self.app.invalidate()

  async def __aenter__(self):
    await self.event_loop.__aenter__()
    self.task = asyncio.create_task(self.app.run_async())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    self.app.exit()
    await self.task
    return await self.event_loop.__aexit__(exc_type, exc_value, traceback)
