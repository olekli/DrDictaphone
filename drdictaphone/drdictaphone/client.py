# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import sys
import asyncio
from mreventloop import connect
from drdictaphone_shared.rpc import RpcClient
from drdictaphone.client_ui import ClientUi

class Client:
  def __init__(self):
    self.rpc_client = RpcClient()
    self.ui = ClientUi()
    connect(self.ui, 'start_rec', self.rpc_client.publish, 'start_rec')
    connect(self.ui, 'stop_rec', self.rpc_client.publish, 'stop_rec')
    connect(self.ui, 'pause_mic', self.rpc_client.publish, 'pause_mic')
    connect(self.ui, 'unpause_mic', self.rpc_client.publish, 'unpause_mic')
    connect(self.ui, 'discard_rec', self.rpc_client.publish, 'discard_rec')
    connect(self.ui, 'query_profiles', self.rpc_client.publish, 'query_profiles')
    connect(self.ui, 'profile_selected', self.rpc_client.publish, 'profile_selected')
    connect(self.ui, 'clear_buffer', self.rpc_client.publish, 'clear_buffer')
    connect(self.ui, 'shutdown', self.rpc_client.publish, 'shutdown')
    connect(self.ui, 'query_status', self.rpc_client.publish, 'query_status')
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
