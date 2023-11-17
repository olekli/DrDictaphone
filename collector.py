# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

class Collector:
  def __init__(self, pipeline):
    self.pipeline = pipeline
    self.content = []

  def __call__(self, audio_segment):
    self.content.append(self.pipeline(self.content, audio_segment))
