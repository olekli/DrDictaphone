# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots
from drdictaphone.beep import Beep

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class AudioFeedback:
  def __init__(self):
    self.is_recording = False
    self.beep = Beep()
    self.beep.event_loop = self.event_loop

  @slot
  def onStartRec(self):
    self.events.start_rec()
    if not self.is_recording:
      self.is_recording = True
      self.beep.beepHighLong()

  @slot
  def onStopRec(self):
    self.events.stop_rec()
    if self.is_recording:
      self.is_recording = False
      self.beep.beepLowLong()

  @slot
  def onToggleRec(self):
    self.events.toggle_rec()
    if self.is_recording:
      self.is_recording = False
      self.beep.beepLowLong()
    else:
      self.is_recording = True
      self.beep.beepHighLong()

  @slot
  def onDiscardRec(self):
    self.events.discard_rec()
    if self.is_recording:
      self.is_recording = False
      self.beep.beepLowShortTwice()
