# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import sounddevice
import threading
import queue
import numpy
import tempfile
from pydub import AudioSegment
from speechbrain.pretrained import VAD
from audio_tools import normaliseFormat

class Recorder:
  def __init__(self, dispatcher):
    self.dispatcher = dispatcher
    self.segments_queue = queue.Queue()
    self.captured_audio = AudioSegment.empty()
    self.segment_length = 1
    self.min_length = 2

    self.is_running = False
    self.is_capturing = False
    self.recording_thread = threading.Thread(target = self.run)

    self.dtype = numpy.int16

    device_info = sounddevice.query_devices(sounddevice.default.device, 'input')
    self.sample_rate = int(device_info['default_samplerate'])
    self.channels = device_info['max_input_channels']
    self.sample_width = numpy.dtype(self.dtype).itemsize

    self.vad = VAD.from_hparams(source = 'speechbrain/vad-crdnn-libriparty', savedir = 'tmpdir')

  def checkForSpeech(self, audio_segment):
    with tempfile.NamedTemporaryFile(
      prefix = 'recorded_audio_',
      suffix = '.wav',
      delete = True
    ) as temp_file:
      padded_audio_segment = audio_segment + AudioSegment.silent(duration = 2000)
      padded_audio_segment.export(temp_file.name, format = 'wav')
      predictions = self.vad.get_speech_segments(
        temp_file.name,
        large_chunk_size = 2,
        small_chunk_size = 1
      )
      return len(predictions) > 0

  def checkCapturing(self, audio_segment):
    is_speech = self.checkForSpeech(audio_segment)
    if not self.is_capturing and is_speech:
      print('start capturing...')
      return True
    if self.is_capturing and not is_speech:
      print('stop capturing...')
      return False
    return self.is_capturing

  def processAudio(self):
    while self.is_running:
      data = self.segments_queue.get()
      audio_segment = AudioSegment(
        data = data.tobytes(),
        sample_width = self.sample_width,
        frame_rate = self.sample_rate,
        channels = self.channels
      )
      audio_segment = normaliseFormat(audio_segment)

      is_capturing_ = self.is_capturing
      self.is_capturing = self.checkCapturing(audio_segment)
      was_capturing = not self.is_capturing and is_capturing_
      if self.is_capturing or was_capturing:
        self.captured_audio = self.captured_audio + audio_segment
      if was_capturing:
        self.dispatchAudio()

  def dispatchAudio(self):
    if len(self.captured_audio) > (self.min_length * 1000):
      self.dispatcher(self.captured_audio)
    self.captured_audio = AudioSegment.empty()

  def callback(self, indata, frames, time, status):
    self.segments_queue.put(indata.copy())

  def run(self):
    self.is_running = True
    with sounddevice.InputStream(
      samplerate = self.sample_rate,
      channels = self.channels,
      dtype = self.dtype,
      callback = self.callback,
      blocksize = self.sample_rate * self.segment_length
    ):
      self.processAudio()

  def __enter__(self):
    print('starting recorder')
    self.recording_thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.is_running = False
    self.recording_thread.join()
    print('exiting recorder')
    return True
