# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class Outlet:
  @slot
  def onResult(self, result):
    logger.debug(f'result: {result}')
    self.events.result(result)
