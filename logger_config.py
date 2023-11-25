# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from dotenv import load_dotenv
load_dotenv()
import os

config = {
  'level': logging.WARNING,
  'format': '%(levelname)s: %(name)s: %(message)s'
#  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

filename = os.environ.get('LOG_FILE', None)
if filename:
  config['filename'] = filename

logging.basicConfig(**config)
