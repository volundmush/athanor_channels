from athanor_channels.commands.base import AbstractChannelAdminCommand, AbstractChannelCommand, AbstractChannelUseCommand


class CharacterChannelCommand(AbstractChannelCommand):
    system_key = 'character'
    help_category = "Character Channel Aliases"
    user_controller = 'character'


class CmdCharacterChannelAdmin(AbstractChannelAdminCommand):
    account_caller = False
    system_key = 'object'
    key = '@chanadm'

    def user_parse(self, user):
        system = self.controllers.get('character')
        return system.find_character(user)


class CmdCharacterChannelUse(AbstractChannelUseCommand):
    account_caller = False
    system_key = 'character'
    key = '@channel'
