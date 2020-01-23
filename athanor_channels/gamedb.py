import re
from evennia.comms.comms import DefaultChannel
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import lazy_property
from evennia.utils.utils import class_from_module
from evennia.utils.logger import log_trace

from athanor.gamedb.scripts import AthanorOptionScript
from athanor.utils.text import partial_match

from athanor_channels.models import ChannelSystemBridge, ChannelCategoryBridge, ChannelBridge
from athanor_channels.commands import AccountChannelCommand


class HasChanOps(object):
    """
    Limited Mixin for providing some permissions storage to the Channel System.
    """

    def get_set_attribute(self, attrname):
        if not self.attributes.has(key=attrname):
            self.attributes.add(key=attrname, value=set())
        return self.attributes.get(key=attrname)

    @lazy_property
    def operators(self):
        return self.get_set_attribute('operators')

    @lazy_property
    def moderators(self):
        return self.get_set_attribute('moderators')


class AthanorChannel(DefaultChannel, HasChanOps):
    """
    Abstract class for Account and Object channels. Don't use this directly!
    """
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    @property
    def bridge(self):
        return self.channel_bridge

    @property
    def category(self):
        return self.bridge.db_category.db_script

    @property
    def system(self):
        return self.bridge.db_category.db_system.db_script

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

    def rename(self, new_name):
        pass

    def is_operator(self, session):
        enactor = session.get_puppet_or_account()
        return enactor in self.operators or self.access(session, 'control') or self.category.is_operator(session)

    def is_moderator(self, session):
        enactor = session.get_puppet_or_account()
        return enactor in self.moderators or self.access(session, 'moderate') or self.category.is_moderator(session)

    def __str__(self):
        return str(self.key)

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_puppet_or_account()

    def render_prefix(self, recipient, sender):
        return f"<{self.key}>"

    def broadcast(self, text, sending_session=None):
        sender = self.get_sender(sending_session)
        for listener in self.listeners:
            prefix = self.render_prefix(listener, sender)
            listener.msg(f"{prefix} {text.render(viewer=listener)}")


class AthanorAccountChannel(AthanorChannel):

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_account()

    @property
    def subscriptions(self):
        return self.account_subscriptions


class AthanorObjectChannel(AthanorChannel):

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_puppet()

    @property
    def subscriptions(self):
        return self.object_subscriptions


class AbstractChannelCategory(AthanorOptionScript, HasChanOps):
    re_name = re.compile(r"(?i)^([A-Z]|[0-9]|\.|-|')+( ([A-Z]|[0-9]|\.|-|')+)*$")

    def __str__(self):
        return str(self.key)

    @property
    def bridge(self):
        return self.channel_category_bridge

    @property
    def system(self):
        return self.bridge.db_system.db_script

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

    def rename(self, new_name):
        pass

    def channels(self):
        return [c.db_channel for c in self.bridge.channels.all()]

    def visible_channels(self, session):
        return [channel for channel in self.channels() if channel.access(session, 'listen')]

    def find_channel(self, session, name):
        if isinstance(name, AthanorChannel):
            return name
        if isinstance(name, ChannelBridge):
            return name.db_channel
        if (found := partial_match(name, self.visible_channels(session))):
            return found
        raise ValueError(f"Cannot Find Channel: {name}")

    def is_operator(self, session):
        enactor = session.get_puppet_or_account()
        return enactor in self.operators or self.access(session, 'control') or self.system.is_operator(session)

    def is_moderator(self, session):
        enactor = session.get_puppet_or_account()
        return enactor in self.moderators or self.access(session, 'moderate') or self.system.is_moderator(session)

    def create_channel(self, session, name):
        if not self.is_operator(session):
            raise ValueError("Permission denied.")
        new_channel = self.system.ndb.channel_typeclass.create_channel(self, name)

    def rename_channel(self, session, name, new_name):
        channel = self.find_channel(session, name)
        if not self.is_operator(session):
            raise ValueError("Permission denied.")
        old_name = str(channel)
        changed_name = channel.rename(new_name)

    def delete_channel(self, session, name, verify_name):
        channel = self.find_channel(session, name)
        if not self.is_operator(session):
            raise ValueError("Permission denied.")
        if not verify_name and verify_name.lower() == str(channel).lower():
            raise ValueError("Verify value does not match channel name!")
        channel.delete()

    def lock_channel(self, session, name, lock_data):
        channel = self.find_channel(session, name)
        if not self.is_operator(session):
            raise ValueError("Permission denied.")
        channel.lock(session, lock_data)

    def config_channel(self, session, name, config_op, config_val):
        channel = self.find_channel(session, name)
        channel.config(session, config_op, config_val)

    def lock(self, session, lock_data):
        pass

    def config(self, session, config_op, config_val):
        pass


class AccountChannelCategory(AbstractChannelCategory):
    pass


class ObjectChannelCategory(AbstractChannelCategory):
    pass


class AbstractChannelSystem(AthanorOptionScript, HasChanOps):

    def __str__(self):
        return str(self.key)

    def at_start(self):
        if not hasattr(self, 'channel_system_bridge'):
            return
        bri = self.channel_system_bridge

        try:
            self.ndb.category_typeclass = class_from_module(bri.db_category_typeclass)

        except Exception:
            log_trace()
            self.ndb.category_typeclass = AccountChannelCategory

        try:
            self.ndb.channel_typeclass = class_from_module(bri.db_channel_typeclass)
        except Exception:
            log_trace()
            self.ndb.channel_typeclass = AthanorAccountChannel

        try:
            self.ndb.command_class = class_from_module(bri.db_command_class)
        except Exception:
            log_trace()
            self.ndb.command_class = AccountChannelCommand

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
        print(f"SESSION: {session}. NAME: {name}")
        print(f"VISIBLE CATEGORIES: {self.visible_categories(session)}")
        if (found := partial_match(name, self.visible_categories(session))):
            return found
        raise ValueError(f"Cannot find Channel Category: {name}")

    def is_operator(self, session):
        enactor = session.get_puppet_or_account()
        return enactor in self.operators or self.access(session, 'control')

    def is_moderator(self, session):
        enactor = session.get_puppet_or_account()
        return enactor in self.moderators or self.access(session, 'moderate')

    def create_category(self, session, name):
        if not self.access(session, 'control'):
            raise ValueError("Permission denied.")
        new_category = self.ndb.category_typeclass.create_channel_category(self, name)
        return new_category

    def rename_category(self, session, name, new_name):
        category = self.find_category(session, name)
        if not (category.access(session, 'control') or self.access(session, 'control')):
            raise ValueError("Permission denied.")
        old_name = str(category)
        changed_name = category.rename(new_name)
        return changed_name

    def delete_category(self, session, name, verify_name):
        category = self.find_category(session, name)
        if not (category.access(session, 'control') or self.access(session, 'control')):
            raise ValueError("Permission denied.")
        if not verify_name and not verify_name.lower() == str(category).lower():
            raise ValueError("Confirmation value must match Category name!")
        category.delete()

    def lock_category(self, session, name, lock_data):
        category = self.find_category(session, name)
        if not (category.access(session, 'control') or self.access(session, 'control')):
            raise ValueError("Permission denied.")
        category.lock(session, lock_data)

    def config_category(self, session, name, config_op, config_val):
        category = self.find_category(session, name)
        if not (category.access(session, 'control') or self.access(session, 'control')):
            raise ValueError("Permission denied.")
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


class AccountChannelSystem(AbstractChannelSystem):
    pass


class ObjectChannelSystem(AbstractChannelSystem):
    pass
