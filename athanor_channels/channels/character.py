from athanor_channels.channels.base import AbstractChannel, AbstractChannelCategory, AbstractChannelSystem


class CharacterChannel(AbstractChannel):

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_puppet()

    @property
    def subscriptions(self):
        return self.object_subscriptions


class CharacterChannelCategory(AbstractChannelCategory):
    pass


class CharacterChannelSystem(AbstractChannelSystem):
    pass
