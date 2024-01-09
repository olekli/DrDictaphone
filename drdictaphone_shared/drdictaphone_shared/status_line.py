# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

def makeStatusLine(status):
  to_print = [
    'MIC' if status['mic'] else '',
    'TRANS' if status['processing'] else '',
    'ERR' if status['error'] else '',
  ]
  left = '  ' + ''.join(f'{word:<6}' for word in to_print)
  right = f'{status["profile_name"]}      costs: {(status["costs"] / 100):.2f}$  '
  return { 'left': left, 'right': right  }

def makeStatusLinePlugin(status):
  to_print = [
    'MIC' if status['mic'] else '',
    'TRANS' if status['processing'] else '',
    'ERR' if status['error'] else '',
  ]
  line = f' {status["profile_name"]} ' + ''.join(f'{word:<6}' for word in to_print)
  return line
