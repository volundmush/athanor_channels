from athanor_channels.channelhandler import AccountChannelHandler, ObjectChannelHandler
from evennia.utils.utils import lazy_property


class AccountChannelMixin(object):

    @lazy_property
    def channels(self):
        return AccountChannelHandler(self)


class ObjectChannelMixin(object):

    @lazy_property
    def channels(self):
        return ObjectChannelHandler(self)
