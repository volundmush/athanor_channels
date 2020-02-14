import re

from athanor.commands.command import AthanorCommand
from athanor.utils.text import Speech


class HasChannelSystem(AthanorCommand):
    lhs_delim = '/'
    controller_key = 'channel'
    entity_types = {
        1: 'system',
        2: 'category',
        3: 'channel'
    }

    def at_pre_cmd(self):
        self.chan_sys = self.controller.find_system(self.system_key)

    def target_channel(self, path):
        err = "Target Format: / for System, <name> for Category, <Category>/<name> for Channel"
        if not path:
            raise ValueError(err)
        if len(path) == 1:
            if path[0] == '/':
                return [self.chan_sys]
            else:
                return (self.chan_sys, self.chan_sys.find_category(self.session, path[0].strip()))
        else:
            if len(path) > 2:
                raise ValueError(err)
            return self.chan_sys.target_channel(self.session, path[0], path[1])

    def parse_targets(self, target):
        return self.target_channel(target)


class HasDisplayList(HasChannelSystem):

    def display_channel_info(self):
        self.msg(self.args)

    def switch_main(self):
        if not self.args:
            return self.msg(self.chan_sys.render_channel_list(self.session))
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
    controller_key = 'channel'
    user_controller = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doc__ = _CHANNEL_DOC.format(key=self.key, system_key=self.system_key)

    def switch_main(self):
        subscrip = self.subscription
        channel = subscrip.db_channel
        if not channel.is_position(self.caller, 'speaker'):
            raise ValueError("Permission denied.")
        alternate_name = None
        if subscrip.db_ccodename:
            alternate_name = subscrip.db_ccodename
        speech_obj = Speech(speaker=self.caller, speech_text=self.args, mode="channel", title=subscrip.db_title,
                            alternate_name=alternate_name, controller=self.user_controller)
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
    Some commands allow targeting all Categories ('System') via /

Usage:
    {key}
        List all channels in the System by Category.
    
    {key}/create <target>[=<description>]
        Creates a Category or a Channel in a Category. Optionally gives it a
        description.
    
    {key}/rename <target>[=<new name>]
        Renames the targeted category[/channel]. and optionally sets a
        description.
    
    {key}/describe <target>=<new description>
        Changes description for a category[/channel].
    
    {key}/lock <target>=<lock string>
        Sets an Evennia lock string to the category[/channel].
        Access types are 'listener', 'speaker', etc, listed below.
        Whoever passes these locks gains that Position without being
        explicitly granted it. Use with caution.
        
    {key}/grant <target>=<user>,<position>
        Grants a user <position> over target. Positions are explained below.
        Granting to System/Category cascades to Categories/Channels.
        Use {key}/revoke with the same syntax to revoke positions.
    
    {key}/ban <target>=<user>,<duration>
        Prevent a specific person from using this channel.
        <duration> must be a simple string such as 7d (7 days) or 5h.
        Banning from System/Category cascades to Categories/Channels.
        Use {key}/unban <target>=<user> to rescind a ban early.

Hierarchy: 
    The Channel System is arranged as System -> Category -> Channel.

Positions:
    The below are access tiers. higher tiers implicitly count
    as lower tiers. IE: An Operator is a Moderator, a Speaker is 
    a Listener.
    
    Listener: Listeners can join channels and hear messages.
    Speaker: Speakers can send messages over channels.
    Moderator: Moderators can use disciplinary commands on users.
    Operator: Operators can alter configurations and create/delete
        resources.

"""

_TARGET = "<category>[/<channel>]"


class AbstractChannelAdminCommand(HasDisplayList):
    switch_options = ('create', 'rename', 'lock', 'config', 'grant', 'revoke', 'ban', 'unban', 'describe')
    switch_syntax = {
        'create': f"{_TARGET}[=<description]",
        'rename': f"{_TARGET}=<new name>",
        'lock': f"{_TARGET}=<lockstring>",
        'config': f"{_TARGET}=<option>/<value>",
        'grant': f"{_TARGET}=<user>,<position>",
        'revoke': f"{_TARGET}=<user>,<position>",
        'ban': f"{_TARGET}=<user>,<duration>",
        'unban': f"{_TARGET}=<user>",
        'describe': f"{_TARGET}=<new description>"
    }
    lhs_delim = '/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doc__ = _ADMIN_DOC.format(system_key=self.system_key, key=self.key)

    def switch_create(self):
        if len(self.lhslist) == 1:
            result = self.controller.create_category(self.session, self.chan_sys, self.lhslist[0])
        elif len(self.lhslist) == 2:
            result = self.controller.create_channel(self.session, self.chan_sys, self.lhslist[0], self.lhslist[1])
        else:
            self.syntax_error()
        if self.rhs:
            result.describe(self.session, self.rhs)

    def _switch_basic(self, operation):
        target = self.target_channel(self.lhslist)
        if not (entity := self.entity_types.get(len(target), None)):
            self.syntax_error()
        op = getattr(self.controller, f"{operation}_{entity}")
        if not op:
            raise ValueError("Code error! Please contact staff!")
        return (target, op)

    def _switch_single(self, operation):
        target, op = self._switch_basic(operation)
        if len(target) == 1:
            return op(self.session, target[0], self.rhs)
        if len(target) == 2:
            return op(self.session, *target, self.rhs)
        if len(target) == 3:
            return op(self.session, *target, self.rhs)

    def _switch_multi(self, operation, multi_count):
        target, op = self._switch_basic(operation)
        if len(self.rhslist) != multi_count:
            self.syntax_error()
        if len(target) == 1:
            return op(self.session, target[0], *self.rhslist)
        if len(target) == 2:
            return op(self.session, *target, *self.rhslist)
        if len(target) == 3:
            return op(self.session, *target, *self.rhslist)

    def display_channel_info(self):
        self.msg(self._switch_single('examine'))

    def switch_describe(self):
        return self._switch_single('describe')

    def switch_grant(self):
        return self._switch_multi('grant', 2)

    def switch_revoke(self):
        return self._switch_multi('revoke', 2)

    def switch_ban(self):
        return self._switch_multi('ban', 2)

    def switch_unban(self):
        return self._switch_single('unban')

    def switch_rename(self):
        return self._switch_single('rename')

    def switch_lock(self):
        return self._switch_single('lock')

    def switch_config(self):
        return self._switch_multi('config', 2)


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
    switch_syntax = {
        'join': "<category>/<channel>=<alias> - Keep Aliases simple!"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doc__ = _USE_COMMAND.format(key=self.key, system_key=self.system_key)

    def switch_join(self):
        target = self.target_channel(self.lhslist)
        if not len(target) == 3:
            self.syntax_error()
        if not self.re_alias.match(self.rhs):
            self.syntax_error()
        self.caller.channels.add(target[2], self.rhs)
