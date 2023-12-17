# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import sounddevice
import numpy
from pydub import AudioSegment
from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.audio_tools import normaliseFormat
from drdictaphone.pipeline_events import PipelineEvents, PipelineSlots
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@forwards(PipelineSlots)
@emits('events', PipelineEvents)
class Microphone:
  def __init__(self):
    self.buffer = AudioSegment.empty()
    self.recording = False
    self.paused = False
    self.time_recorded = 0
    self.dtype = numpy.int16
    self.sample_width = None
    self.sample_rate = None
    self.channels = None

  def startStream(self):
    device_info = sounddevice.query_devices(sounddevice.default.device, 'input')
    logger.info(f'recording on device: {device_info["name"]}')
    self.sample_rate = int(device_info['default_samplerate'])
    self.channels = 1
    self.sample_width = numpy.dtype(self.dtype).itemsize

    self.input_stream = sounddevice.InputStream(
      samplerate = self.sample_rate,
      channels = self.channels,
      dtype = self.dtype,
      blocksize = int(self.sample_rate / 10),
      callback = self.callback
    )
    self.input_stream.start()

  def stopStream(self):
    self.input_stream.stop()
    self.input_stream.close()

  def stopRec(self, pass_recording):
    assert self.recording
    logger.debug('stop recording')
    self.stopStream()

    if not pass_recording:
      logger.debug('discarding')
      self.buffer = AudioSegment.empty()

    self.recording = False
    self.paused = False
    self.time_recorded = 0
    self.events.idle()
    self.events.stop_rec()
    self.events.time_recorded(0)
    if len(self.buffer) > 0:
      self.events.result(self.buffer)
      self.events.fence()

  @slot
  def onStartRec(self):
    assert not self.recording
    logger.debug('start recording')
    self.buffer = AudioSegment.empty()
    self.recording = True
    self.startStream()
    self.events.active()
    self.events.start_rec()

  @slot
  def onStopRec(self):
    self.stopRec(True)

  @slot
  def onDiscardRec(self):
    self.stopRec(False)

  @slot
  def onPauseMic(self):
    assert self.recording and not self.paused
    logger.debug('pause mic')
    self.stopStream()
    self.paused = True
    self.events.idle()

  @slot
  def onUnpauseMic(self):
    assert self.paused
    self.paused = False
    self.startStream()
    self.events.active()

  def makeAudioSegment(self, indata):
    return normaliseFormat(AudioSegment(
      data = indata.tobytes(),
      sample_width = self.sample_width,
      frame_rate = self.sample_rate,
      channels = self.channels
    ))

  def callback(self, indata, frames, time, status):
    self.buffer += self.makeAudioSegment(indata)
