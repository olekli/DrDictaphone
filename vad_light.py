# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
from pydub import AudioSegment
from speechbrain.pretrained import VAD
from pipeline_events import PipelineEvents
import logger

logger = logger.get(__name__)

class VadLight:
  def __init__(self,
    silence_threshold = 1000
  ):
    self.events = PipelineEvents()
    self.silence_threshold = silence_threshold

    self.vad = VAD.from_hparams(source = 'speechbrain/vad-crdnn-libriparty', savedir = 'tmpdir')
    self.buffer = AudioSegment.silent(duration = 2000)
    self.collected = AudioSegment.empty()

  def onStartVad(self):
    self.events.start_vad()

  def onStopVad(self):
    self.events.result(self.collected + self.buffer)
    self.buffer = AudioSegment.silent(duration = 2000)
    self.collected = AudioSegment.empty()
    self.events.idle()
    self.events.stop_vad()

  def onResult(self, audio_segment):
    self.buffer += audio_segment
    logger.debug(f'received segment, buffer len: {len(self.buffer)}')
    self.checkForSpeech()

  def checkForSpeech(self, flush = False):
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
          self.buffer = AudioSegment.silent(duration = 2000)
          self.events.idle()
        elif len(predictions) > 0:
          self.events.active()
          predictions.append([len(self.buffer)])
          gaps = []
          for i in range(1, len(predictions)):
            gaps.append(
              (predictions[i][0] - predictions[i-1][1], (predictions[0][0], predictions[i-1][1]))
            )
          cut_at = 0
          for silence_after_segment, (start, end) in reversed(gaps):
            if silence_after_segment > self.silence_threshold:
              self.collected += self.buffer[start:end]
              self.collected += AudioSegment.silent(duration = self.silence_threshold)
              cut_at = end
          if cut_at > 0:
            self.buffer = AudioSegment.silent(
              duration = 2000 - len(self.buffer[cut_at:])
            ) + self.buffer[cut_at:]
