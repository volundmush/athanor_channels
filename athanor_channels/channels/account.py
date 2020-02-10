from athanor_channels.channels.base import AbstractChannel, AbstractChannelCategory, AbstractChannelSystem
import athanor


class HasAccountUser(object):

    def find_user(self, session, user):
        return athanor.CONTROLLER_MANAGER.get('account').find_account(user)

    def get_enactor(self, session):
        return session.get_account()


class AccountChannel(HasAccountUser, AbstractChannel):

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_account()

    @property
    def subscriptions(self):
        return self.account_subscriptions


class AccountChannelCategory(HasAccountUser, AbstractChannelCategory):
    pass


class AccountChannelSystem(HasAccountUser, AbstractChannelSystem):
    pass
