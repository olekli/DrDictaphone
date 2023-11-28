# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

from dotenv import load_dotenv
load_dotenv()
import os
import yaml
from datetime import datetime
from model.context import Context
from model.profile import Profile

def getApiKey(config_dir):
  with open(os.path.join(config_dir, 'config', 'openai_api_key'), 'rt') as file:
    return file.read().rstrip('\n')

config = {
  'openai_api_key': getApiKey(os.environ.get('CONFIG_DIR', '.')),
  'directories': {
    'config': os.environ.get('CONFIG_DIR', '.'),
    'output': os.environ.get('OUTPUT_DIR', '.'),
  }
}

def getProfilePath(profile):
  return os.path.join(config['directories']['config'], 'profile', f'{profile}.yaml')

def makeOutputFilename(path):
  now = datetime.now()
  timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
  path = makePath('output', path)
  os.makedirs(path, exist_ok = True)
  return os.path.join(path, f'{timestamp}.txt')

def makePath(type, path):
  if os.path.isabs(path):
    return path
  else:
    return os.path.join(config['directories'][type], path)

def readContentOrFile(content):
  if isinstance(content, str):
    with open(makePath('config', content), 'rt') as file:
      data = yaml.safe_load(file)
      return data
  else:
    return content

def transform(transformations, content):
  for key in content:
    if key in transformations:
      for transformation in transformations[key]:
        content[key] = transformation(content[key])
  return content

context_transformations = {
  'tools': [readContentOrFile],
  'gpt_model': [readContentOrFile],
  'options': [readContentOrFile],
  'instructions': [readContentOrFile]
}

profile_transformations = {
  'context': [readContentOrFile, lambda content: transform(context_transformations, content)]
}

def readModel(Model, filename, transformations):
  filename = makePath('config', filename)
  with open(filename, 'rt') as file:
    data = yaml.safe_load(file)
  data = transform(transformations, data)
  return Model(**data)

def readProfile(filename):
  return readModel(Profile, filename, profile_transformations)
