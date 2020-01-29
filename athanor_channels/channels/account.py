from athanor_channels.channels.base import AbstractChannel, AbstractChannelCategory, AbstractChannelSystem


class AccountChannel(AbstractChannel):

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_account()

    @property
    def subscriptions(self):
        return self.account_subscriptions


class AccountChannelCategory(AbstractChannelCategory):
    pass


class AccountChannelSystem(AbstractChannelSystem):
    pass