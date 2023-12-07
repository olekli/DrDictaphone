# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pynvim
from mreventloop import emits, connect
from drdictaphone.main_wrapper import MainWrapper

@pynvim.plugin
@emits('events', [ 'start_rec', 'stop_rec' ])
class DrDictaphonePlugin(object):
  def __init__(self, nvim):
    self.nvim = nvim
    self.profile_name = ''
    self.main = MainWrapper()
    connect(self, [ 'start_rec', 'stop_rec' ], self.main, None)
    connect(self.main, [ 'result' ], self, None)
    self.main.__enter__()
    self.row = 0

  @pynvim.command('DrdictaphoneSetProfile', nargs = '*')
  def setProfile(self, args):
    if len(args) > 1:
      self.main.setProfile(args[0])

  @pynvim.command('DrdictaphoneStart', nargs = '0')
  def start_dictate(self, args):
    self.main.events.start_rec()

  @pynvim.command('DrdictaphoneStop', nargs = '0')
  def stop_dictate(self, args):
    self.nvim.command('setlocal readonly')
    self.row, _ = self.nvim.current.window.cursor
    self.main.events.stop_rec()

  def onResult(self, text):
    self.nvim.async_call(lambda : self.insertText(text))

  def insertText(self, text):
    self.nvim.command('setlocal noreadonly')
    buffer = self.nvim.current.buffer
    buffer.append(text, row)

  @pynvim.autocmd('VimLeave', sync = True)
  def onVimLeave(self):
    self.main.__exit__(None, None, None)
