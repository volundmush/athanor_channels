from athanor.utils.submessage import SubMessage


class ChannelSystemMessage(SubMessage):
    system_name = "CHANNEL"

    def send_target(self):
        pass


class ChannelCategoryMessage(SubMessage):
    system_name = "CHANNEL"

    def send_target(self):
        pass


class CreateCategory(ChannelCategoryMessage):
    source_message = "Successfully created Channel Category: {target_fullname}"
    target_message = ""
    admin_message = "|w{source_name}|n created Channel Category: {target_fullname}"


class RenameCategory(ChannelCategoryMessage):
    source_message = "Successfully renamed Channel Category: {old_name} to {target_fullname}"
    target_message = ""
    admin_message = "|w{source_name}|n created Channel Category: {old_name} to {target_fullname}"


class DeleteCategory(ChannelCategoryMessage):
    source_message = "Successfully |rDELETED|n Channel Category: {target_fullname}"
    target_message = ""
    admin_message = "|w{source_name}|n |rDELETED|n Channel Category: {target_fullname}"


class LockCategory(ChannelCategoryMessage):
    source_message = "Successfully locked Channel Category: {target_fullname} to: {lock_string}"
    target_message = ""
    admin_message = "|w{source_name}|n created Channel Category: {target_fullname} to: {lock_string}"


class ConfigCategory(ChannelCategoryMessage):
    source_message = "Successfully re-configured Channel Category: {target_fullname}. Set {config_op} to: {config_val}}"
    target_message = ""
    admin_message = "|w{source_name}|n created Channel Category: {target_fullname} to: {lock_string}"


class ChannelMessage(SubMessage):
    system_name = "CHANNEL"

    def send_target(self):
        pass


class CreateChannel(ChannelMessage):
    source_message = "Successfully created Channel: {target_fullname}"
    target_message = ""
    admin_message = "|w{source_name}|n created Channel: {target_fullname}"


class RenameChannel(ChannelMessage):
    source_message = "Successfully renamed Channel: {old_name} to {target_fullname}"
    target_message = "|w{source_name}|n created Channel: {old_name} to {target_fullname}"
    admin_message = "|w{source_name}|n created Channel: {old_name} to {target_fullname}"


class DeleteChannel(ChannelMessage):
    source_message = "Successfully |rDELETED|n Channel: {target_fullname}"
    target_message = "|w{source_name}|n |rDELETED|n Channel: {target_fullname}"
    admin_message = "|w{source_name}|n |rDELETED|n Channel: {target_fullname}"


class LockChannel(ChannelMessage):
    source_message = "Successfully locked Channel: {target_fullname} to: {lock_string}"
    target_message = "|w{source_name}|n created Channel: {target_fullname} to: {lock_string}"
    admin_message = "|w{source_name}|n created Channel: {target_fullname} to: {lock_string}"


class ConfigChannel(ChannelCategoryMessage):
    source_message = "Successfully re-configured Channel: {target_fullname}. Set {config_op} to: {config_val}}"
    target_message = "|w{source_name}|n created Channel: {target_fullname} to: {lock_string}"
    admin_message = "|w{source_name}|n created Channel: {target_fullname} to: {lock_string}"
