from collections import defaultdict
from athanor.cmdsets.base import AthanorCmdSet


class AbstractChannelHandler(object):

    def __init__(self, owner):
        self.owner = owner
        self._cached = False
        self._cached_cmdsets = dict()
        self.update_cache()

    def update_cache(self):
        cmdsets = dict()
        for subscription in self.subscriptions():
            system = subscription.db_channel.system
            if system not in cmdsets:
                cmdsets[system] = AthanorCmdSet()
            cmd = system.ndb.command_class(
                key=subscription.db_name,
                locks="cmd:all()%s" % subscription.db_channel.locks,
                subscription=subscription
            )
            cmdsets[system].add(cmd)
        self._cached_cmdsets = cmdsets
        self._cached = True

    def cmdsets(self):
        if not self._cached:
            self.update_cache()
        return list(self._cached_cmdsets.values())

    def subscriptions(self):
        return self.owner.channel_subscriptions.all()


class AccountChannelHandler(AbstractChannelHandler):
    pass


class ObjectChannelHandler(AbstractChannelHandler):

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
