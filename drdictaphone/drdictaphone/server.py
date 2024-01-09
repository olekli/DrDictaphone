# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
from mreventloop import connect, disconnect, has_event_loop, emits, slot, getEventLoop, EventLoop
from drdictaphone_shared.rpc import RpcServer
from drdictaphone.config import readProfile, makeOutputFilename, getProfilePath
from drdictaphone.profile_manager import ProfileManager
from drdictaphone.server_pipeline import ServerPipeline
from drdictaphone.status_manager import StatusManager
from drdictaphone.status_aggregator import StatusAggregator
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
class Server:
  def __init__(self):
    self.profile_manager = ProfileManager()
    self.profile_manager.event_loop = self.event_loop
    self.pipeline = None
    self.status_manager = StatusManager()
    self.status_manager.event_loop = self.event_loop
    self.rpc = RpcServer()
    connect(self.rpc, 'profile_selected', self.profile_manager, 'onProfileSelected')
    connect(self.rpc, 'query_profiles', self.profile_manager, 'onQueryProfiles')
    connect(self.profile_manager, 'profile_change', self, 'onProfileChange')
    connect(self.profile_manager, 'available_profiles', self.rpc.publish, 'available_profiles')
    connect(self.profile_manager, 'profile_change', self.status_manager, 'onProfileChange')
    connect(self.rpc, 'query_status', self.status_manager, 'onQueryStatus')
    connect(self.status_manager, 'updated', self.rpc.publish, 'status')
    connect(self.rpc, 'shutdown', self, 'onShutdown')
    self.status_aggregator = None

    self.exiting = asyncio.Event()

  @slot
  async def onProfileChange(self, profile):
    await self.stopPipeline()
    await self.startPipeline(profile)

  @slot
  def onShutdown(self):
    self.exiting.set()

  async def startPipeline(self, profile):
    logger.info(f'starting pipeline: {profile.id}')
    logger.debug(f'profile: {profile}')
    self.pipeline = ServerPipeline(profile)

    connect(self.rpc, 'start_rec', self.pipeline.pipeline, 'onStartRec')
    connect(self.rpc, 'stop_rec', self.pipeline.pipeline, 'onStopRec')
    connect(self.rpc, 'toggle_rec', self.pipeline.pipeline, 'onToggleRec')
    connect(self.rpc, 'discard_rec', self.pipeline.pipeline, 'onDiscardRec')
    connect(self.rpc, 'pause_mic', self.pipeline.pipeline, 'onPauseMic')
    connect(self.rpc, 'unpause_mic', self.pipeline.pipeline, 'onUnpauseMic')
    connect(self.rpc, 'clear_buffer', self.pipeline.pipeline, 'onClearBuffer')
    connect(self.rpc, 'load_file', self.pipeline.pipeline, 'onLoadFile')
    connect(self.pipeline.outlet, 'result', self.rpc.publish, 'result')
    connect(self.pipeline.outlet, 'result', lambda _: self.status_manager.onErrorUnset())
    connect(self.pipeline.outlet, 'error', self.status_manager, 'onErrorSet')
    connect(self.pipeline.cost_counter, 'costs_incurred', self.status_manager, 'onCostsIncurred')
    connect(self.pipeline.microphone, 'active', self.status_manager, 'onStartRec')
    connect(self.pipeline.microphone, 'idle', self.status_manager, 'onStopRec')
    if self.status_aggregator:
      disconnect(self.status_aggregator)
    self.status_aggregator = StatusAggregator([
      self.pipeline.vad.event_loop,
      self.pipeline.transcriber.event_loop,
      self.pipeline.post_processor.event_loop,
    ])
    self.status_aggregator.event_loop = self.event_loop
    connect(self.status_aggregator, 'active', self.status_manager, 'onStartProcessing')
    connect(self.status_aggregator, 'idle', self.status_manager, 'onStopProcessing')

    await self.pipeline.__aenter__()

  async def stopPipeline(self):
    logger.info('stopping pipeline')
    disconnect(self.rpc, 'start_rec')
    disconnect(self.rpc, 'stop_rec')
    disconnect(self.rpc, 'toggle_rec')
    disconnect(self.rpc, 'discard_rec')
    disconnect(self.rpc, 'pause_mic')
    disconnect(self.rpc, 'unpause_mic')
    disconnect(self.rpc, 'clear_buffer')
    disconnect(self.rpc, 'load_file')
    if self.pipeline:
      await self.pipeline.__aexit__(None, None, None)

  async def __aenter__(self):
    logger.info('starting server...')
    await self.event_loop.__aenter__()
    await self.rpc.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    logger.info('stopping server...')
    await self.stopPipeline()
    await self.event_loop.__aexit__(exc_type, exc_value, traceback)
    await self.rpc.__aexit__(exc_type, exc_value, traceback)
    self.exiting.set()

  def __await__(self):
    yield from self.exiting.wait().__await__()
