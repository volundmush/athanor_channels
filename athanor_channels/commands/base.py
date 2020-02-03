import re

from evennia.utils.utils import lazy_property

from athanor.commands.command import AthanorCommand
from athanor.utils.text import Speech


class HasChannelSystem(AthanorCommand):
    lhs_delim = '/'

    def at_pre_cmd(self):
        self.chan_sys = self.controllers.get('channel').find_system(self.system_key)

    def target_channel(self, path, pathlist):
        err = "Must target a channel! Format: / for System, <name> for Category, <Category>/<name> for Channel"
        if not path:
            raise ValueError(err)
        if path == '/':
            return (self.chan_sys)
        if '/' not in path:
            return (self.chan_sys, self.chan_sys.find_category(self.session, path))
        else:
            path = pathlist
            if len(path) > 2:
                raise ValueError(err)
            category = self.chan_sys.find_category(self.session, pathlist[0])
            channel = category.find_channel(self.session, pathlist[1])
            return (self.chan_sys, category, channel)


class HasDisplayList(HasChannelSystem):

    def display_channel_list(self):
        if not (categories := self.chan_sys.visible_categories(self.session)):
            raise ValueError("No categories to display!")
        styling = self.caller.styler
        message = list()
        message.append(styling.styled_header(f"{self.chan_sys} Channel Categories"))
        for category in categories:
            message.append(self.styled_separator(f"{category} Channels"))
            for channel in category.visible_channels(self.session):
                message.append(str(channel))
        message.append(styling.blank_footer)
        self.msg("\n".join(str(l) for l in message))

    def display_channel_info(self):
        self.msg(self.args)
        print(self.args)

    def switch_main(self):
        if not self.args:
            return self.display_channel_list()
        return self.display_channel_info()

_CHANNEL_DOC = """
This command was created as an alias to a {system_key} Channel.

Usage:
    {key} <text>
        Send text to a channel.
    
    {key}/who
        Display other users on the channel.
    
    {key}/leave
        Leave the channel. This command will be removed.
    
    {key}/title <title>
        Set a title-prefix that will appear before your names.
    
    {key}/altname <alternate name>
        Change the name you see this channel's messages under.
    
    {key}/off
        Stop receiving messages until you /on. Clears on a logoff/login.
    
    {key}/codename <code name>
        An alternate name you will appear as, on supported channels.

    Set /title, /altname, or /codename to None to clear them.
"""


class AbstractChannelCommand(HasChannelSystem, AthanorCommand):
    switch_options = ('who', 'leave', 'title', 'altname', 'mute', 'unmute', 'codename', 'on', 'off')
    controller = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doc__ = _CHANNEL_DOC.format(key=self.key, system_key=self.system_key)

    def switch_main(self):
        subscrip = self.subscription
        channel = subscrip.db_channel
        alternate_name = None
        if subscrip.db_ccodename:
            alternate_name = subscrip.db_ccodename
        speech_obj = Speech(speaker=self.caller, speech_text=self.args, mode="channel", title=subscrip.db_title,
                            alternate_name=alternate_name, controller=self.controller)
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


_ADMIN_DOC = """
This command is for administrating the {system_key} Channel System.

Note: For below, <target> is either a <category> or a <category>/<channel>

Usage:
    {key}
        List all channels in the System by Category.
    
    {key}/create <target>[=<description>]
        Creates a Category or a Channel in a Category. Optionally gives it a
        description.
    
    {key}/rename <target>[=<new name>]
        Renames the targeted category[/channel]. and optionally sets a
        description.
    
    {key}/lock <target>=<lock string>
        Sets an Evennia lock string to the category[/channel].
        Please don't screw with this if you don't know what you're doing.
    
    {key}/grant <target>=<position>,<user1>[,<user2>,<user3>,<user4>,...]
        Grants one or more users <position> over target.
        <position> can be moderator or operator. Explained further down.
        if <target> is /, it grants the position to all categories.
        Use {key}/revoke with the same syntax to revoke positions.
    
    {key}/ban <target>=<user>,<duration>
        Prevent a specific person from using this channel.
        <duration> must be a simple string such as 7d (7 days) or 5h.
        Use {key}/unban <target>=<user> to rescind a ban early.

Concepts:
    Moderators: Moderators can use disciplinary commands on users.
    Operators: Operators can alter configurations and create/delete 
        resources such as channels.
        Operators also possess all Moderator powers.
    Hierarchy: The Channel System is arranged as 
        System -> Category -> Channel.
        If you are a <position> in a parent entity, you inherit this 
        position on all child entities. IE: If you have Operator status
        on a Category, you have power over all channels in that category.
"""


