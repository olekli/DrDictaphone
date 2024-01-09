# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import sys
import asyncio
from mreventloop import connect
from drdictaphone_shared.rpc import RpcClient, pub_event_names

async def sendRequestAsync(method, *args):
  rpc_client = RpcClient()

  async with rpc_client:
    await getattr(rpc_client.publish, method)(*args)

def sendRequest(method, *args):
  asyncio.set_event_loop(asyncio.new_event_loop())
  asyncio.run(sendRequestAsync(method, *args))

if __name__ == '__main__':
  sendRequest(*sys.argv[1:])
