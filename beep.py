# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy as np
import sounddevice as sd

class Beep:
  def __init__(self):
    self.sample_rate = 44100
    self.high_beep_audio = self.makeBeep(440)
    self.low_beep_audio = self.makeBeep(220)

  def makeBeep(self, frequency):
    duration = 0.08
    volume = 0.2
    t = np.linspace(0, duration, int(self.sample_rate * duration), False)
    note = np.sin(frequency * 2 * np.pi * t)
    note *= volume
    audio = note * (2**15 - 1)
    audio = np.clip(audio, -2**15, 2**15 - 1)
    audio = audio.astype(np.int16)
    return audio

  def beep(self, audio):
    sd.play(audio, self.sample_rate, blocksize = int(self.sample_rate / 5))
    sd.wait()

  def beepHigh(self):
    self.beep(self.high_beep_audio)

  def beepLow(self):
    self.beep(self.low_beep_audio)
