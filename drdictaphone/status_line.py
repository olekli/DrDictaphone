# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from drdictaphone import logger

logger = logger.get(__name__)

def makeStatusLine(status):
  to_print = [
    'MIC' if status['mic'] else '',
    'PROC' if status['processing'] else '',
    'ERR' if status['error'] else '',
  ]
  left = '  ' + ''.join(f'{word:<6}' for word in to_print)
  right = f'{status["profile_name"]}      costs: {(status["costs"] / 100):.2f}$  '
  return { 'left': left, 'right': right  }
