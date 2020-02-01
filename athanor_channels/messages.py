from athanor.utils.submessage import SubMessage


class ChannelSystemMessage(SubMessage):
    system_name = "CHANNEL"

    def send_target(self):
        pass


class ChannelCategoryMessage(SubMessage):
    system_name = "CHANNEL"

    def send_target(self):
        pass


class ChannelMessage(SubMessage):
    system_name = "CHANNEL"

    def send_target(self):
        pass


class CreateMessage(ChannelMessage):
    source_message = ""
    target_message = ""
    admin_message = "|w{source_name}|n created Account: |w{target_name}|n"


class RenameMessage(ChannelMessage):
    source_message = "Successfully renamed Account: |w{old_name}|n to |w{target_name}"
    target_message = "|w{source_name}|n renamed your Account from |w{old_name}|n to |w{target_name}"
    admin_message = "|w{source_name}|n renamed Account |w{old_name}|n to |w{target_name}"
