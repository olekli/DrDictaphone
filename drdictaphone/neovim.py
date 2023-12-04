# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from drdictaphone.event_loop import EventLoop, connect
from events import Events
import pynvim

@pynvim.plugin
class DrDictaphonePlugin(object):
  def __init__(self, nvim):
    self.events = Events(('start_rec', 'stop_rec'))
    self.__event_loop__ == EventLoop()
    self.nvim = nvim
    self.profile_name = ''
    self.main = MainWrapper()
    self.__event_loop__.enter()
    connect(self, [ 'start_rec', 'stop_rec' ], self.main, None)
    connect(self.main, [ 'result' ], self, None)
    self.main.__enter__()
    self.row = 0

  @pynvim.command('drdictaphone-set-profile', nargs = '*')
  def setProfile(self, args):
    if len(args) > 1:
      self.main.setProfile(args[0])

  @pynvim.command('drdictaphone-start', nargs = '0')
  def start_dictate(self, args):
    self.main.events.start_rec()

  @pynvim.command('drdictaphone-stop', nargs = '0')
  def stop_dictate(self, args):
    self.nvim.command('setlocal nonmodifiable')
    self.row, _ = self.nvim.current.window.cursor
    self.main.events.stop_rec()

  def onResult(self, text):
    self.nvim.async_call(lambda : self.insertText(text))

  def insertText(self, text):
    self.nvim.command('setlocal modifiable')
    buffer = self.nvim.current.buffer
    buffer.append(text, row)

  @pynvim.autocmd('VimLeave', sync = True)
  def onVimLeave(self):
    self.main.__exit__(None, None, None)
    self.__event_loop__.exit(None, None, None)
