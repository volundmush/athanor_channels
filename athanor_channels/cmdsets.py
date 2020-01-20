from evennia.commands.default import comms
from athanor.cmdsets.base import AthanorCmdSet
from athanor_channels.commands import CmdAccountChannelAdmin, CmdObjectChannelAdmin


class AthanorAccountChannelCmdSet(AthanorCmdSet):
    to_remove = [comms.CmdAddCom, comms.CmdDelCom, comms.CmdAllCom, comms.CmdChannels, comms.CmdCdesc,
                 comms.CmdCdestroy, comms.CmdChannelCreate, comms.CmdClock, comms.CmdCBoot, comms.CmdCemit,
                 comms.CmdCWho, comms.CmdIRC2Chan, comms.CmdIRCStatus, comms.CmdRSS2Chan, comms.CmdGrapevine2Chan]
    to_add = [CmdAccountChannelAdmin]


class AthanorCharacterChannelCmdSet(AthanorCmdSet):
    to_add = [CmdObjectChannelAdmin]
