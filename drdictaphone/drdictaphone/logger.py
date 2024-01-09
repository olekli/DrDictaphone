# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import logging
from drdictaphone.config import config

def get(module):
  logger = logging.getLogger(module)
  logger.setLevel(logging.getLevelName(config['loglevel']))
  return logger
