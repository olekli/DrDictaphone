# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

def normaliseFormat(audio_segment):
  result = audio_segment.set_channels(1)
  result = result.set_frame_rate(16000)
  result = result.set_sample_width(2)
  return result
