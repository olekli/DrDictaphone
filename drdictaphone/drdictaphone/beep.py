# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
from mreventloop import emits, slot, has_event_loop, forwards
import numpy as np
import sounddevice as sd

@has_event_loop('event_loop')
class Beep:
  def __init__(self):
    self.sample_rate = 44100
    self.high_beep_audio_short = self.makeBeep(440, 0.05)
    self.low_beep_audio_short = self.makeBeep(220, 0.05)
    self.high_beep_audio_long = self.makeBeep(440, 0.1)
    self.low_beep_audio_long = self.makeBeep(220, 0.12)

  def makeBeep(self, frequency, duration):
    duration = duration
    volume = 0.2
    t = np.linspace(0, duration, int(self.sample_rate * duration), False)
    note = np.sin(frequency * 2 * np.pi * t)
    note *= volume
    audio = note * (2**15 - 1)
    audio = np.clip(audio, -2**15, 2**15 - 1)
    audio = audio.astype(np.int16)
    return audio

  def beep_(self, audio):
    sd.play(audio, self.sample_rate, blocksize = int(self.sample_rate / 5), blocking = False)
    sd.wait()

  async def beep(self, audio):
    await asyncio.to_thread(self.beep_, audio)

  @slot
  async def beepHighShort(self):
    await self.beep(self.high_beep_audio_short)

  @slot
  async def beepLowShort(self):
    await self.beep(self.low_beep_audio_short)

  @slot
  async def beepLowShortTwice(self):
    await self.beep(self.low_beep_audio_short)
    await self.beep(self.low_beep_audio_short)

  @slot
  async def beepHighLong(self):
    await self.beep(self.high_beep_audio_long)

  @slot
  async def beepLowLong(self):
    await self.beep(self.low_beep_audio_long)
