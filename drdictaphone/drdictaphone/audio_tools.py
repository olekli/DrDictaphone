# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

def normaliseFormat(audio_segment):
  result = audio_segment.set_channels(1)
  result = result.set_frame_rate(16000)
  result = result.set_sample_width(2)
  return result
