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
  def __init__(self, segment_length, rms_threshold = 0):
    self.events = Events(('result', 'fence'))

    self.segment_length = segment_length
    self.rms_threshold = rms_threshold

  def callback(self, indata, sample_width, sample_rate, channels):
    audio_segment = AudioSegment(
      data = indata.tobytes(),
      sample_width = sample_width,
      frame_rate = sample_rate,
      channels = channels
    )
    audio_segment = normaliseFormat(audio_segment)
    if audio_segment.rms > self.rms_threshold:
      self.events.result(audio_segment)

  def __enter__(self):
    logger.debug('entering')
    dtype = numpy.int16
    device_info = sounddevice.query_devices(sounddevice.default.device, 'input')
    sample_rate = int(device_info['default_samplerate'])
    channels = device_info['max_input_channels']
    sample_width = numpy.dtype(dtype).itemsize

    self.input_stream = sounddevice.InputStream(
      samplerate = sample_rate,
      channels = channels,
      dtype = dtype,
      blocksize = sample_rate * self.segment_length,
      callback = lambda indata, frames, time, status:
        self.callback(indata, sample_width, sample_rate, channels)
    )
    self.input_stream.__enter__()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    logger.debug('exiting')
    return self.input_stream.__exit__(exc_type, exc_val, exc_tb)

  def onResult(self, result):
    pass

  def onFence(self):
    pass
