# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from dotenv import load_dotenv
load_dotenv()
import os
import sys
import yaml
from datetime import datetime
from drdictaphone.model.profile import Profile
from drdictaphone.find_ffmpeg import findFfmpeg
from drdictaphone_shared.config_path import getConfigPath

config = {
  'logfile': os.environ.get('LOG_FILE', 'drdictaphone.log'),
  'paths': {
    'config': {},
    'output': {}
  }
}

default_application_mode = 'frozen' \
  if (getattr(sys, 'frozen', False) or 'DRDICTAPHONE_PROD' in os.environ) \
  else ''

def initConfig(application_mode = default_application_mode):
  findFfmpeg()

  config['application_mode'] = application_mode

  if config['application_mode'] == 'frozen':
    user_path = getConfigPath()

    if not user_path:
      print('Configuration not set up properly.')
      print('`~/.drdictaphonerc` needs to contain the path to your installation.')
      sys.exit(1)

    config['loglevel'] = os.environ.get('LOG_LEVEL', 'INFO')
    config['paths']['application'] = os.path.dirname(os.path.abspath(__file__))
    config['paths']['log'] = os.path.join(user_path, config['logfile'])
    config['paths']['config']['user'] = os.path.join(user_path)
    config['paths']['config']['internal'] = config['paths']['application']
    config['paths']['output']['user'] = os.path.join(user_path, 'output')
    config['paths']['openai_api_key'] = os.path.join(config['paths']['config']['user'], 'config', 'openai_api_key')

  else:
    config['loglevel'] = os.environ.get('LOG_LEVEL', 'DEBUG')
    config['paths']['application'] = os.path.dirname(os.path.abspath(__file__))
    config['paths']['log'] = os.path.join(config['paths']['application'], config['logfile'])
    config['paths']['config']['user'] = config['paths']['application']
    config['paths']['output']['user'] = os.path.join(config['paths']['application'], 'output')
    config['paths']['config']['internal'] = config['paths']['application']
    config['paths']['openai_api_key'] = os.path.join(config['paths']['config']['user'], 'config', 'openai_api_key')

  createConfigSkel()
  config['openai_api_key'] = getApiKey()

def checkConfig():
  if not config['openai_api_key']:
    print(f'Please provide OpenAI API key in file: {config["paths"]["openai_api_key"]}')
    sys.exit(1)

def getPath(type, path):
  if os.path.isabs(path):
    return path
  else:
    if 'user' in config['paths'][type]:
      user_path = os.path.join(config['paths'][type]['user'], path)
      if not os.path.exists(user_path) and 'internal' in config['paths'][type]:
        user_path = os.path.join(config['paths'][type]['internal'], path)
      return user_path
    elif isinstance(config['paths'][type], str):
      user_path = os.path.join(config['paths'][type], path)
      return user_path
    else:
      assert False

def createConfigSkel():
  os.makedirs(os.path.join(config['paths']['config']['user'], 'config'), exist_ok = True)
  if not os.path.exists(os.path.join(config['paths']['config']['user'], 'profile')):
    os.makedirs(os.path.join(config['paths']['config']['user'], 'profile'), exist_ok = True)
    source = os.path.join(config['paths']['config']['internal'], 'profile', 'default.yaml')
    target = os.path.join(config['paths']['config']['user'], 'profile', 'default.yaml')
    with open(source, 'rt') as file:
      default = file.read()
    with open(target, 'wt') as file:
      file.write(default)

def getApiKey():
  path = config['paths']['openai_api_key']
  key = None
  if os.path.exists(path):
    with open(path, 'rt') as file:
      key = file.read().rstrip('\n')
  else:
    with open(path, 'at'):
      pass
  if not key:
    return None
  return key

def getProfilePath(profile):
  profile_path = getPath('config', 'profile')
  if profile:
    profile_path = os.path.join(profile_path, f'{profile}.yaml')
  return profile_path

def makeOutputFilename(path):
  now = datetime.now()
  timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
  path = getPath('output', path)
  os.makedirs(path, exist_ok = True)
  return os.path.join(path, f'{timestamp}.txt')

def readContentOrFile(content):
  if isinstance(content, str):
    with open(getPath('config', content), 'rt') as file:
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
  'gpt_model': [readContentOrFile],
  'post_processor': [readContentOrFile, lambda content: transform(context_transformations, content)]
}

profile_defaults = {
  'post_processor': 'post_processor/default.yaml',
  'gpt_model': None,
  'options': None,
  'output_command': None,
}

def readModel(Model, filename, defaults, transformations):
  filename = getPath('config', filename)
  with open(filename, 'rt') as file:
    data = yaml.safe_load(file)
  data = transform(transformations, applyDefaults(defaults, data))
  data['post_processor']['topic'] = data['topic']
  data['post_processor']['language'] = data['language']
  if data['gpt_model']:
    data['post_processor']['gpt_model'] = data['gpt_model']
  if data['options']:
    data['post_processor']['options'] = { **data['post_processor']['options'], **data['options'] }
  if 'id' in Model.__fields__:
    data['id'] = os.path.splitext(os.path.basename(filename))[0]
  return Model(**data)

def readProfile(filename):
  profile = readModel(Profile, filename, profile_defaults, profile_transformations)
  return profile
