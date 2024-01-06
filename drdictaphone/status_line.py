# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

def makeStatusLine(status):
  to_print = [
    'MIC' if status['mic'] else '',
    'PROC' if status['processing'] else '',
    'ERR' if status['error'] else '',
  ]
  left = '  ' + ''.join(f'{word:<6}' for word in to_print)
  right = f'{status["profile_name"]}      costs: {(status["costs"] / 100):.2f}$  '
  return { 'left': left, 'right': right  }

def makeStatusLinePlugin(status):
  to_print = [
    'MIC' if status['mic'] else '',
    'PROC' if status['processing'] else '',
    'ERR' if status['error'] else '',
  ]
  line = f' {status["profile_name"]} ' + ''.join(f'{word:<6}' for word in to_print)
  return line
