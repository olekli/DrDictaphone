# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import events

class Events(events.Events):
  __events__ = ('result', 'fence', 'shutdown')
