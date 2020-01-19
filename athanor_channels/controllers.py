from django.conf import settings
from django.db.models import Q

from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace

from athanor.gamedb.scripts import AthanorGlobalScript
from athanor_channels.channels import AthanorAccountChannel, AthanorObjectChannel, AthanorChannelSystem, \
    AthanorChannelCategory
from athanor.utils.valid import simple_name
from athanor.utils.text import partial_match
from athanor_channels.models import ChannelCategoryBridge, ChannelBridge, AccountChannelSubscription, \
    ObjectChannelSubscription, ChannelSystemBridge
from athanor_channels import messages as cmsg


class AthanorChannelController(AthanorGlobalScript):
    system_name = 'CHANNEL'
    option_dict = {
        'system_locks': ('Locks governing Faction System.', 'Lock',
                         "create:perm(Admin);delete:perm(Admin);admin:perm(Admin)"),
        'faction_locks': ('Default/Fallback locks for all Factions.', 'Lock',
                        "see:all();invite:fmember();accept:fmember();apply:all();admin:fsuperuser()")
    }

    def at_start(self):
        """
        This loads the fallbacks for when more specific settings are not defined in settings.py.
        """
        try:
            chan_system_typeclass = settings.CHANNEL_SYSTEM_TYPECLASS
            self.ndb.chan_system_typeclass = class_from_module(chan_system_typeclass,
                                                                 defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.chan_system_typeclass = AthanorChannelSystem

        try:
            chan_category_typeclass = settings.CHANNEL_CATEGORY_TYPECLASS
            self.ndb.chan_category_typeclass = class_from_module(chan_category_typeclass,
                                                                 defaultpaths=settings.TYPECLASS_PATHS)
        except Exception:
            log_trace()
            self.ndb.chan_category_typeclass = AthanorChannelCategory

        try:
            obj_channel_typeclass = settings.OBJECT_CHANNEL_TYPECLASS
            self.ndb.obj_channel_typeclass = class_from_module(obj_channel_typeclass,
                                                               defaultpaths=settings.TYPECLASS_PATHS)

        except Exception:
            log_trace()
            self.ndb.obj_channel_typeclass = AthanorObjectChannel

        try:
            acc_channel_typeclass = settings.ACCOUNT_CHANNEL_TYPECLASS
            self.ndb.acc_channel_typeclass = class_from_module(acc_channel_typeclass,
                                                               defaultpaths=settings.TYPECLASS_PATHS)

        except Exception:
            log_trace()
            self.ndb.acc_channel_typeclass = AthanorAccountChannel

    def systems(self, key):
        return [bridge.db_script for bridge in ChannelSystemBridge.objects.filter(db_system_key=key)]

    def find_system(self, sys_key):
        if (chan_sys := ChannelSystemBridge.objects.filter(db_system_key=sys_key).first()):
            return chan_sys
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
