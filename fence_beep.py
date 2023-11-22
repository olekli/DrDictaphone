# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import sounddevice as sd
from events import Events

class FenceBeep:
  def __init__(self):
    self.events = Events(('result', 'fence'))

    duration = 0.2
    frequency = 440
    sample_rate = 44100
    volume = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    note = np.sin(frequency * 2 * np.pi * t)
    note *= volume
    audio = note * (2**15 - 1)
    audio = np.clip(audio, -2**15, 2**15 - 1)
    audio = audio.astype(np.int16)

    self.sample_rate = sample_rate
    self.audio = audio
    self.beep = True

  def onResult(self, result):
    self.beep = True
    self.events.result(result)

  def onFence(self):
    if self.beep:
      sd.play(self.audio, self.sample_rate)
      self.events.fence()
      sd.wait()
      self.beep = False
