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
        'name': "Account Channels",
        'system_typeclass': "athanor_channels.channels.account.AccountChannelSystem",
        "category_typeclass": "athanor_channels.channels.account.AccountChannelCategory",
        "channel_typeclass": "athanor_channels.channels.account.AccountChannel",
        "command_class": "athanor_channels.commands.account.AccountChannelCommand"
    }
    settings.CHANNEL_SYSTEMS["object"] = {
        'name': "Character Channels",
        'system_typeclass': "athanor_channels.channels.object.ObjectChannelSystem",
        "category_typeclass": "athanor_channels.channels.object.ObjectChannelCategory",
        "channel_typeclass": "athanor_channels.channels.object.ObjectChannel",
        "command_class": "athanor_channels.commands.object.ObjectChannelCommand"
    }
    settings.GAMEDB_MIXINS["ACCOUNT"].append("athanor_channels.mixins.AccountChannelMixin")
    settings.GAMEDB_MIXINS["CHARACTER"].append("athanor_channels.mixins.ObjectChannelMixin")
    settings.INLINEFUNC_MODULES.append('athanor_channels.inlinefuncs')
    settings.OPTIONS_ACCOUNT_DEFAULT['quotes_channel'] = ("Color for Quotation marks on Channels.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['speech_channel'] = ("Color for Dialogue on Channels.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['speaker_channel'] = ("Color for name of Speaker in channel dialogue.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['self_channel'] = ("Color for your own name in channel dialogue.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['other_channel'] = ("Default Color for names on channels.", "Color", 'n')
