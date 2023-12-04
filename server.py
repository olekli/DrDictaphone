# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import socket
import signal
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from main import Main
import logger_config
import logger

logger = logger.get(__name__)

class Server:
  def __init__(self, socket_path):
    self.socket_path = socket_path
    try:
      os.unlink(self.socket_path)
    except OSError:
      if os.path.exists(self.socket_path):
        raise

    self.server = SimpleJSONRPCServer(
      socket_path,
      address_family = socket.AF_UNIX
    )
    self.main = None

    self.server.register_function(self.setProfile, 'setProfile')

  def setProfile(self, profile_name):
    if self.main:
        self.main.__exit__(None, None, None)
    self.main = Main(profile_name)
    self.main.__enter__()

  def startRecording(self):
    self.main.pipeline.onStarRec()

  def run(self):
    logger.info(f'starting server on: {self.socket_path}')
    self.server.serve_forever()
    if self.main:
      self.main.__exit__(None, None, None)

  def stop(self):
    logger.info(f'shutting down...')
    self.server.server_close()
    if self.main:
      self.main.__exit__(None, None, None)
    os.unlink(self.socket_path)

server = None

def signal_handler(signum, frame):
  if server:
    server.stop()
  exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
  server = Server('/tmp/drdictaphone')
  server.run()
