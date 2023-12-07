# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import tempfile
from pydub import AudioSegment
from speechbrain.pretrained import VAD
from mreventloop import emits, slot, supports_event_loop
from drdictaphone.pipeline_events import PipelineEvents
from drdictaphone import logger

logger = logger.get(__name__)

@supports_event_loop('event_loop')
@emits('events', PipelineEvents)
class StaticVad:
  def __init__(self, silence_threshold = 1000):
    self.events = PipelineEvents()
    self.silence_threshold = silence_threshold

    self.vad = VAD.from_hparams(source = 'speechbrain/vad-crdnn-libriparty', savedir = 'tmpdir')

  @slot
  def onResult(self, audio_segment):
    if len(audio_segment) < 3000:
      self.events.result(audio_segment)
    else:
      with tempfile.NamedTemporaryFile(
        prefix = 'recorded_audio_',
        suffix = '.wav',
        delete = True
      ) as temp_file:
        logger.debug(f'received audio of length: {len(audio_segment)}')
        audio_segment.export(temp_file.name, format = 'wav')
        predictions = self.vad.get_speech_segments(
          temp_file.name,
          large_chunk_size = int(len(audio_segment) / 1000) - 1,
          small_chunk_size = 1,
          apply_energy_VAD = True,
        )
        predictions = [ [int(x * 1000), int(y * 1000)] for [x, y] in predictions.tolist() ]
        logger.debug(f'predictions: {predictions}')
        result = AudioSegment.empty()
        prev_end = 0
        for start, end in predictions:
          if (start - prev_end) < self.silence_threshold:
            result += audio_segment[prev_end:end]
          else:
            result += audio_segment[(start - self.silence_threshold):end]
          prev_end = end
        if len(result) > 0:
          self.events.result(result)

  @slot
  def onFence(self):
    self.events.fence()
