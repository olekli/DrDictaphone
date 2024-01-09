# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import sys
import asyncio
from mreventloop import connect, SyncEvent
from drdictaphone_shared.rpc import RpcClient, pub_event_names

async def runClientCommand_(method, result_event_name, *args):
  rpc_client = RpcClient()

  async with rpc_client:
    result_event = SyncEvent(getattr(rpc_client.events, result_event_name))
    await getattr(rpc_client.publish, method)(*args)
    result = await result_event
    return result

def runClientCommand(method, result_event_name, *args):
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  return loop.run_until_complete(runClientCommand_(method, result_event_name, *args))

def loadFile(filename):
  result = runClientCommand('load_file', 'result', filename)
  print('\n'.join(result))

def setProfile(profile_name):
  result = runClientCommand('profile_selected', 'status', profile_name)
  print(f'profile selected: {result["profile_name"]}')

client_commands = {
  'transcribe-file': loadFile,
  'set-profile': setProfile,
}
