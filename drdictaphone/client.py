# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import asyncio
from mreventloop import connect
from drdictaphone.rpc import RpcClient
from drdictaphone.client_ui import ClientUi

class Client:
  def __init__(self):
    self.rpc_client = RpcClient()
    self.ui = ClientUi()
    connect(self.ui, 'start_rec', self.rpc_client.request, 'start_rec')
    connect(self.ui, 'stop_rec', self.rpc_client.request, 'stop_rec')
    connect(self.ui, 'pause_mic', self.rpc_client.request, 'pause_mic')
    connect(self.ui, 'unpause_mic', self.rpc_client.request, 'unpause_mic')
    connect(self.ui, 'discard_rec', self.rpc_client.request, 'discard_rec')
    connect(self.ui, 'query_profiles', self.rpc_client.request, 'query_profiles')
    connect(self.ui, 'profile_selected', self.rpc_client.request, 'profile_selected')
    connect(self.ui, 'clear_buffer', self.rpc_client.request, 'clear_buffer')
    connect(self.rpc_client, 'result', self.ui, 'onResult')
    connect(self.rpc_client, 'status', self.ui, 'onStatus')
    connect(self.rpc_client, 'available_profiles', self.ui, 'onAvailableProfiles')

  async def __aenter__(self):
    await self.rpc_client.__aenter__()
    await self.ui.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.ui.__aexit__(exc_type, exc_value, traceback)
    await self.rpc_client.__aexit__(exc_type, exc_value, traceback)

  def __await__(self):
    yield from self.ui.__await__()
