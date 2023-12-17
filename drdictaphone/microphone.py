# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pydub import AudioSegment
from mreventloop import emits, slot, has_event_loop
from drdictaphone.audio_tools import normaliseFormat
from drdictaphone.pipeline_events import PipelineEvents
from drdictaphone.pa import pa
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@emits('events', PipelineEvents)
class Microphone:
  def __init__(self):
    self.buffer = AudioSegment.empty()
    self.recording = False
    self.paused = False

    default_device_index = pa.get_default_input_device_info()['index']
    device_info = pa.get_device_info_by_index(default_device_index)

    logger.debug(f'{device_info}')
    logger.info(f'recording on device: {device_info["name"]}')
    logger.debug(f'{device_info}')

    self.sample_rate = int(device_info['defaultSampleRate'])
    self.channels = 1
    self.audio_format = pyaudio.paInt16
    self.sample_width = pa.get_sample_size(self.audio_format)
    logger.debug(f'sw: {self.sample_width}')
    logger.debug(f'sr: {self.sample_rate}')
    self.chunk = 1024

    self.stream = None

  def startStream(self):
    self.stream = pa.open(
      format = self.audio_format,
      channels = self.channels,
      rate = self.sample_rate,
      input = True,
      frames_per_buffer = self.chunk,
      stream_callback = self.callback
    )

  def stopStream(self):
    self.stream.stop_stream()
    self.stream.close()

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
    assert self.recording
    logger.debug('stop recording')
    self.stopStream()
    self.events.result(normaliseFormat(self.buffer))
    self.recording = False
    self.paused = False
    self.events.idle()
    self.events.stop_rec()
    self.events.fence()

  @slot
  def onPauseMic(self):
    assert self.recording and not self.paused
    logger.debug('pause mic')
    self.input_stream.stop()
    self.paused = True
    self.events.idle()

  @slot
  def onUnpauseMic(self):
    assert self.paused
    self.paused = False
    self.input_stream.start()
    self.events.active()

  def makeAudioSegment(self, indata):
    return AudioSegment(
      data = indata,
      sample_width = self.sample_width,
      frame_rate = self.sample_rate,
      channels = self.channels
    )

  def callback(self, indata, frames, time, status):
    self.buffer += self.makeAudioSegment(indata)
    return (None, pyaudio.paContinue)
