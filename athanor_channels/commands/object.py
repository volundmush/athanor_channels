from athanor_channels.commands.base import AbstractChannelAdminCommand, AbstractChannelCommand, AbstractChannelUseCommand


class ObjectChannelCommand(AbstractChannelCommand):
    system_key = 'object'


class CmdObjectChannelAdmin(AbstractChannelAdminCommand):
    account_caller = False
    system_key = 'object'
    key = '@chanadm'

    def user_parse(self, user):
        system = self.controllers.get('character')
        return system.find_character(user)


class CmdObjectChannelUse(AbstractChannelUseCommand):
    account_caller = False
    system_key = 'object'
    key = '@channel'
