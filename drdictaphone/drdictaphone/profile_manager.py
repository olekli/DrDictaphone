# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

import os
import aiofiles
import yaml
from mreventloop import emits, slot, has_event_loop
from drdictaphone.config import readProfile, getProfilePath
from drdictaphone import logger

logger = logger.get(__name__)

@has_event_loop('event_loop')
@emits('events', [ 'profile_change', 'available_profiles' ])
class ProfileManager:
  def __init__(self):
    self.profile_name = None
    self.profile = None

  @slot
  def onProfileSelected(self, profile_name):
    logger.debug(f'profile selected: {profile_name}')
    self.profile_name = profile_name
    profile_path = getProfilePath(self.profile_name)
    os.utime(profile_path, None)
    self.profile = readProfile(profile_path)
    self.events.profile_change(self.profile)

  @slot
  def onAddTopic(self, topic):
    self.profile.raw['topic'].append(topic)
    profile_path = getProfilePath(self.profile_name)
    with open(profile_path, 'w+t') as file:
      file.write(yaml.dump(self.profile.raw))
    self.profile = readProfile(profile_path)
    self.events.profile_change(self.profile)

  @slot
  def onQueryProfiles(self):
    profile_path = getProfilePath(None)
    available_profiles = os.listdir(profile_path)
    available_profiles.sort(
      key = lambda x: os.path.getatime(os.path.join(profile_path, x)),
      reverse = True
    )
    available_profiles = [
      x for x, y in [
        os.path.splitext(entry) for entry in available_profiles
      ]
    ]
    self.events.available_profiles(available_profiles)
