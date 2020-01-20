from django.db.models import Q
from athanor.cmdsets.base import AthanorCmdSet


class AbstractChannelHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self._cached = False
        self._cached_cmdsets = dict()
        self.update_cache()

    def update_cache(self):
        cmdsets = dict()
        for subscription in self.subscriptions.all():
            system = subscription.db_channel.system
            if system not in cmdsets:
                cmdsets[system] = AthanorCmdSet()
            cmd = system.ndb.command_class(
                key=subscription.db_name,
                locks="cmd:all()%s" % subscription.db_channel.locks,
                subscription=subscription
            )
            cmdsets[system].add(cmd)
            self.check_listen(subscription.db_channel)
        self._cached_cmdsets = cmdsets
        self._cached = True

    def cmdsets(self):
        if not self._cached:
            self.update_cache()
        return list(self._cached_cmdsets.values())

    @property
    def subscriptions(self):
        return self.owner.channel_subscriptions

    def add(self, channel, alias):
        if (found := self.subscriptions.filter(db_namespace=self.namespace, db_name=alias).first()):
            raise ValueError(f"That conflicts with an existing alias to {found.db_channel}!")
        self.subscriptions.create(db_namespace=self.namespace, db_channel=channel, db_name=alias)
        self.update_cache()

    def find_alias(self, alias):
        if not (found := self.subscriptions.filter(db_namespace=self.namespace, db_name=alias).first()):
            raise ValueError(f"Channel Alias not found: {alias}!")
        return found

    def leave(self, alias):
        found = self.find_alias(alias)
        found.delete()
        self.update_cache()

    def codename(self, alias, codename):
        found = self.find_alias(alias)

    def title(self, alias, title):
        found = self.find_alias(alias)

    def altname(self, alias, altname):
        found = self.find_alias(alias)

    def check_listen(self, channel):
        all_aliases = self.subscriptions.filter(db_channel=channel)
        listening = True if self.owner in channel.listeners else False
        # If listening and shouldn't be...
        if listening:
            if not all_aliases.filter(Q(db_muted=False) | Q(db_enabled=True)).count():
                channel.remove_listener(self.owner)
        else:
            if all_aliases.filter(Q(db_muted=False) | Q(db_enabled=True)).count():
                channel.add_listener(self.owner)

    def mute(self, alias):
        found = self.find_alias(alias)
        found.muted = True
        self.check_listen(found.db_channel)

    def unmute(self, alias):
        found = self.find_alias(alias)
        found.muted = False
        self.check_listen(found.db_channel)

    def on(self, alias):
        found = self.find_alias(alias)
        found.enabled = True
        self.check_listen(found.db_channel)

    def off(self, alias):
        found = self.find_alias(alias)
        found.enabled = False
        self.check_listen(found.db_channel)


class AccountChannelHandler(AbstractChannelHandler):
    namespace = 'account'


class ObjectChannelHandler(AbstractChannelHandler):
    namespace = 'object'

    def cmdsets(self):
        cmdset_list = super().cmdsets()
        if self.owner.account:
            cmdset_list.extend(self.owner.account.channels.cmdsets())
        return cmdset_list


class GlobalChannelHandler(object):

    def add(self, channel):
        pass

    def clear(self):
        pass

    def remove(self, channel):
        pass

    def update(self):
        pass

    def get_cmdset(self, source_object):
        return source_object.channels.cmdsets()
