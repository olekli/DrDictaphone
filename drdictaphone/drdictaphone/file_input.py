# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from pydub import AudioSegment
from drdictaphone.audio_tools import normaliseFormat
from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class FileInput:
  def __init__(self):
    pass

  @slot
  def onLoadFile(self, filename):
    logger.info(f'loading file: {filename}')
    try:
      audio_file = normaliseFormat(AudioSegment.from_file(filename))
    except Exception as e:
      logger.error(f'unable to load file: {filename}: {e}')
      audio_file = None
    self.events.result(audio_file)
