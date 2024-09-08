# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import logging
from drdictaphone.config import config

logger_config = {
  'level': logging.INFO,
  'filename': config['paths']['log'],
  'format': '%(asctime)s %(levelname)s: %(name)s: %(message)s'
}

logging.basicConfig(**logger_config)
