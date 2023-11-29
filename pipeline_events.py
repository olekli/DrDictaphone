# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import events

class PipelineEvents(events.Events):
  __events__ = (
    'result',
    'fence',
    'active',
    'idle',
    'start_vad',
    'start_rec',
    'stop_vad',
    'stop_rec',
    'costs',
    'pause_mic',
    'unpause_mic',
    'time_recorded',
    'clear_buffer',
  )
