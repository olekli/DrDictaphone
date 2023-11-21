# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logging.basicConfig(
  level = logging.WARNING,
#  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  format='%(levelname)s: %(name)s: %(message)s'
)
