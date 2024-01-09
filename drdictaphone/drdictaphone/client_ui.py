# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
from prompt_toolkit import Application
from prompt_toolkit.application import in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from mreventloop import slot, emits, has_event_loop
from drdictaphone_shared.status_line import makeStatusLine

@has_event_loop('event_loop')
@emits('events', [
  'start_rec',
  'stop_rec',
  'pause_mic',
  'unpause_mic',
  'clear_buffer',
  'discard_rec',
  'query_profiles',
  'profile_selected',
  'shutdown',
  'query_status',
])
class ClientUi:
  def __init__(self):
    self.bindings = self.makeKeyBinds()
    self.text_area = TextArea(focusable = False, read_only = True)
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
        self.text_area,
        VSplit([
          self.status_bar_left,
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

    main = None

  def makeKeyBinds(self):
    bindings = KeyBindings()

    bindings.add(' ')(lambda event: self.togglePauseMic())
    bindings.add('p')(lambda event: self.toggleRecording())
    bindings.add('q')(lambda event: self.exit())
    bindings.add('c')(lambda event: self.clearBuffer())
    bindings.add('d')(lambda event: self.discardRec())
    bindings.add('s')(lambda event: self.selectProfile())

    return bindings

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
    self.events.shutdown()
    self.app.exit()

  def discardRec(self):
    if self.is_recording:
      self.events.discard_rec()
      self.is_recording = False
      self.is_paused = False

  def clearBuffer(self):
    self.text_area.text = ''
    self.app.invalidate()
    self.events.clear_buffer()

  def selectProfile(self):
    self.events.query_profiles()

  async def promptForProfile(self, available_profiles):
    async with in_terminal():
      completer = WordCompleter(available_profiles)
      print('Available profiles:\n')
      for profile in available_profiles:
        print(f'{profile}')
      print('')
      user_input = prompt(
        f'Select profile ({available_profiles[0]}): ',
        completer = completer,
        in_thread = True
      )
      if user_input == '':
        user_input = available_profiles[0]
      print(f'selected {user_input}')
      return user_input

  @slot
  async def onAvailableProfiles(self, available_profiles):
    user_input = await self.promptForProfile(available_profiles)
    self.events.profile_selected(user_input)

  @slot
  def onResult(self, new_text):
    if self.text_area.text:
      self.text_area.text += '\n\n'
    text = '\n\n'.join(new_text)
    self.text_area.text += f'{text}'
    self.app.invalidate()

  @slot
  def onStatus(self, status):
    status_line = makeStatusLine(status)
    self.status_bar_left.content = FormattedTextControl(status_line['left'])
    self.status_bar_right.content = FormattedTextControl(status_line['right'])
    self.app.invalidate()

  async def __aenter__(self):
    await self.event_loop.__aenter__()
    self.main = asyncio.create_task(self.app.run_async())
    self.events.query_status()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    if self.app.is_running:
      self.app.exit()
    await self.main
    return await self.event_loop.__aexit__(exc_type, exc_value, traceback)

  def __await__(self):
    yield from self.main.__await__()