_TARGET = "<category>[/<channel>] OR /"


class AbstractChannelAdminCommand(HasDisplayList):
    switch_options = ('create', 'rename', 'lock', 'config', 'grant', 'revoke', 'ban')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doc__ = _ADMIN_DOC.format(system_key=self.system_key, key=self.key)

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
        cmd = f"{self.key}/rename"
        err = f"Usage: {cmd} {_TARGET}=<new name>"
        target = self.target_channel(self.lhs, self.lhslist)
        if len(target) == 1:
            raise ValueError(err)
        if len(target) == 2:
            self.controllers.get('channel').rename_category(self.session, target[0], target[1], self.rhs)
        if len(target) == 3:
            self.controllers.get('channel').rename_channel(self.session, target[0], target[1], target[2], self.rhs)

    def switch_lock(self):
        cmd = f"{self.key}/lock"
        err = f"Usage: {cmd} {_TARGET}=<lockstring>"
        target = self.target_channel(self.lhs, self.lhslist)
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
        err = f"Usage: {cmd} {_TARGET}=<op>,<val>"
        target = self.target_channel(self.lhs, self.lhslist)
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
        err = f"Usage: {cmd} {_TARGET}=<position>,<user1>[,<user2>,<user3>...]"
        target = self.target_channel(self.lhs, self.lhslist)
        if not len(self.rhslist) > 1:
            raise ValueError(err)
        subjects = self.user_parselist(self.rhslist[1:])
        if len(target) == 1:
            self.controllers.get('channel').grant_system(self.session, target[0], subjects)
        if len(target) == 2:
            self.controllers.get('channel').grant_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            self.controllers.get('channel').grant_channel(self.session, target[0], target[1], target[2], subjects)

    def switch_revoke(self):
        cmd = f"{self.key}/revoke"
        err = f"Usage: {cmd} {_TARGET}=<position>,<user1>[,<user2>,<user3>...]"
        target = self.target_channel(self.lhs, self.lhslist)
        if not len(self.rhslist) > 2:
            raise ValueError(err)
        subjects = self.user_parselist(self.rhslist[1:])
        if len(target) == 1:
            self.controllers.get('channel').revoke_system(self.session, target[0], subjects)
        if len(target) == 2:
            self.controllers.get('channel').revoke_category(self.session, target[0], target[1], subjects)
        if len(target) == 3:
            self.controllers.get('channel').revoke_channel(self.session, target[0], target[1], target[2], subjects)

    def switch_ban(self):
        cmd = f"{self.key}/ban"
        err = f"Usage: {cmd} {_TARGET}=<user>,<duration1>"
        target = self.target_channel(self.lhs, self.lhslist)
        if len(target) == 1:
            self.controllers.get('channel').ban_system(self.session, target[0], self.rhs)
        if len(target) == 2:
            self.controllers.get('channel').ban_category(self.session, target[0], target[1], self.rhs)
        if len(target) == 3:
            self.controllers.get('channel').ban_channel(self.session, target[0], target[1], target[2], self.rhs)

    def switch_unban(self):
        cmd = f"{self.key}/ban"
        err = f"Usage: {cmd} {_TARGET}>=<user>"
        target = self.target_channel(self.lhs, self.lhslist)
        subjects = self.user_parselist(self.rhslist)
        if len(target) == 1:
            self.controllers.get('channel').unban_system(self.session, target[0], self.rhs)
        if len(target) == 2:
            self.controllers.get('channel').unban_category(self.session, target[0], target[1], self.rhs)
        if len(target) == 3:
            self.controllers.get('channel').unban_channel(self.session, target[0], target[1], target[2], self.rhs)


_USE_COMMAND = """
Command used to manage subscriptions to {system_key} channels.

Usage:
    {key}
        List all available channels.
    
    {key}/join <category>/<channel>=<alias>
        Creates an alias to a channel. This creates a new 'command' for you.
        The alias can be used to then talk on the channel.
        Example: {key}/join Public/General=g
        Then talk on it using: g Blahblah...
    
    {key}/who <category>/<channel>
        Shows the users on a channel.
        
    {key}/info <category>/<channel>
        Shows various information about a channel.
"""


class AbstractChannelUseCommand(HasDisplayList):
    switch_options = ('join', 'who', 'info')
    re_alias = re.compile(r"(?i)^([^\/\s])+$")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doc__ = _USE_COMMAND.format(key=self.key, system_key=self.system_key)

    def switch_join(self):
        target = self.target_channel(self.lhs, self.lhslist)
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





