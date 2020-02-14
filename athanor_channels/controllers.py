from django.conf import settings

from evennia.utils.utils import class_from_module

from athanor.controllers.base import AthanorController
from athanor_channels.models import ChannelSystemBridge
from athanor_channels.channels.base import AbstractChannelSystem


class AthanorChannelController(AthanorController):
    system_name = 'CHANNEL'

    def do_load(self):
        """
        This loads the fallbacks for when more specific settings are not defined in settings.py.
        """

        for sys_key, sys_data in settings.CHANNEL_SYSTEMS.items():
            sys_typeclass = sys_data.get("system_typeclass")
            cat_typeclass = sys_data.get("category_typeclass")
            chan_typeclass = sys_data.get("channel_typeclass")
            command_class = sys_data.get("command_class")
            try:
                found = self.find_system(sys_key)
                found.integrity_check(sys_typeclass, cat_typeclass, chan_typeclass, command_class)
                found.at_start()
            except ValueError as e:
                self.create_system(sys_key, sys_typeclass, cat_typeclass, chan_typeclass, command_class)

    def systems(self):
        return [bridge.db_script for bridge in ChannelSystemBridge.objects.all()]

    def create_system(self, sys_key, system_typeclass, category_typeclass, channel_typeclass, command_class):
        sys_typeclass = class_from_module(system_typeclass)
        new_system = sys_typeclass.create_channel_system(sys_key, category_typeclass, channel_typeclass, command_class)
        return new_system

    def find_system(self, sys_key):
        if isinstance(sys_key, ChannelSystemBridge):
            return sys_key.db_script
        if isinstance(sys_key, AbstractChannelSystem):
            return sys_key
        if (chan_sys := ChannelSystemBridge.objects.filter(db_system_key=sys_key).first()):
            return chan_sys.db_script
        raise ValueError(f"Channel System {sys_key} does not exist!")

    def create_category(self, session, sys_key, name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.create_category(session, name)

    def rename_category(self, session, sys_key, name, new_name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.rename_category(session, name, new_name)

    def delete_category(self, session, sys_key, name, verify_name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.rename_category(session, name, verify_name)

    def lock_system(self, session, sys_key, lock_data):
        chan_sys = self.find_system(sys_key)
        return chan_sys.lock(session, lock_data)

    def lock_category(self, session, sys_key, name, lock_data):
        chan_sys = self.find_system(sys_key)
        return chan_sys.lock_category(session, name, lock_data)

    def config_category(self, session, sys_key, name, config_op, config_val):
        chan_sys = self.find_system(sys_key)
        return chan_sys.config_category(session, name, config_op, config_val)

    def create_channel(self, session, sys_key, category, name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.create_channel(session, category, name)

    def rename_channel(self, session, sys_key, category, name, new_name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.rename_channel(session, category, name, new_name)

    def delete_channel(self, session, sys_key, category, name, verify_name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.delete_channel(session, category, name, verify_name)

    def lock_channel(self, session, sys_key, category, name, lock_data):
        chan_sys = self.find_system(sys_key)
        return chan_sys.lock_channel(session, category, name, lock_data)

    def config_channel(self, session, sys_key, category, name, config_op, config_val):
        chan_sys = self.find_system(sys_key)
        return chan_sys.config_channel(session, category, name, config_op, config_val)

    def grant_system(self, session, sys_key, user, position):
        chan_sys = self.find_system(sys_key)
        return chan_sys.grant(session, user, position)
    
    def grant_category(self, session, sys_key, name, user, position):
        chan_sys = self.find_system(sys_key)
        return chan_sys.grant_category(session, name, user, position)
    
    def grant_channel(self, session, sys_key, category, name, user, position):
        chan_sys = self.find_system(sys_key)
        return chan_sys.grant_channel(session, category, name, user, position)

    def revoke_system(self, session, sys_key, user, position):
        chan_sys = self.find_system(sys_key)
        return chan_sys.revoke(session, user, position)

    def revoke_category(self, session, sys_key, name, user, position):
        chan_sys = self.find_system(sys_key)
        return chan_sys.revoke_category(session, name, user, position)

    def revoke_channel(self, session, sys_key, category, name, user, position):
        chan_sys = self.find_system(sys_key)
        return chan_sys.revoke_channel(session, category, name, user, position)

    def ban_system(self, session, sys_key, user, duration):
        chan_sys = self.find_system(sys_key)
        return chan_sys.ban(session, user, duration)

    def ban_category(self, session, sys_key, name, user, duration):
        chan_sys = self.find_system(sys_key)
        return chan_sys.ban_category(session, name, user, duration)

    def ban_channel(self, session, sys_key, category, name, user, duration):
        chan_sys = self.find_system(sys_key)
        return chan_sys.ban_channel(session, category, name, user, duration)
    
    def unban_system(self, session, sys_key, user):
        chan_sys = self.find_system(sys_key)
        return chan_sys.unban(session, user)

    def unban_category(self, session, sys_key, name, user):
        chan_sys = self.find_system(sys_key)
        return chan_sys.unban_category(session, name, user)

    def unban_channel(self, session, sys_key, category, name, user):
        chan_sys = self.find_system(sys_key)
        return chan_sys.unban_channel(session, category, name, user)

    def who_channel(self, session, sys_key, category, name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.who_channel(session, category, name)

    def examine_system(self, session, sys_key):
        chan_sys = self.find_system(sys_key)
        return chan_sys.examine(session)

    def examine_category(self, session, sys_key, name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.examine_category(session, name)

    def examine_channel(self, session, sys_key, category, name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.examine_channel(session, category, name)

    def target_channel(self, session, sys_key, category, name):
        chan_sys = self.find_system(sys_key)
        return chan_sys.target_channel(session, category, name)

    def describe_system(self, session, sys_key, description):
        raise ValueError("Cannot describe a system!")

    def describe_category(self, session, sys_key, category, description):
        chan_sys = self.find_system(sys_key)
        return chan_sys.describe_category(session, category, description)

    def describe_channel(self, session, sys_key, category, name, description):
        chan_sys = self.find_system(sys_key)
        return chan_sys.describe_channel(session, category, name, description)