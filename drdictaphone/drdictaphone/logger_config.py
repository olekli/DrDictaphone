# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from drdictaphone.config import config

logger_config = {
  'level': logging.INF,
  'filename': config['paths']['log'],
  'format': '%(asctime)s %(levelname)s: %(name)s: %(message)s'
}

logging.basicConfig(**logger_config)
