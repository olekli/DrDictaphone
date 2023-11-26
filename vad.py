# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
from pydub import AudioSegment
from speechbrain.pretrained import VAD
from events import Events
import logger

logger = logger.get(__name__)

class Vad:
  def __init__(self,
    silence_threshold_content = 800,
    silence_threshold_fence = 2000,
    min_length = 500
  ):
    self.events = Events(('result', 'fence', 'active', 'idle'))
    self.vad = VAD.from_hparams(source = 'speechbrain/vad-crdnn-libriparty', savedir = 'tmpdir')
    self.buffer = AudioSegment.silent(duration = 2000)
    self.silence_threshold_content = silence_threshold_content
    self.silence_threshold_fence = silence_threshold_fence
    self.min_length = min_length

    self.fenced_on_no_speech = False

    self.pass_thru = True

  def checkForSpeech(self):
    if len(self.buffer) >= 3000:
      with tempfile.NamedTemporaryFile(
        prefix = 'recorded_audio_',
        suffix = '.wav',
        delete = True
      ) as temp_file:
        self.buffer.export(temp_file.name, format = 'wav')
        predictions = self.vad.get_speech_segments(
          temp_file.name,
          large_chunk_size = int(len(self.buffer) / 1000) - 1,
          small_chunk_size = 1,
          apply_energy_VAD = True,
        )
        predictions = [ [int(x * 1000), int(y * 1000)] for [x, y] in predictions.tolist() ]
        if len(predictions) == 0:
          if not self.fenced_on_no_speech:
            self.events.fence()
            self.fenced_on_no_speech = True
          self.buffer = AudioSegment.silent(duration = 2000)
        elif len(predictions) > 0:
          self.fenced_on_no_speech = False
          predictions.append([len(self.buffer)])
          gaps = []
          for i in range(1, len(predictions)):
            gaps.append(
              (predictions[i][0] - predictions[i-1][1], (predictions[0][0], predictions[i-1][1]))
            )
          cut_at = 0
          for silence_after_segment, (start, end) in reversed(gaps):
            if silence_after_segment > self.silence_threshold_content:
              if (end - start) > self.min_length:
                self.events.result(self.buffer[start:end])
              else:
                logger.warning(f'dropping segment because it is too short: {end - start}')
              cut_at = end
            if silence_after_segment > self.silence_threshold_fence:
              self.events.fence()
            if cut_at > 0:
              self.buffer = AudioSegment.silent(
                duration = 3000 - len(self.buffer[cut_at:])
              ) + self.buffer[cut_at:]
              break

  def onResult(self, audio_segment):
    if self.pass_thru:
      self.events.result(audio_segment)
    else:
      self.buffer += audio_segment
      logger.debug(f'received segment, buffer len: {len(self.buffer)}')
      self.checkForSpeech()

  def onFence(self):
    if not self.pass_thru:
      self.buffer += AudioSegment.silent(duration = int(self.silence_threshold_fence * 1.5))
      self.fenced_on_no_speech = False
      self.checkForSpeech()
      self.pass_thru = True
      self.events.idle()
    else:
      self.events.fence()

  def enable(self):
    self.pass_thru = False
    self.events.active()
