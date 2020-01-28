from athanor_channels.channels.base import AbstractChannel, AbstractChannelCategory, AbstractChannelSystem

class AthanorObjectChannel(AbstractChannel):

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_puppet()

    @property
    def subscriptions(self):
        return self.object_subscriptions


class ObjectChannelCategory(AbstractChannelCategory):
    pass


class ObjectChannelSystem(AbstractChannelSystem):
    pass
