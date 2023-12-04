# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from drdictaphone.config import initConfig
initConfig()
from drdictaphone.server import Server
import logging

logger_config = {
  'level': logging.WARNING,
  'format': '%(asctime)s %(levelname)s: %(name)s: %(message)s'
}
logging.basicConfig(**logger_config)

from drdictaphone import logger

async def main():
  async with Server() as server:
    await server

if __name__ == '__main__':
  logger = logger.get(__name__)

  asyncio.set_event_loop(asyncio.new_event_loop())
  asyncio.run(main())
