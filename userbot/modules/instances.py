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

@register(outgoing=True, pattern=r"^\.insinfo$")
async def insinfo(insinf):
    """For .insinfo command, get container or instance usage."""

    await insinf.edit("`Initialize...`")

    # Define instance usage
    cpuName = "Docker Container Common CPU"
    cpuCoreCount = psutil.cpu_count(logical=True)
    cpuUsage = psutil.cpu_percent(interval=1)
    diskTotal = int(psutil.disk_usage('/').total/(1024*1024*1024))
    diskUsed = int(psutil.disk_usage('/').used/(1024*1024*1024))
    diskAvail = int(psutil.disk_usage('/').free/(1024*1024*1024))
    diskPercent = psutil.disk_usage('/').percent
    ramTotal = int(psutil.virtual_memory().total/(1024*1024))
    ramUsage = int(psutil.virtual_memory().used/(1024*1024))
    ramFree = int(psutil.virtual_memory().free/(1024*1024))
    ramUsagePercent = psutil.virtual_memory().percent
    upTime = await asyncrunapp(
                "uptime",
                "-p",
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )
    stdout, stderr = await upTime.communicate()
    upTimeOut = str(stdout.decode().strip()) + str(stderr.decode().strip())
    
    msg = '''
HANA-CI Instance Services
--------------------------------

CPU Info
CPU Name                  = {}
CPU Core Count            = {} Cores
CPU Usage                 = {} %
CPU Uptime                = {}

RAM Info
RAM Total Capacity        = {} MB
RAM Total Usage           = {} MB | {} %
RAM Total Free            = {} MB

Storage Info
Storage Total Capacity    = {} GB
Storage Total Usage       = {} GB | {} %
Storage Total Free        = {} GB\n'''.format(cpuName,cpuCoreCount,cpuUsage,upTimeOut,ramTotal,ramUsage,ramFree,ramUsagePercent,diskTotal,diskUsed,diskPercent,diskAvail)
    
    await insinf.edit("`"+msg+"`")

@register(outgoing=True, pattern=r"^\.inslogs$")
async def inslogs(insl):
    """For .insl command, get container or instance logs."""
    if not insl.text[0].isalpha() and insl.text[0] not in ("/", "#", "@", "!"):
        try:
            await insl.edit("`Initialize...`")

            fetch = await asyncrunapp(
                "bash",
                "sendLaravelLog.sh",
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
        "insinfo": ">`.insinfo`" "\nUsage: Shows container or instance usage.",
        "inslogs": ">`.inslogs`" "\nUsage: Shows container or instance logs.",
    }
)
