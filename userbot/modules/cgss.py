# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Copyright 2024, Dicky Herlambang "Nicklas373" <herlambangdicky5@gmail.com>
# Copyright 2016-2024, HANA-CI Build Project
# SPDX-License-Identifier: GPL-3.0-or-later
# This module based on https://github.com/Nicklas373/CGSS_ACB_Downloader that only
# have minimal function to track DB manifest version and report to user.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about latest revision on IM@S Cinderella Girls Starlight Stage JP dataset. """

from userbot import CMD_HELP
from userbot.events import register
import json, requests

@register(outgoing=True, pattern=r"^\.cgssMdl$")
async def cgssMdl(cgss):
    """For .cgss command, get latest revision on IM@S Cinderella Girls Starlight Stage JP dataset."""
    version=None
    verbose=True

    await cgss.edit("`Initialize...`")

    if not version:
        if verbose:
            try:
                await cgss.edit("`Getting game version ...`")
                url="https://starlight.kirara.ca/api/v1/info"
                r=requests.get(url)
                jsonData=json.loads(r.content)
                version=jsonData['truth_version']
            except Exception as e:
                await cgss.edit("`No DB service was available!...`")
                version="NULL"
            else:
                await cgss.edit("`Getting game version from esterTion source...`")
                url="https://raw.githubusercontent.com/esterTion/cgss_master_db_diff/master/!TruthVersion.txt"
                r=requests.get(url)
                version=r.text.rstrip()
            await cgss.edit("`Getting game version from local repository...`")
            url="https://raw.githubusercontent.com/Nicklas373/CGSS_ACB_Downloader/master/Static_version"
            r=requests.get(url)
            old_version=r.text.rstrip()
            if (version > old_version):
                reason="Local DB older than Dynamic DB!"
            elif (version == old_version):
                reason="Local DB on latest version!"
            elif (version < old_version):
                reason="Local DB higher than Dynamic DB, ERROR"
            result=(
                    f"**CGSS DB Manifest Ver.**\n"
                    f"\n"
                    f"**Local DB Ver.** : `{old_version}`\n"
                    f"**Online DB Ver.** : `{version}`\n"
                    f"**Status** : `{reason}`\n"
                    f"\n"
                    )
            await cgss.edit(result)


CMD_HELP.update(
    {
        "cgssMdl": ">`.cgss`" "\nUsage: Shows latest revision on IM@S Cinderella Girls Starlight Stage JP dataset.",
    }
)
