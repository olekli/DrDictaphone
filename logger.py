# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from config import config

def get(module):
  logger = logging.getLogger(module)
  logger.setLevel(logging.getLevelName(config['loglevel']))
  return logger
