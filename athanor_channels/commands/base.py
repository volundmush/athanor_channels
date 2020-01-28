import re


from athanor.commands.command import AthanorCommand
from athanor.utils.text import Speech


class HasChannelSystem(AthanorCommand):

    def at_pre_cmd(self):
        self.chan_sys = self.controllers.get('channel').find_system(self.system_key)

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
        if not (categories := self.chan_sys.visible_categories(self.session)):
            raise ValueError("No categories to display!")
        message = list()
        message.append(self.styled_header(f"{self.chan_sys} Channel Categories"))
        for category in categories:
            message.append(self.styled_separator(f"{category} Channels"))
            for channel in category.visible_channels(self.session):
                message.append(str(channel))
        message.append(self._blank_footer)
        self.msg("\n".join(str(l) for l in message))

    def display_channel_info(self):
        pass

    def switch_main(self):
        if not self.args:
            return self.display_channel_list()
        return self.display_channel_info()


class AbstractChannelCommand(HasChannelSystem, AthanorCommand):
    switch_options = ('who', 'leave', 'title', 'altname', 'mute', 'unmute', 'on', 'off')

    def switch_main(self):
        subscrip = self.subscription
        channel = subscrip.db_channel
        speech_obj = Speech(speaker=self.caller, speech_text=self.args, mode="channel", title=subscrip.db_title,
                            alternate_name=subscrip.db_altname, name_dict=channel.name_map)
        channel.broadcast(speech_obj, self.session)

    def switch_leave(self):
        self.caller.channels.remove(self.subscription)

    def switch_codename(self):
        self.caller.channels.codename(self.subscription, self.args)

    def switch_title(self):
        self.caller.channels.title(self.subscription, self.args)

    def switch_altname(self):
        self.caller.channels.altname(self.subscription, self.args)

    def switch_mute(self):
        self.caller.channels.mute(self.subscription)

    def switch_unmute(self):
        self.caller.channels.unmute(self.subscription)

    def switch_on(self):
        self.caller.channels.on(self.subscription)

    def switch_off(self):
        self.caller.channels.off(self.subscription)

    def switch_who(self):
        self.caller.channels.who(self.subscription)


class AbstractChannelAdminCommand(HasDisplayList):
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
            self.controllers.get('channel').create_channel(self.session, self.chan_sys, category, chan_name)
        else:
            self.controllers.get('channel').create_category(self.session, self.chan_sys, self.args)

    def switch_rename(self):
        err = f"Usage: {self.key}/rename <Category>[/<channel>]=<new name>"
        target = self.target_channel(self.lhs)
        if len(target) == 1:
            raise ValueError(err)
        if len(target) == 2:
            self.controllers.get('channel').rename_category(self.session, target[0], target[1], self.rhs)
        if len(target) == 3:
            self.controllers.get('channel').rename_channel(self.session, target[0], target[1], target[2], self.rhs)

    def switch_lock(self):
        cmd = f"{self.key}/lock"
        err = f"Usage: {cmd} /=<lockstring>, or {cmd} <Category>[/<channel>]=<lockstring>"
        target = self.target_channel(self.lhs)
        if not self.rhs:
            raise ValueError(err)
        if len(target) == 1:
            self.controllers.get('channel').lock_system(self.session, target[0], self.rhs)
        if len(target) == 2:
            self.controllers.get('channel').lock_category(self.session, target[0], target[1], self.rhs)
        if len(target) == 3:
            self.controllers.get('channel').lock_channel(self.session, target[0], target[1], target[2], self.rhs)

    def switch_config(self):
        cmd = f"{self.key}/config"
        err = f"Usage: {cmd} /=<op>,<val> or {cmd} <Category>[/<channel>]=<op>,<val>"
        target = self.target_channel(self.lhs)
        if not self.rhs or not len(self.rhslist) == 2:
            raise ValueError(err)
        if len(target) == 1:
            self.controllers.get('channel').config_system(self.session, target[0], *self.rhslist)
        if len(target) == 2:
            self.controllers.get('channel').config_category(self.session, target[0], target[1], *self.rhslist)
        if len(target) == 3:
            self.controllers.get('channel').config_channel(self.session, target[0], target[1], target[2], *self.rhslist)

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
            self.controllers.get('channel').grant_system(self.session, target[0], subjects)
        if len(target) == 2:
            self.controllers.get('channel').grant_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            self.controllers.get('channel').grant_channel(self.session, target[0], target[1], target[2], subjects)

    def switch_revoke(self):
        cmd = f"{self.key}/revoke"
        err = f"Usage: {cmd} /=<position>,<user1>[,<user2>,<user3>...]"
        target = self.target_channel(self.lhs)
        if not len(self.rhslist) > 2:
            raise ValueError(err)
        subjects = self.user_parselist(self.rhslist)
        if len(target) == 1:
            self.controllers.get('channel').revoke_system(self.session, target[0], subjects)
        if len(target) == 2:
            self.controllers.get('channel').revoke_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            self.controllers.get('channel').revoke_channel(self.session, target[0], target[1], target[2], subjects)

    def switch_ban(self):
        cmd = f"{self.key}/ban"
        err = f"Usage: {cmd} /=<target>,<duration1>"
        target = self.target_channel(self.lhs)
        if not len(self.rhslist) > 2:
            raise ValueError(err)
        subjects = self.user_parselist(self.rhslist)
        if len(target) == 1:
            self.controllers.get('channel').ban_system(self.session, target[0], subjects)
        if len(target) == 2:
            self.controllers.get('channel').ban_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            self.controllers.get('channel').ban_channel(self.session, target[0], target[1], target[2], subjects)


class AbstractChannelUseCommand(HasDisplayList):
    switch_options = ('join', 'leave', 'title', 'altname', 'mute', 'unmute', 'on', 'off')
    re_alias = re.compile(r"(?i)^([^\/\s])+$")

    def switch_join(self):
        target = self.target_channel(self.lhs)
        err = f"Usage: {self.key}/join <Category>/<Channel>=<alias> - Aliases must be simple, disallowing whitespace or /"
        if not len(target) == 3:
            raise ValueError(err)
        if not self.re_alias.match(self.rhs):
            raise ValueError(err)
        self.caller.channels.add(target[2], self.rhs)

    def switch_leave(self):
        self.caller.channels.remove(self.args)

    def switch_codename(self):
        self.caller.channels.codename(self.lhs, self.rhs)

    def switch_title(self):
        self.caller.channels.title(self.lhs, self.rhs)

    def switch_altname(self):
        self.caller.channels.altname(self.lhs, self.rhs)

    def switch_mute(self):
        self.caller.channels.mute(self.args)

    def switch_unmute(self):
        self.caller.channels.unmute(self.args)

    def switch_on(self):
        self.caller.channels.on(self.args)

    def switch_off(self):
        self.caller.channels.off(self.args)





