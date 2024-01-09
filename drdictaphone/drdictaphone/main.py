# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import os
import signal
import time
import asyncio
import threading
from drdictaphone.config import initConfig, checkConfig
initConfig()
checkConfig()
from drdictaphone.server import Server
from drdictaphone.client import Client
from drdictaphone_shared.rpc import RpcBroker
import drdictaphone.logger_config
from drdictaphone import logger

logger = logger.get(__name__)

async def client_main():
  async with Client() as client:
    await client

async def server_main():
  async with RpcBroker(), Server() as server:
    await server

def server_entry():
  asyncio.set_event_loop(asyncio.new_event_loop())
  asyncio.run(server_main())

def client_entry():
  asyncio.set_event_loop(asyncio.new_event_loop())
  asyncio.run(client_main())

def runStandalone():
  server_thread = threading.Thread(target = server_entry)
  server_thread.start()

  client_thread = threading.Thread(target = client_entry)
  client_thread.start()

  while client_thread.is_alive() and server_thread.is_alive():
    client_thread.join(timeout = 1)
    server_thread.join(timeout = 3)
  logger.debug(f'exiting with thread status: {client_thread.is_alive()}, {server_thread.is_alive()}')
  if client_thread.is_alive() or server_thread.is_alive():
    os.kill(os.getpid(), signal.SIGTERM)
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGKILL)

if __name__ == '__main__':
  runStandalone()
