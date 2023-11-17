# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

class Pipeline:
  def __init__(self, trancriber, post_processor):
    self.transcriber = trancriber
    self.post_processor = post_processor

  def __call__(self, textual_context, audio_segment):
    transcription = self.transcriber(textual_context, audio_segment)
    processed = self.post_processor(textual_context, transcription)
    return processed
