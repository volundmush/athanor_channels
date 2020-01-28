def init_settings(settings):
    settings.CHANNEL_HANDLER_CLASS = "athanor_channels.channelhandler.GlobalChannelHandler"
    settings.CMDSETS["ACCOUNT"].append("athanor_channels.cmdsets.AthanorAccountChannelCmdSet")
    settings.CMDSETS["CHARACTER"].append("athanor_channels.cmdsets.AthanorCharacterChannelCmdSet")
    settings.CONTROLLERS["channel"] = {
        'class': 'athanor_channels.controllers.AthanorChannelController'
    }
    settings.INSTALLED_APPS.append("athanor_channels")
    settings.CHANNEL_SYSTEMS = dict()
    settings.CHANNEL_SYSTEMS["account"] = {
        'system_typeclass': "athanor_channels.gamedb.AccountChannelSystem",
        "category_typeclass": "athanor_channels.gamedb.AccountChannelCategory",
        "channel_typeclass": "athanor_channels.gamedb.AccountChannel",
        "command_class": "athanor_channels.commands.AccountChannelCommand"
    }
    settings.CHANNEL_SYSTEM_TYPECLASS = "athanor_channels.gamedb.AccountChannelSystem"
    settings.CHANNEL_CATEGORY_TYPECLASS = "athanor_channels.gamedb.AccountChannelCategory"
    settings.CHANNEL_CHANNEL_TYPECLASS = "athanor_channels.gamedb.AthanorAccountChannel"
    settings.CHANNEL_COMMAND_CLASS = "athanor_channels.commands.AccountChannelCommand"
    settings.MIXINS["ACCOUNT"].append("athanor_channels.mixins.AccountChannelMixin")
    settings.MIXINS["CHARACTER"].append("athanor_channels.mixins.ObjectChannelMixin")