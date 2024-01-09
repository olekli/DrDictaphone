# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import argparse
from drdictaphone.client_commands import client_commands

parser = argparse.ArgumentParser(description = 'DrDictaphone')
subparsers = parser.add_subparsers(dest = 'command')

command_parser = subparsers.add_parser('install', help = 'Install run script and configuration')
command_parser.add_argument('directory', type = str, help = 'Directory for DrDictaphone')
command_parser = subparsers.add_parser('server', help = 'Only run server')
command_parser = subparsers.add_parser('shutdown', help = 'Shutdown a running server')
command_parser = subparsers.add_parser('client', help = 'Only run client')

for command in client_commands:
  command_parser = subparsers.add_parser(command)
  command_parser.add_argument('arg', type = str)

args = parser.parse_args()

if args.command == 'install':
  from drdictaphone.install import install
  install(args.directory)
elif args.command == 'server':
  from drdictaphone.server_main import runServer
  runServer()
elif args.command == 'client':
  from drdictaphone.client_main import runClient
  runClient()
elif args.command == 'shutdown':
  from drdictaphone.cli_client import sendRequest
  sendRequest('shutdown')
elif args.command in client_commands:
  client_commands[args.command](args.arg)
else:
  from drdictaphone.main import runStandalone
  runStandalone()
