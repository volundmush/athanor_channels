from athanor.utils.message import AdminMessage


class ChannelMessage(AdminMessage):
    system_name = "CHANNEL"
    targets = ['enactor', 'target', 'user', 'admin']


class Create(ChannelMessage):
    messages = {
        'enactor': "Successfully created {target_typename}: {target_fullname}",
        'target': "|w{enactor_name}|n created {target_typename}: {target_fullname}",
        'admin': "|w{enactor_name}|n created {target_typename}: {target_fullname}"
    }


class Rename(ChannelMessage):
    messages = {
        'enactor': "Successfully renamed {target_typename}: {old_name} to {target_fullname}",
        'target': "|w{enactor_name}|n renamed {target_typename}: {old_name} to {target_fullname}",
        'admin': "|w{enactor_name}|n renamed {target_typename}: {old_name} to {target_fullname}"
    }


class Delete(ChannelMessage):
    messages = {
        'enactor': "Successfully |rDELETED|n {target_typename}: {target_fullname}",
        'target': "|w{enactor_name}|n |rDELETED|n {target_typename}: {target_fullname}",
        'admin': "|w{enactor_name}|n |rDELETED|n {target_typename}: {target_fullname}"
    }


class Lock(ChannelMessage):
    messages = {
        'enactor': "Successfully locked {target_typename}: {target_fullname} to: {lock_string}",
        'target': "|w{enactor_name}|n locked {target_typename}: {target_fullname} to: {lock_string}",
        'admin': "|w{enactor_name}|n locked {target_typename}: {target_fullname} to: {lock_string}"
    }


class Config(ChannelMessage):
    messages = {
        'enactor': "Successfully re-configured {target_typename}: {target_fullname}. Set {config_op} to: {config_val}}",
        'target': "|w{enactor_name}|n re-configured {target_typename}: {target_fullname}. Set {config_op} to: {config_val}}",
        'admin': "|w{enactor_name}|n re-configured {target_typename}: {target_fullname}. Set {config_op} to: {config_val}}"
    }


class Grant(ChannelMessage):
    pass


class Revoke(ChannelMessage):
    pass


class Ban(ChannelMessage):
    pass


class Unban(ChannelMessage):
    pass
