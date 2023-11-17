# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

class Collector:
  def __init__(self, pipeline, output):
    self.pipeline = pipeline
    self.output = output
    self.content = []

  def __call__(self, audio_segment):
    result = self.pipeline(self.content, audio_segment)
    self.content.append(result)
    self.output(result)
