# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import aiofiles
import yaml
from mreventloop import emits, slot, has_event_loop, forwards
from drdictaphone.config import readProfile, getProfilePath

@has_event_loop('event_loop')
@emits('events', [ 'profile_change' ])
class ProfileManager:
  def __init__(self):
    self.profile_name = None
    self.profile = None

  @slot
  def onProfileSelected(self, profile_name):
    self.profile_name = profile_name
    profile_path = getProfilePath(self.profile_name)
    os.utime(profile_path, None)
    self.profile = readProfile(profile_path)
    self.events.profile_change(self.profile)

  @slot
  def onAddTopic(self, topic)
    self.profile.raw['topic'].append(topic)
    profile_path = getProfilePath(self.profile_name)
    with open(profile_path, 'w+t') as file:
      file.write(yaml.dump(self.profile.raw)
    self.profile = readProfile(profile_path)
    self.events.profile_change(self.profile)
