# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import asyncio
from mreventloop import Client as RpcClient
from mreventloop import connect

async def main():
  pub_events = [ 'status', 'result', 'available_profiles' ]
  rpc_client = RpcClient(
    'ipc:///tmp/drdictaphone.ipc',
    [ 'start_rec', 'stop_rec', 'profile_selected', 'shutdown', 'query_profiles' ],
    pub_events
  )

  for event_name in pub_events:
    connect(
      rpc_client, event_name,
      None, lambda *args, event_name=event_name, **kwargs: print(f'{event_name}: {args}')
    )

  async with rpc_client:
    result = await getattr(rpc_client.request, sys.argv[1])(*sys.argv[2:])
    print(f'{result}')
    assert result
    await asyncio.to_thread(input)

if __name__ == '__main__':
  asyncio.set_event_loop(asyncio.new_event_loop())
  asyncio.run(main())
