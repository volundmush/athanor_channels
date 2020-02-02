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
    settings.CHANNEL_SYSTEMS["character"] = {
        'name': "Character Channels",
        'system_typeclass': "athanor_channels.channels.character.CharacterChannelSystem",
        "category_typeclass": "athanor_channels.channels.character.CharacterChannelCategory",
        "channel_typeclass": "athanor_channels.channels.character.CharacterChannel",
        "command_class": "athanor_channels.commands.character.CharacterChannelCommand"
    }
    settings.GAMEDB_MIXINS["ACCOUNT"].append("athanor_channels.mixins.AccountChannelMixin")
    settings.GAMEDB_MIXINS["CHARACTER"].append("athanor_channels.mixins.CharacterChannelMixin")
    settings.INLINEFUNC_MODULES.append('athanor_channels.inlinefuncs')
    settings.OPTIONS_ACCOUNT_DEFAULT['quotes_channel'] = ("Color for Quotation marks on Channels.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['speech_channel'] = ("Color for Dialogue on Channels.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['speaker_channel'] = ("Color for name of Speaker in channel dialogue.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['self_channel'] = ("Color for your own name in channel dialogue.", "Color", 'n')
    settings.OPTIONS_ACCOUNT_DEFAULT['other_channel'] = ("Default Color for names on channels.", "Color", 'n')

    operations = {
        "channel_system_operate": {
            "description": "Is an Operator for all Channel Systems. All of them.",
            "permission": "Admin"
        },
        "channel_system_moderate": {
            "description": "Is a Moderator for all Channel Systems. All of them.",
            "permission": "Admin"
        },
        "channel_category_operate": {
            "description": "Is an Operator for all established Channel Categories. All of them.",
            "permission": "Admin"
        },
        "channel_category_moderate": {
            "description": "Is a Moderator for all established Channel Categories. All of them.",
            "permission": "Admin"
        },
        "channel_operate": {
            "description": "Is an Operator for all established Channels. All of them.",
            "permission": "Admin"
        },
        "channel_moderate": {
            "description": "Is a Moderator for all established Channels. All of them.",
            "permission": "Admin"
        }
    }
    settings.OPERATIONS.update(operations)
