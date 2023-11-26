# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import sounddevice
import numpy
from pydub import AudioSegment
from audio_tools import normaliseFormat
import logger
from events import Events

logger = logger.get(__name__)

class Microphone:
  def __init__(self):
    self.events = Events(('result', 'fence', 'active', 'idle'))
    self.buffer = AudioSegment.empty()
    self.running = False
    self.dtype = numpy.int16
    self.sample_width = None
    self.sample_rate = None
    self.channels = None

  def makeAudioSegment(self, indata, sample_width, sample_rate, channels):
    return normaliseFormat(AudioSegment(
      data = indata.tobytes(),
      sample_width = sample_width,
      frame_rate = sample_rate,
      channels = channels
    ))

  def callback_buffer(self, indata, frames, time, status):
    self.buffer += self.makeAudioSegment(indata, self.sample_width, self.sample_rate, self.channels)

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
    self.running = True

  def startRecording(self):
    assert not self.running
    logger.debug('start recording')
    self.events.active()
    self.makeInputStream(self.callback_buffer)

  def startStream(self):
    assert not self.running
    logger.debug('start stream')
    self.events.active()
    self.makeInputStream(self.callback_stream)

  def stop(self):
    logger.debug('stop')
    self.input_stream.__exit__(None, None, None, None)
    if len(self.buffer) > 0:
      self.events.result(self.buffer)
    self.events.fence()
    self.buffer = AudioSegment.empty()
    self.events.idle()
    self.running = False
