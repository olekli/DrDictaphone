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

def createSkel():
  dirs = [ 'profile', 'context', 'instructions', 'config' ]
  for dir in dirs:
    os.makedirs(os.path.join(config['directories']['config'], dir), exist_ok = True)

def getProfilePath(profile):
  profile_path = os.path.join(config['directories']['config'], 'profile')
  if profile:
    profile_path = os.path.join(profile_path, f'{profile}.yaml')
  return profile_path

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

def applyDefaults(defaults, content):
  for key in defaults:
    if key not in content:
      content[key] = defaults[key]
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
  'post_processor': [readContentOrFile, lambda content: transform(context_transformations, content)]
}

profile_defaults = {
  'post_processor': 'post_processor/default.yaml',
  'gpt_model': None,
  'options': None
}

def readModel(Model, filename, defaults, transformations):
  filename = makePath('config', filename)
  with open(filename, 'rt') as file:
    data = yaml.safe_load(file)
  data = transform(transformations, applyDefaults(defaults, data))
  data['post_processor']['topic'] = data['topic']
  data['post_processor']['language'] = data['language']
  if data['gpt_model']:
    data['post_processor']['gpt_model'] = data['gpt_model']
  if data['options']:
    data['post_processor']['options'] = { **data['post_processor']['options'], **data['options'] }
  return Model(**data)

def readProfile(filename):
  profile = readModel(Profile, filename, profile_defaults, profile_transformations)
  return profile
