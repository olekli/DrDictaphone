# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import logging.config
import logging
import os
from drdictaphone_shared.config_path import getConfigPath

logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
          'format': '%(asctime)s %(levelname)s: %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': os.path.join(getConfigPath(), 'neovim.log'),
            'level': logging.INFO,
        },
    },
    'loggers': {
        'neovim-plugin': {
            'handlers': ['file_handler'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

logging.config.dictConfig(logger_config)
logger = logging.getLogger('neovim-plugin')

import pynvim
import asyncio
from mreventloop import has_event_loop, slot, connect
from drdictaphone_shared.rpc import RpcClient
from drdictaphone_shared.status_line import makeStatusLinePlugin

@pynvim.plugin
@has_event_loop('event_loop')
class DrDictaphonePlugin(object):
  def __init__(self, nvim):
    logger.debug('init plugin')
    self.nvim = nvim
    self.row = 0
    self.rpc = RpcClient()
    connect(self.rpc, 'result', self, 'onResult')
    connect(self.rpc, 'status', self, 'onStatus')
    connect(self.event_loop, 'started', lambda: self.rpc.publish.query_status())
    asyncio.create_task(self.rpc.__aenter__())
    asyncio.create_task(self.event_loop.__aenter__())

  @pynvim.command('DrDictaphoneInit', nargs = '*')
  def dummy(self, args):
    pass

  @pynvim.command('DrDictaphoneSetProfile', nargs = '*')
  def setProfile(self, args):
    self.nvim.loop.create_task(self.setProfile_(args))

  async def setProfile_(self, args):
    logger.debug(f'selecting profile: {args[0]}')
    if len(args) > 0:
      await self.rpc.publish.profile_selected(args[0])

  @pynvim.command('DrDictaphoneStart', nargs = '0')
  def startDictate(self, args):
    self.nvim.loop.create_task(self.startDictate_())

  async def startDictate_(self):
    logger.debug(f'start recording')
    await self.rpc.publish.start_rec()

  @pynvim.command('DrDictaphoneStop', nargs = '0')
  def stopDictate(self, args):
    self.nvim.loop.create_task(self.stopDictate_())

  async def stopDictate_(self):
    logger.debug(f'stop recording')
    await self.rpc.publish.stop_rec()

  @pynvim.command('DrDictaphoneToggle', nargs = '0')
  def toggleDictate(self, args):
    self.nvim.loop.create_task(self.toggleDictate_())

  async def toggleDictate_(self):
    logger.debug(f'toggle recording')
    await self.rpc.publish.toggle_rec()

  @slot
  def onResult(self, result):
    logger.debug(f'received result: {result}')
    self.nvim.async_call(lambda: self.insertText(result))

  @slot
  def onStatus(self, status):
    logger.debug(f'received status: {status}')
    self.nvim.async_call(lambda: self.updateStatus(makeStatusLinePlugin(status)))

  def insertText(self, lines):
    if lines:
      buffer = self.nvim.current.buffer
      window = self.nvim.current.window
      row, _ = window.cursor
      if len(buffer[row - 1]) == 0:
        buffer[row - 1] = lines[0]
        lines = lines[1:]
        last_row = row - 1
        row += 1
      if lines:
        buffer.append(lines, row if row < len(buffer) else -1)
        last_row = row - 1 + len(lines)
        last_row = last_row if last_row < len(buffer) else len(buffer) - 1
      line_length = len(buffer[last_row])
      window.cursor = [last_row + 1, line_length - 1]

  def updateStatus(self, status):
    self.nvim.vars['airline_section_b'] = status
    self.nvim.command('AirlineRefresh')

#  @pynvim.autocmd('VimLeave', sync = True)
#  def onVimLeave(self):
#    self.rpc_client.__exit__(None, None, None)
