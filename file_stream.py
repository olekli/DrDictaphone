# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from pydub import AudioSegment
from audio_tools import normaliseFormat

class FileStream:
  def __init__(self, filename, segment_length_ms, callback):
    self.filename = filename
    self.segment_length_ms = segment_length_ms
    self.callback = callback

  def __enter__(self):
    audio_file = normaliseFormat(AudioSegment.from_file(self.filename))
    audio_file = audio_file + AudioSegment.silent(duration = 3000)
    i = 0
    while (i + self.segment_length_ms) < len(audio_file):
      segment = audio_file[i:(i + self.segment_length_ms)]
      assert len(segment) == self.segment_length_ms, f'{len(segment)} == {self.segment_length_ms}'
      self.callback(segment)
      i += self.segment_length_ms
    last_segment = audio_file[i:]
    padding_length = self.segment_length_ms - (len(audio_file) - i)
    last_segment = last_segment + AudioSegment.silent(duration = padding_length)
    assert len(last_segment) == self.segment_length_ms, f'{len(last_segment)} == {self.segment_length_ms}'
    self.callback(last_segment)
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    pass
