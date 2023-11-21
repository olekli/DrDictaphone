# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import threading
import tempfile
from pydub import AudioSegment
from speechbrain.pretrained import VAD
from audio_tools import normaliseFormat

class Recorder:
  def __init__(self, input_queue, dispatcher):
    self.input_queue = input_queue
    self.dispatcher = dispatcher
    self.recording_thread = threading.Thread(target = self.processAudio)

  def processAudio(self):
    while True:
      audio_segment = self.input_queue.get()
      self.dispatcher(audio_segment)
      if audio_segment == None:
        return

  def __enter__(self):
    print('starting recorder')
    self.recording_thread.start()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.input_queue.put(None)
    self.recording_thread.join()
    print('exiting recorder')
    return True
