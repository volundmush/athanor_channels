from athanor_channels.commands.base import AbstractChannelAdminCommand, AbstractChannelCommand, AbstractChannelUseCommand


class AccountChannelCommand(AbstractChannelCommand):
    system_key = 'account'
    account_caller = True
    help_category = "Account Channel Aliases"
    user_controller = 'account'


class CmdAccountChannelAdmin(AbstractChannelAdminCommand):
    account_caller = True
    system_key = 'account'
    key = '@achanadm'

    def user_parse(self, user):
        system = self.controllers.get('account')
        return system.find_account(user)


class CmdAccountChannelUse(AbstractChannelUseCommand):
    account_caller = True
    system_key = 'account'
    key = '@achannel'
