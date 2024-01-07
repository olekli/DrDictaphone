# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import signal
from drdictaphone.config import initConfig
initConfig()
from drdictaphone.server import Server
from drdictaphone_shared.rpc import RpcBroker
import logging

logger_config = {
  'level': logging.WARNING,
  'format': '%(asctime)s %(levelname)s: %(name)s: %(message)s'
}
logging.basicConfig(**logger_config)

async def main():
  async with RpcBroker(), Server() as server:
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, server.onShutdown)
    await server

def runServer():
  asyncio.set_event_loop(asyncio.new_event_loop())
  asyncio.run(main())

if __name__ == '__main__':
  runServer()
