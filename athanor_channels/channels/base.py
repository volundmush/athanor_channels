import re
from evennia.comms.comms import DefaultChannel
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property, class_from_module
from evennia.utils.logger import log_trace

from athanor.gamedb.scripts import AthanorOptionScript
from athanor.utils.text import partial_match
from athanor.gamedb.base import HasRenderExamine, HasOps

from athanor_channels.models import ChannelSystemBridge, ChannelCategoryBridge, ChannelBridge
from athanor_channels import messages as cmsg
from athanor_channels.commands.base import AbstractChannelCommand


class HasChanOps(HasOps, HasRenderExamine):
    """
    Limited Mixin for providing some permissions storage to the Channel System.
    """
    grant_msg = cmsg.Grant
    revoke_msg = cmsg.Revoke
    ban_msg = cmsg.Ban
    unban_msg = cmsg.Unban
    lock_msg = cmsg.Lock
    config_msg = cmsg.Config

    def render_examine(self, viewer, callback=True):
        return self.render_examine_callback(None, viewer, callback=callback)

    def examine(self, session):
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        return self.render_examine(enactor, callback=False)


class AbstractChannel(HasChanOps, DefaultChannel):
    """
    Abstract class for Account and Object channels. Don't use this directly!
    """
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")
    operate_operation = "channel_operate"
    moderate_operation = "channel_moderate"
    use_operation = 'channel_use'
    examine_type = 'channel'

    @property
    def cname(self):
        return self.bridge.cname

    @property
    def fullname(self):
        return f"{self.system}/{self.category.cname}/{self.cname}"

    def generate_substitutions(self, viewer):
        return {"name": self.key,
                "cname": self.bridge.cname,
                "fullname": self.fullname,
                'typename': 'Channel'}

    @property
    def bridge(self):
        return self.channel_bridge

    @property
    def category(self):
        return self.bridge.db_category.db_script

    @property
    def system(self):
        return self.category.system

    @property
    def parent(self):
        return self.category

    @lazy_property
    def listeners(self):
        """
        Since the number of subscribers to a channel could potentially grow very large, the listeners
        property is a cache of subscriptions that are actually actively listening to the channel.
        """
        return set()

    def add_listener(self, listener):
        self.listeners.add(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def create_bridge(self, category, name, clean_name, unique_key=None):
        if hasattr(self, 'channel_bridge'):
            return
        ChannelBridge.objects.create(db_channel=self, db_name=clean_name, db_iname=clean_name.lower(), db_cname=name,
                                     db_category=category.channel_category_bridge, db_unique_key=unique_key)

    @classmethod
    def create_channel(cls, category, key, unique_key=None):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Channel Name.")
        if not cls.re_name.match(clean_key):
            raise ValueError("Channel Names must be EXPLANATION HERE.")
        if category.channel_category_bridge.channels.filter(db_iname=clean_key.lower()).count():
            raise ValueError("Name conflicts with another Channel.")
        channel, errors = cls.create(clean_key)
        if channel:
            channel.create_bridge(category, key.raw(), clean_key, unique_key)
        else:
            raise ValueError(errors)
        return channel

    def rename(self, key):
        """
        Renames a channel and updates all relevant fields.

        Args:
            key (str): The channel's new name. Can include ANSI codes.

        Returns:
            key (ANSIString): The successful key set.
        """
        key = ANSIString(key)
        clean_key = key.clean()
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Channel Name.")
        if not self.re_name.match(clean_key):
            raise ValueError("Channel name does not meet standards. Avoid double spaces and special characters.")
        bridge = self.bridge
        if bridge.db_category.channels.filter(db_iname=clean_key.lower()).exclude(db_channel=self).count():
            raise ValueError("Name conflicts with another Character.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key.raw()
        bridge.save(update_fields=['db_name', 'db_iname', 'db_cname'])
        return key

    def __str__(self):
        return str(self.key)

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_puppet_or_account()

    def render_prefix(self, recipient, sender):
        return f"<{self.bridge.cname}>"

    def broadcast(self, text, sending_session=None):
        sender = self.get_sender(sending_session)
        for listener in self.listeners:
            prefix = self.render_prefix(listener, sender)
            listener.msg(f"{prefix} {text.render(viewer=listener)}")

    def check_access(self, checker, lock):
        return self.access(checker, lock) or self.category.access(checker, lock)


class AbstractChannelCategory(HasChanOps, AthanorOptionScript):
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")
    operate_operation = "channel_category_operate"
    moderate_operation = "channel_category_moderate"
    use_operation = 'channel_category_use'

    @property
    def cname(self):
        return self.bridge.cname

    @property
    def fullname(self):
        return f"{self.system}/{self.bridge.cname}"

    def generate_substitutions(self, viewer):
        return {"name": str(self),
                "cname": self.bridge.cname,
                "fullname": self.fullname,
                'typename': 'Channel Category'}

    def __str__(self):
        return str(self.key)

    @property
    def bridge(self):
        return self.channel_category_bridge

    @property
    def system(self):
        return self.bridge.db_system.db_script

    @property
    def parent(self):
        return self.system

    def create_bridge(self, chan_sys, name, clean_name, unique_key=None):
        if hasattr(self, 'channel_category_bridge'):
            return
        ChannelCategoryBridge.objects.create(db_script=self, db_name=clean_name, db_iname=clean_name.lower(), db_cname=name,
                                     db_system=chan_sys.channel_system_bridge, db_unique_key=unique_key)

    @classmethod
    def create_channel_category(cls, chan_sys, key):
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Channel Category Name.")
        if not cls.re_name.match(clean_key):
            raise ValueError("Channel Category names must be EXPLANATION.")
        if chan_sys.channel_system_bridge.channel_categories.filter(db_iname=clean_key.lower()).count():
            raise ValueError("Name conflicts with another Channel Category.")
        script, errors = cls.create(clean_key, persistent=True)
        if script:
            script.create_bridge(chan_sys, key.raw(), clean_key)
        else:
            raise ValueError(errors)
        return script

    def rename(self, key):
        """
        Renames a channel category and updates all relevant fields.

        Args:
            key (str): The category's new name. Can include ANSI codes.

        Returns:
            key (ANSIString): The successful key set.
        """
        key = ANSIString(key)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Channel CategoryName.")
        if not self.re_name.match(clean_key):
            raise ValueError("Channel Category name does not meet standards. Avoid double spaces and special characters.")
        bridge = self.bridge
        if bridge.db_system.channel_categories.filter(db_iname=clean_key.lower()).exclude(db_script=self).count():
            raise ValueError("Name conflicts with another Channel Category.")
        self.key = clean_key
        bridge.db_name = clean_key
        bridge.db_iname = clean_key.lower()
        bridge.db_cname = key.raw()
        bridge.save(update_fields=['db_name', 'db_iname', 'db_cname'])
        return key

    def channels(self):
        return [c.db_channel for c in self.bridge.channels.all()]

    def visible_channels(self, session):
        return [channel for channel in self.channels() if channel.access(session, 'listen')]

    def find_channel(self, session, name):
        if isinstance(name, AbstractChannel):
            return name
        if isinstance(name, ChannelBridge):
            return name.db_channel
        if (found := partial_match(name, self.visible_channels(session))):
            return found
        raise ValueError(f"Cannot Find Channel: {name}")

    def check_access(self, checker, lock):
        return self.access(checker, lock) or self.system.access(checker, lock)

    def create_channel(self, session, name):
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        new_channel = self.system.ndb.channel_typeclass.create_channel(self, name)
        entities = {'enactor': enactor, 'target': new_channel}
        cmsg.Create(entities).send()
        return new_channel

    def rename_channel(self, session, name, new_name):
        channel = self.find_channel(session, name)
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        if not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        old_name = channel.fullname
        changed_name = channel.rename(new_name)
        entities = {'enactor': enactor, 'target': channel}
        cmsg.Rename(entities, old_name=old_name).send()

    def delete_channel(self, session, name, verify_name):
        channel = self.find_channel(session, name)
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        if not verify_name and verify_name.lower() == str(channel).lower():
            raise ValueError("Verify value does not match channel name!")
        entities = {'enactor': enactor, 'target': channel}
        cmsg.Delete(entities).send()
        channel.delete()

    def lock_channel(self, session, name, lock_data):
        channel = self.find_channel(session, name)
        return channel.lock(session, lock_data)

    def config_channel(self, session, name, config_op, config_val):
        channel = self.find_channel(session, name)
        return channel.config(session, config_op, config_val)

    def grant_channel(self, session, name, position, user):
        channel = self.find_channel(session, name)
        return channel.grant(session, position, user)

    def revoke_channel(self, session, name, position, user):
        channel = self.find_channel(session, name)
        return channel.revoke(session, position, user)

    def ban_channel(self, session, name, user, duration):
        channel = self.find_channel(session, name)
        return channel.ban_channel(session, user, duration)

    def unban_channel(self, session, name, user):
        channel = self.find_channel(session, name)
        return channel.unban(session, user)

    def who_channel(self, session, name):
        channel = self.find_channel(session, name)
        return channel.who(session)

    def examine_channel(self, session, name):
        channel = self.find_channel(session, name)
        return channel.examine(session)


class AbstractChannelSystem(HasChanOps, AthanorOptionScript):
    operate_operation = "channel_system_operate"
    moderate_operation = "channel_system_moderate"
    use_operation = 'channel_system_use'

    def generate_substitutions(self, viewer):
        return {"name": str(self),
                "fullname": str(self),
                'typename': 'Channel System'}

    def __str__(self):
        return str(self.key)

    def at_start(self):
        if not hasattr(self, 'channel_system_bridge'):
            return
        bri = self.channel_system_bridge

        # Some safeguards are set here but they're really not how this works. These
        # imports are really not allowed to fail.
        try:
            self.ndb.category_typeclass = class_from_module(bri.db_category_typeclass)

        except Exception:
            log_trace()
            self.ndb.category_typeclass = AbstractChannelCategory

        try:
            self.ndb.channel_typeclass = class_from_module(bri.db_channel_typeclass)
        except Exception:
            log_trace()
            self.ndb.channel_typeclass = AbstractChannel

        try:
            self.ndb.command_class = class_from_module(bri.db_command_class)
        except Exception:
            log_trace()
            self.ndb.command_class = AbstractChannelCommand

        # This ensures that all categories and channels in this system will be using the proper
        # typeclass.
        for category in self.categories():
            if not category.is_typeclass(self.ndb.category_typeclass, exact=True):
                category.swap_typeclass(self.ndb.category_typeclass)
            for channel in category.channels():
                if not channel.is_typeclass(self.ndb.channel_typeclass, exact=True):
                    channel.swap_typeclass(self.ndb.channel_typeclass)

    def create_bridge(self, sys_key, category_typeclass, channel_typeclass, command_class):
        if hasattr(self, 'channel_system_bridge'):
            return
        ChannelSystemBridge.objects.create(db_script=self, db_command_class=command_class, db_system_key=sys_key,
                                           db_category_typeclass=category_typeclass,
                                           db_channel_typeclass=channel_typeclass)

    def parent_operator(self, user):
        return user.check_lock(f"oper({self.operate_operation})")

    def parent_moderator(self, user):
        return user.check_lock(f"oper({self.operate_operation})")

    @classmethod
    def create_channel_system(cls, name, category_typeclass, channel_typeclass, command_class):
        key = ANSIString(name)
        clean_key = str(key.clean())
        if '|' in clean_key:
            raise ValueError("Malformed ANSI in Channel System Name.")
        if ChannelSystemBridge.objects.filter(db_system_key=clean_key.lower()).count():
            raise ValueError("Name conflicts with another Channel System.")
        script, errors = cls.create(clean_key, persistent=True)
        if script:
            script.create_bridge(clean_key, category_typeclass, channel_typeclass, command_class)
            script.at_start()
        else:
            raise ValueError(errors)
        return script

    def integrity_check(self, sys_typeclass, cat_typeclass, chan_typeclass, command_class):
        reload = False
        if not self.is_typeclass(sys_typeclass, exact=True):
            self.swap_typeclass(sys_typeclass)
            reload = True
        bri = self.channel_system_bridge
        if not bri.category_typeclass == cat_typeclass:
            bri.category_typeclass = cat_typeclass
            reload = True
        if not bri.channel_typeclass == chan_typeclass:
            bri.channel_typeclass = chan_typeclass
            reload = True
        if not bri.command_class == command_class:
            bri.command_class = command_class
            reload = True
        if reload:
            self.at_start()

    def categories(self):
        return [b.db_script for b in self.channel_system_bridge.channel_categories.all().order_by('db_name')]

    def visible_categories(self, checker):
        return [cat for cat in self.categories() if cat.access(checker, 'see') or True]

    def find_category(self, session, name):
        if isinstance(name, AbstractChannelCategory):
            return name
        if isinstance(name, ChannelCategoryBridge):
            return name.db_script
        if (found := partial_match(name, self.visible_categories(session))):
            return found
        raise ValueError(f"Cannot find Channel Category: {name}")

    def create_category(self, session, name):
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        new_category = self.ndb.category_typeclass.create_channel_category(self, name)
        entities = {'enactor': enactor, 'target': new_category}
        cmsg.Create(entities).send()
        return new_category

    def rename_category(self, session, name, new_name):
        category = self.find_category(session, name)
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        old_name = category.fullname
        changed_name = category.rename(new_name)
        entities = {'enactor': enactor, 'target': category}
        cmsg.Rename(entities, old_name=old_name).send()
        return changed_name

    def delete_category(self, session, name, verify_name):
        category = self.find_category(session, name)
        if not (enactor := self.get_user(session)) or not self.is_operator(enactor):
            raise ValueError("Permission denied.")
        if not verify_name and not verify_name.lower() == str(category).lower():
            raise ValueError("Confirmation value must match Category name!")
        entities = {'enactor': enactor, 'target': category}
        cmsg.Delete(entities).send()
        category.delete()

    def lock_category(self, session, name, lock_data):
        category = self.find_category(session, name)
        return category.lock(session, lock_data)

    def config_category(self, session, name, config_op, config_val):
        category = self.find_category(session, name)
        return category.config(session, config_op, config_val)

    def create_channel(self, session, category, name):
        category = self.find_category(session, category)
        return category.create_channel(session, name)

    def rename_channel(self, session, category, name, new_name):
        category = self.find_category(session, category)
        return category.rename_channel(session, name, new_name)

    def delete_channel(self, session, category, name, verify_name):
        category = self.find_category(session, category)
        return category.delete_channel(session, name, verify_name)

    def lock_channel(self, session, category, name, lock_data):
        category = self.find_category(session, category)
        return category.lock_channel(session, name, lock_data)

    def config_channel(self, session, category, name, config_op, config_val):
        category = self.find_category(session, category)
        return category.config_channel(session, name, config_op, config_val)

    def grant_category(self, session, category, position, user):
        category = self.find_category(session, category)
        return category.grant_category(session, position, user)

    def grant_channel(self, session, category, name, position, user):
        category = self.find_category(session, category)
        return category.grant_channel(session, name, position, user)

    def revoke_category(self, session, category, position, user):
        category = self.find_category(session, category)
        return category.revoke_category(session, position, user)

    def revoke_channel(self, session, category, name, position, user):
        category = self.find_category(session, category)
        return category.revoke_channel(session, name, position, user)

    def ban_category(self, session, category, user, duration):
        category = self.find_category(session, category)
        return category.ban_category(session, user, duration)

    def ban_channel(self, session, category, name, user, duration):
        category = self.find_category(session, category)
        return category.ban_channel(session, name, user, duration)

    def unban_category(self, session, category, user):
        category = self.find_category(session, category)
        return category.unban_category(session, user)

    def unban_channel(self, session, category, name, user):
        category = self.find_category(session, category)
        return category.unban_channel(session, name, user)

    def who_channel(self, session, category, name):
        category = self.find_category(session, category)
        return category.who_channel(session, name)

    def examine_category(self, session, category):
        category = self.find_category(session, category)
        return category.examine_category(session)

    def examine_channel(self, session, category, name):
        category = self.find_category(session, category)
        return category.examine_channel(session, name)