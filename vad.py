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
    self.events = Events(('final_result', 'temporary_result'))
    self.vad = VAD.from_hparams(source = 'speechbrain/vad-crdnn-libriparty', savedir = 'tmpdir')
    self.buffer = AudioSegment.empty()
    self.max_silence = 1000
    self.min_length = 500

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
          self.buffer = AudioSegment.empty()
        elif len(predictions) > 0:
          predictions.append([len(self.buffer)])
          gaps = []
          for i in range(1, len(predictions)):
            gaps.append(
              (predictions[i][0] - predictions[i-1][1], (predictions[0][0], predictions[i-1][1]))
            )
          cut_at = 0
          for length, (start, end) in gaps:
            if length > self.max_silence:
              if (end - start) > self.min_length:
                self.events.final_result(self.buffer[start:end])
              else:
                logger.warning(f'dropping segment because it is too short: {end - start}')
              cut_at = end
          self.buffer = self.buffer[cut_at:]

  def onFinalResult(self, audio_segment):
    self.buffer += audio_segment
    logger.debug(f'received segment, buffer len: {len(self.buffer)}')
    self.checkForSpeech()

  def onTemporaryResult(self, audio_segment):
    assert False
