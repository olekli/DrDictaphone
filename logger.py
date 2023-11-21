# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from dotenv import load_dotenv
load_dotenv()
import os

def get(module):
  logger = logging.getLogger(module)
  logger.setLevel(logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO')))
  return logger
