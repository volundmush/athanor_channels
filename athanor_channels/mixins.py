from athanor_channels.channelhandler import AccountChannelHandler, CharacterChannelHandler
from evennia.utils.utils import lazy_property


class AccountChannelMixin(object):

    @lazy_property
    def channels(self):
        return AccountChannelHandler(self)


class CharacterChannelMixin(object):

    @lazy_property
    def channels(self):
        return CharacterChannelHandler(self)
