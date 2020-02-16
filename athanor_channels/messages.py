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
    messages = {
        'enactor': "Successfully granted {user_name} the {status} Status on: {target_fullname}",
        'target': "|w{enactor_name}|n granted {user_name} the {status} Status on this {target_typename}",
        'admin': "|w{enactor_name}|n granted {user_name} the {status} Status on: {target_fullname}"
    }


class Revoke(ChannelMessage):
    messages = {
        'enactor': "Successfully revoked {user_name}'s {status} Status on: {target_fullname}",
        'target': "|w{enactor_name}|n revoked {user_name}'s {status} Status on this {target_typename}",
        'admin': "|w{enactor_name}|n revoked {user_name}'s {status} Status on: {target_fullname}"
    }


class Ban(ChannelMessage):
    messages = {
        'enactor': "Successfully banned {user_name}'s from: {target_fullname} for: {duration_style_2}",
        'target': "|w{enactor_name}|n banned {user_name} from this {target_typename} for {duration_style_2}",
        'admin': "|w{enactor_name}|n banned {user_name}'s from: {target_fullname} for: {duration_style_2}",
    }


class Unban(ChannelMessage):
    messages = {
        'enactor': "Successfully lifted {user_name}'s ban from: {target_fullname}",
        'target': "|w{enactor_name}|n lifted {user_name} ban from this {target_typename}",
        'admin': "|w{enactor_name}|n lifted {user_name}'s ban from: {target_fullname}",
    }


class Describe(ChannelMessage):
    pass
