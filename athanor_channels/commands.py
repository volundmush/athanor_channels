from evennia import GLOBAL_SCRIPTS

from evennia.comms.channelhandler import ChannelCommand
from athanor.commands.command import AthanorCommand


class HasChannelSystem(object):

    def at_pre_cmd(self):
        self.chan_sys = GLOBAL_SCRIPTS.channel.find_system(self.system_key)

    def target_channel(self, path):
        err = "Must target a channel! Format: / for System, <name> for Category, <Category>/<name> for Channel"
        if not path:
            raise ValueError(err)
        if path == '/':
            return (self.chan_sys)
        if '/' not in path:
            return (self.chan_sys, self.chan_sys.find_category(self.session, path))
        else:
            path = path.split('/', 1)
            category = self.chan_sys.find_category(self.session, path[0])
            channel = category.find_channel(self.session, path[1])
            return (self.chan_sys, category, channel)


class HasDisplayList(HasChannelSystem):

    def display_channel_list(self):
        pass

    def display_channel_info(self):
        pass

    def switch_main(self):
        if not self.args:
            return self.display_channel_list()
        return self.display_channel_info()


class AbstractChannelCommand(HasChannelSystem, ChannelCommand):
    pass


class AccountChannelCommand(AbstractChannelCommand):
    system_key = 'account'
    account_caller = True


class ObjectChannelCommand(AbstractChannelCommand):
    system_key = 'object'


class AbstractChannelAdminCommand(HasDisplayList, AthanorCommand):
    """

    """
    switch_options = ('create', 'rename', 'lock', 'config', 'grant', 'revoke', 'ban')

    def switch_create(self):
        err = f"Usage: {self.key}/create <CategoryName> OR {self.key}/create <Category>/<ChannelName>"
        if not self.args:
            raise ValueError(err)
        if self.args == '/':
            raise ValueError(err)
        if '/' in self.args:
            cat_path, chan_name = self.args.split('/', 1)
            if not cat_path or not chan_name:
                raise ValueError(err)
            category = self.chan_sys.find_category(self.session, cat_path)
            GLOBAL_SCRIPTS.channel.create_channel(self.session, self.chan_sys, category, chan_name)
        else:
            GLOBAL_SCRIPTS.channel.create_category(self.session, self.chan_sys, self.args)

    def switch_rename(self):
        err = f"Usage: {self.key}/rename <Category>[/<channel>]=<new name>"
        target = self.target_channel(self.lhs)
        if len(target) == 1:
            raise ValueError(err)
        if len(target) == 2:
            GLOBAL_SCRIPTS.channel.rename_category(self.session, target[0], target[1], self.rhs)
        if len(target) == 3:
            GLOBAL_SCRIPTS.channel.rename_channel(self.session, target[0], target[1], target[2], self.rhs)

    def switch_lock(self):
        cmd = f"{self.key}/lock"
        err = f"Usage: {cmd} /=<lockstring>, or {cmd} <Category>[/<channel>]=<lockstring>"
        target = self.target_channel(self.lhs)
        if not self.rhs:
            raise ValueError(err)
        if len(target) == 1:
            GLOBAL_SCRIPTS.channel.lock_system(self.session, target[0], self.rhs)
        if len(target) == 2:
            GLOBAL_SCRIPTS.channel.lock_category(self.session, target[0], target[1], self.rhs)
        if len(target) == 3:
            GLOBAL_SCRIPTS.channel.lock_channel(self.session, target[0], target[1], target[2], self.rhs)

    def switch_config(self):
        cmd = f"{self.key}/config"
        err = f"Usage: {cmd} /=<op>,<val> or {cmd} <Category>[/<channel>]=<op>,<val>"
        target = self.target_channel(self.lhs)
        if not self.rhs or not len(self.rhslist) == 2:
            raise ValueError(err)
        if len(target) == 1:
            GLOBAL_SCRIPTS.channel.config_system(self.session, target[0], *self.rhslist)
        if len(target) == 2:
            GLOBAL_SCRIPTS.channel.config_category(self.session, target[0], target[1], *self.rhslist)
        if len(target) == 3:
            GLOBAL_SCRIPTS.channel.config_channel(self.session, target[0], target[1], target[2], *self.rhslist)

    def user_parselist(self, users):
        return [self.user_parse(user) for user in users]

    def switch_grant(self):
        cmd = f"{self.key}/grant"
        err = f"Usage: {cmd} /=<position>,<user1>[,<user2>,<user3>...]"
        target = self.target_channel(self.lhs)
        if not len(self.rhslist) > 2:
            raise ValueError(err)
        subjects = self.user_parselist(self.rhslist)
        if len(target) == 1:
            GLOBAL_SCRIPTS.channel.grant_system(self.session, target[0], subjects)
        if len(target) == 2:
            GLOBAL_SCRIPTS.channel.grant_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            GLOBAL_SCRIPTS.channel.grant_channel(self.session, target[0], target[1], target[2], subjects)

    def switch_revoke(self):
        cmd = f"{self.key}/revoke"
        err = f"Usage: {cmd} /=<position>,<user1>[,<user2>,<user3>...]"
        target = self.target_channel(self.lhs)
        if not len(self.rhslist) > 2:
            raise ValueError(err)
        subjects = self.user_parselist(self.rhslist)
        if len(target) == 1:
            GLOBAL_SCRIPTS.channel.revoke_system(self.session, target[0], subjects)
        if len(target) == 2:
            GLOBAL_SCRIPTS.channel.revoke_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            GLOBAL_SCRIPTS.channel.revoke_channel(self.session, target[0], target[1], target[2], subjects)

    def switch_ban(self):
        cmd = f"{self.key}/ban"
        err = f"Usage: {cmd} /=<target>,<duration1>"
        target = self.target_channel(self.lhs)
        if not len(self.rhslist) > 2:
            raise ValueError(err)
        subjects = self.user_parselist(self.rhslist)
        if len(target) == 1:
            GLOBAL_SCRIPTS.channel.ban_system(self.session, target[0], subjects)
        if len(target) == 2:
            GLOBAL_SCRIPTS.channel.ban_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            GLOBAL_SCRIPTS.channel.ban_channel(self.session, target[0], target[1], target[2], subjects)


class CmdAccountChannelAdmin(AbstractChannelAdminCommand):
    account_caller = True
    system_key = 'account'
    key = '@achanadm'

    def user_parse(self, user):
        system = GLOBAL_SCRIPTS.account
        return system.find_account(user)


class CmdObjectChannelAdmin(AbstractChannelAdminCommand):
    account_caller = False
    system_key = 'object'
    key = '@chanadm'

    def user_parse(self, user):
        system = GLOBAL_SCRIPTS.character
        return system.find_character(user)
