# Copyright (C) 2019 The Raphielscape Company LLC.
# Copyright (C) 2024 HANA-CI Build Project
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about container / instances. """

from asyncio import create_subprocess_exec as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from userbot import CMD_HELP
from userbot.events import register

import psutil

@register(outgoing=True, pattern=r"^\.diskinfo$")
async def diskinfo(diskinf):
    """For .diskinf command, get container or instance disk usage."""

    await diskinf.edit("`Initialize...`")

    # Define total disk usage
    diskTotal = int(psutil.disk_usage('/').total/(1024*1024*1024))
    diskUsed = int(psutil.disk_usage('/').used/(1024*1024*1024))
    diskAvail = int(psutil.disk_usage('/').free/(1024*1024*1024))
    diskPercent = psutil.disk_usage('/').percent

    msg = '''
Storage Info
Storage Total Capacity    = {} GB
Storage Total Usage         = {} GB | {} %
Storage Total Free            = {} GB\n'''.format(diskTotal,diskUsed,diskPercent,diskAvail)
    
    await diskinf.edit("`"+msg+"`")

@register(outgoing=True, pattern=r"^\.inslogs$")
async def inslogs(insl):
    """For .insl command, get container or instance logs."""
    if not insl.text[0].isalpha() and insl.text[0] not in ("/", "#", "@", "!"):
        try:
            await insl.edit("`Initialize...`")

            fetch = await asyncrunapp(
                "sendLaravelLog.sh",
                "",
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )

            stdout, stderr = await fetch.communicate()
            result = str(stdout.decode().strip()) + str(stderr.decode().strip())

            await insl.edit("`Logs has been sent with: `" + result)
        except FileNotFoundError:
            await insl.edit("`FileNotFoundError: sendLaravelLog.sh`")
        except Exception:
            await insl.edit("`Undefined Exception !`")

CMD_HELP.update(
    {
        "diskinfo": ">`.diskinf`" "\nUsage: Shows container or instance disk usage.",
        "inslogs": ">`.inslogs`" "\nUsage: Shows container or instance logs.",
    }
)
