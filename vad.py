# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
from pydub import AudioSegment
from speechbrain.pretrained import VAD
from events import Events
import logger

logger = logger.get(__name__)

class Vad:
  def __init__(self):
    self.events = Events(('result'))
    self.vad = VAD.from_hparams(source = 'speechbrain/vad-crdnn-libriparty', savedir = 'tmpdir')
    self.captured_audio = AudioSegment.empty()
    self.min_length = 1
    self.is_capturing = False

  def padAudio(self, audio_segment):
    padding = 3000 - len(audio_segment)
    if padding > 0:
      return audio_segment + AudioSegment.silent(duration = padding)
    else:
      return audio_segment

  def checkCapturing(self, audio_segment):
    is_speech = self.checkForSpeech(self.padAudio(audio_segment))
    if not self.is_capturing and is_speech:
      logger.debug('start capturing...')
      return True
    if self.is_capturing and not is_speech:
      logger.debug('stop capturing')
      return False
    return self.is_capturing

  def checkForSpeech(self, audio_segment):
    with tempfile.NamedTemporaryFile(
      prefix = 'recorded_audio_',
      suffix = '.wav',
      delete = True
    ) as temp_file:
      audio_segment.export(temp_file.name, format = 'wav')
      predictions = self.vad.get_speech_segments(
        temp_file.name,
        large_chunk_size = 2,
        small_chunk_size = 1
      )
      return len(predictions) > 0

  def dispatchAudio(self):
    if len(self.captured_audio) > (self.min_length * 1000):
      self.events.result(self.captured_audio)
    self.captured_audio = AudioSegment.empty()

  def __call__(self, context, audio_segment):
    is_capturing_ = self.is_capturing
    self.is_capturing = self.checkCapturing(audio_segment)
    was_capturing = not self.is_capturing and is_capturing_
    if self.is_capturing or was_capturing:
      self.captured_audio = self.captured_audio + audio_segment
    if was_capturing:
      self.dispatchAudio()
