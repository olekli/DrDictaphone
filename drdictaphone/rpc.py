# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import Server, Client

req_event_names = [
  'start_rec',
  'stop_rec',
  'discard_rec',
  'pause_mic',
  'unpause_mic',
  'profile_selected',
  'shutdown',
  'query_profiles',
  'clear_buffer',
]

pub_event_names = [
  'status',
  'result',
  'available_profiles',
]

socket_path = 'ipc:///tmp/drdictaphone.ipc'

RpcServer = lambda: Server(socket_path, req_event_names, pub_event_names)
RpcClient = lambda: Client(socket_path, req_event_names, pub_event_names)
