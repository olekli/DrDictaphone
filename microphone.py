# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import sounddevice
import numpy
from pydub import AudioSegment
from audio_tools import normaliseFormat
import logger
from pipeline_events import PipelineEvents

logger = logger.get(__name__)

class Microphone:
  def __init__(self):
    self.events = PipelineEvents()
    self.buffer = AudioSegment.empty()
    self.recording = False
    self.streaming = False
    self.paused = False
    self.time_recorded = 0
    self.dtype = numpy.int16
    self.sample_width = None
    self.sample_rate = None
    self.channels = None

  def onStartRec(self):
    assert not self.recording and not self.streaming
    logger.debug('start recording')
    self.recording = True
    self.makeInputStream(self.callback_recording)
    self.events.active()
    self.events.start_rec()

  def onStopRec(self):
    assert self.recording
    logger.debug('stop recording')
    self.input_stream.__exit__(None, None, None, None)

    if len(self.buffer) > 0:
      self.events.result(self.buffer)

    self.recording = False
    self.paused = False
    self.time_recorded = 0
    self.buffer = AudioSegment.empty()
    self.events.idle()
    self.events.stop_rec()
    self.events.time_recorded(0)
    self.events.fence()

  def onStartVad(self):
    assert not self.recording and not self.streaming
    logger.debug('start stream')
    self.streaming = True
    self.events.active()
    self.makeInputStream(self.callback_stream)
    self.events.start_vad()

  def onStopVad(self):
    assert self.streaming
    logger.debug('stop stream')
    self.input_stream.__exit__(None, None, None, None)

    if len(self.buffer) > 0:
      self.events.result(self.buffer)

    self.buffer = AudioSegment.empty()
    self.streaming = False
    self.paused = False
    self.events.idle()
    self.events.stop_vad()

  def onPauseMic(self):
    assert (self.recording or self.streaming) and not self.paused
    logger.debug('pause mic')
    self.input_stream.__exit__(None, None, None, None)
    self.paused = True
    self.events.idle()

  def onUnpauseMic(self):
    assert self.paused
    self.paused = False
    if self.recording:
      self.makeInputStream(self.callback_recording)
    elif self.streaming:
      self.makeInputStream(self.callback_stream)
    else:
      assert False
    self.events.active()

  def makeAudioSegment(self, indata, sample_width, sample_rate, channels):
    return normaliseFormat(AudioSegment(
      data = indata.tobytes(),
      sample_width = sample_width,
      frame_rate = sample_rate,
      channels = channels
    ))

  def callback_recording(self, indata, frames, time, status):
    self.buffer += self.makeAudioSegment(indata, self.sample_width, self.sample_rate, self.channels)
    time_recorded = int(len(self.buffer) / 1000)
    if self.time_recorded != time_recorded:
      self.time_recorded = time_recorded
      self.events.time_recorded(self.time_recorded)

  def callback_stream(self, indata, frames, time, status):
    self.buffer += self.makeAudioSegment(indata, self.sample_width, self.sample_rate, self.channels)
    if len(self.buffer) >= 1000:
      self.events.result(self.buffer)
      self.buffer = AudioSegment.empty()

  def makeInputStream(self, callback):
    device_info = sounddevice.query_devices(sounddevice.default.device, 'input')
    self.sample_rate = int(device_info['default_samplerate'])
    self.channels = device_info['max_input_channels']
    self.sample_width = numpy.dtype(self.dtype).itemsize

    self.input_stream = sounddevice.InputStream(
      samplerate = self.sample_rate,
      channels = self.channels,
      dtype = self.dtype,
      blocksize = int(self.sample_rate / 10),
      callback = callback
    )
    self.input_stream.__enter__()
