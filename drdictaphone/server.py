# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from mreventloop import connect, disconnect, has_event_loop, emits, slot, getEventLoop, EventLoop
from mreventloop import Server as RpcServer
from drdictaphone.config import readProfile, makeOutputFilename, getProfilePath
from drdictaphone.profile_manager import ProfileManager
from drdictaphone.server_pipeline import ServerPipeline
from drdictaphone.server_status_line import ServerStatusLine
from drdictaphone.server_ui import ServerUi
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@emits('events', [ 'recording', 'processing', 'result_ready' ])
class Server:
  def __init__(self):
    self.profile_manager = ProfileManager()
    self.profile_manager.event_loop = self.event_loop
    self.pipeline = None
    self.status_line = ServerStatusLine()
    self.status_line.event_loop = self.event_loop
    self.ui = ServerUi()
    self.rpc_server = RpcServer(
      'ipc:///tmp/drdictaphone.ipc',
      [ 'start_rec', 'stop_rec', 'profile_selected', 'shutdown', 'query_profiles' ],
      [ 'status', 'result', 'available_profiles' ]
    )
    connect(self.rpc_server, 'profile_selected', self.profile_manager, 'onProfileSelected')
    connect(self.rpc_server, 'query_profiles', self.profile_manager, 'onQueryProfiles')
    connect(self.profile_manager, 'profile_change', self, 'onProfileChange')
    connect(self.profile_manager, 'available_profiles', self.rpc_server.publish, 'available_profiles')
    connect(self.profile_manager, 'profile_change', self.status_line, 'onProfileChange')
    connect(self, 'recording', self.status_line, 'onRecording')
    connect(self, 'processing', self.status_line, 'onProcessing')
    connect(self.status_line, 'status_update', self.ui, 'onStatusUpdate')
    connect(self.status_line, 'status_update', self.rpc_server.publish, 'status')
    connect(self.rpc_server, 'shutdown', self, 'onShutdown')

    self.exiting = asyncio.Event()

  @slot
  async def onProfileChange(self, profile):
    await self.stopPipeline()
    await self.startPipeline(profile)

  @slot
  def onShutdown(self):
    self.exiting.set()

  async def startPipeline(self, profile):
    logger.debug(f'starting pipeline: {profile}')
    self.pipeline = ServerPipeline(profile)

    connect(self.rpc_server, 'start_rec', self.pipeline.microphone, 'onStartRec')
    connect(self.rpc_server, 'stop_rec', self.pipeline.microphone, 'onStopRec')
    connect(self.pipeline.result_buffer, 'result', self.rpc_server.publish, 'result')
    connect(self.pipeline.microphone, 'active', self, lambda: self.events.recording(True))
    connect(self.pipeline.microphone, 'idle', self, lambda: self.events.recording(False))
    connect(
      self.pipeline.transcriber.event_loop, 'active',
      self, lambda: self.events.processing(True)
    )
    connect(
      self.pipeline.transcriber.event_loop, 'idle',
      self, lambda: self.events.processing(False)
    )
    connect(
      self.pipeline.post_processor.event_loop, 'active',
      self, lambda: self.events.processing(True)
    )
    connect(
      self.pipeline.post_processor.event_loop, 'idle',
      self, lambda: self.events.processing(False)
    )

    await self.pipeline.__aenter__()

  async def stopPipeline(self):
    logger.debug('stopping pipeline')
    disconnect(self.rpc_server, 'start_rec')
    disconnect(self.rpc_server, 'stop_rec')
    if self.pipeline:
      await self.pipeline.__aexit__(None, None, None)

  async def __aenter__(self):
    logger.debug('starting server...')
    await self.event_loop.__aenter__()
    await self.rpc_server.__aenter__()
    await self.ui.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    logger.debug('stopping server...')
    await self.stopPipeline()
    await self.ui.__aexit__(exc_type, exc_value, traceback)
    await self.event_loop.__aexit__(exc_type, exc_value, traceback)
    await self.rpc_server.__aexit__(exc_type, exc_value, traceback)
    self.exiting.set()

  def __await__(self):
    yield from self.exiting.wait().__await__()
