# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import logging.config
import logging
import os

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
            'filename': os.path.expanduser('~/DrDictaphone/neovim.log'),
            'level': logging.DEBUG,
        },
    },
    'loggers': {
        'neovim-plugin': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

logging.config.dictConfig(logger_config)
logger = logging.getLogger('neovim-plugin')

import pynvim
import asyncio
from mreventloop import has_event_loop, slot, connect
from drdictaphone.rpc import RpcClient
from drdictaphone.status_line import makeStatusLinePlugin

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
    connect(self.event_loop, 'started', self, lambda: self.rpc.request.query_status())
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
      await self.rpc.request.profile_selected(args[0])

  @pynvim.command('DrDictaphoneStart', nargs = '0')
  def startDictate(self, args):
    self.nvim.loop.create_task(self.startDictate_())

  async def startDictate_(self):
    logger.debug(f'start recording')
    await self.rpc.request.start_rec()

  @pynvim.command('DrDictaphoneStop', nargs = '0')
  def stopDictate(self, args):
    self.nvim.loop.create_task(self.stopDictate_())

  async def stopDictate_(self):
    logger.debug(f'stop recording')
    await self.rpc.request.stop_rec()

  @pynvim.command('DrDictaphoneToggle', nargs = '0')
  def toggleDictate(self, args):
    self.nvim.loop.create_task(self.toggleDictate_())

  async def toggleDictate_(self):
    logger.debug(f'toggle recording')
    await self.rpc.request.toggle_rec()

  @slot
  def onResult(self, result):
    logger.debug(f'received result: {result}')
    self.nvim.async_call(lambda: self.insertText(result))

  @slot
  def onStatus(self, status):
    logger.debug(f'received status: {status}')
    self.nvim.async_call(lambda: self.updateStatus(makeStatusLinePlugin(status)))

  def insertText(self, lines):
    row, _ = self.nvim.current.window.cursor
    for line in lines:
      self.nvim.current.buffer.append(line, row)

  def updateStatus(self, status):
    self.nvim.vars['airline_section_b'] = status
    self.nvim.command('AirlineRefresh')

#  @pynvim.autocmd('VimLeave', sync = True)
#  def onVimLeave(self):
#    self.rpc_client.__exit__(None, None, None)
