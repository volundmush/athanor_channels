from django.conf import settings

from evennia.utils.utils import class_from_module

from athanor.controllers.base import AthanorController
from athanor_channels.models import ChannelSystemBridge
from athanor_channels.channels import AbstractChannelSystem


class AthanorChannelController(AthanorController):
    system_name = 'CHANNEL'

    def do_load(self):
        """
        This loads the fallbacks for when more specific settings are not defined in settings.py.
        """

        for sys_key, sys_data in settings.CHANNEL_SYSTEMS.items():
            sys_typeclass = sys_data.get("system_typeclass", settings.CHANNEL_SYSTEM_TYPECLASS)
            cat_typeclass = sys_data.get("category_typeclass", settings.CHANNEL_CATEGORY_TYPECLASS)
            chan_typeclass = sys_data.get("channel_typeclass", settings.CHANNEL_CHANNEL_TYPECLASS)
            command_class = sys_data.get("command_class", settings.CHANNEL_COMMAND_CLASS)
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
