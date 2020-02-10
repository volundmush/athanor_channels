from athanor_channels.channels.base import AbstractChannel, AbstractChannelCategory, AbstractChannelSystem
import athanor


class HasCharacterUser(object):

    def find_user(self, session, user):
        return athanor.CONTROLLER_MANAGER.get('character').find_character(user)

    def get_enactor(self, session):
        return session.get_puppet()


class CharacterChannel(HasCharacterUser, AbstractChannel):

    def get_sender(self, sending_session=None):
        if not sending_session:
            return None
        return sending_session.get_puppet()

    @property
    def subscriptions(self):
        return self.object_subscriptions


class CharacterChannelCategory(HasCharacterUser, AbstractChannelCategory):
    pass


class CharacterChannelSystem(HasCharacterUser, AbstractChannelSystem):
    pass
