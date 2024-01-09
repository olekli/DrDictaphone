# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import asyncio
from drdictaphone.client import Client
import logging

logger_config = {
  'level': logging.DEBUG,
  'filename': './drdictaphone-client.log',
  'format': '%(asctime)s %(levelname)s: %(name)s: %(message)s'
}
logging.basicConfig(**logger_config)

async def main():
  async with Client() as client:
    await client

def runClient():
  asyncio.set_event_loop(asyncio.new_event_loop())
  asyncio.run(main())

if __name__ == '__main__':
  runClient()
