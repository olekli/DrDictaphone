# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from mreventloop import Peer, Broker

req_event_names = [
  'start_rec',
  'stop_rec',
  'toggle_rec',
  'discard_rec',
  'pause_mic',
  'unpause_mic',
  'profile_selected',
  'shutdown',
  'query_profiles',
  'clear_buffer',
  'query_status',
]

pub_event_names = [
  'status',
  'result',
  'available_profiles',
]

in_socket_path = 'ipc:///tmp/drdictaphone_in.ipc'
out_socket_path = 'ipc:///tmp/drdictaphone_out.ipc'

RpcBroker = lambda: Broker(in_socket_path, out_socket_path)
RpcServer = lambda: Peer(in_socket_path, out_socket_path, req_event_names, pub_event_names)
RpcClient = lambda: Peer(in_socket_path, out_socket_path, pub_event_names, req_event_names)
