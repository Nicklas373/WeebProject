# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Copyright 2024, Dicky Herlambang "Nicklas373" <herlambangdicky5@gmail.com>
# Copyright 2016-2024, HANA-CI Build Project
# SPDX-License-Identifier: GPL-3.0-or-later
# This module based on https://github.com/Nicklas373/CGSS_ACB_Downloader 
# Revision: 16630db88f0c123025b8459944ffe120c9718f69
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about latest revision on IM@S Cinderella Girls Starlight Stage JP dataset. """

from userbot import CMD_HELP
from userbot.events import register
from zipfile import ZipFile 
import csv
import json
import numpy as np
import requests
import shutil
import sqlite3,hashlib
import os, os.path
import time
from datetime import date
from lz4 import block
from pathlib import Path
from os import path

@register(outgoing=True, pattern=r"^\.cgss$")
async def cgss(cgss):
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
            await cgss.edit("`Getting game version from local source...`")
            if os.path.exists("Static_version"):
                f=Path("Static_version")
                f=open(f)
                old_version = f.read()
                f.close()
            else:
                f = open("Static_version", "w")
                f.write("000000")
                f.close()
                old_version = "000000"
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

@register(outgoing=True, pattern=r"^\.cgsssync$")
async def cgssSync(cgss):
    """For .cgssSync command, It will download assets data on IM@S Cinderella Girls Starlight Stage JP."""

    await cgss.edit("`Initialize...`")

    def dlfilefrmurl(url,path,headers):
        r=requests.get(url,headers=headers)
        fp=open(path,'wb')
        fp.write(r.content)
        fp.close()
        ldate=r.headers['Last-Modified']
        timeStruct=time.strptime(ldate,"%a, %d %b %Y %H:%M:%S GMT")
        timestamp=time.mktime(timeStruct)+8*60*60
        os.utime(path,(os.stat(path).st_atime,timestamp))
        r.close()

    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    def humansize(nbytes):
        i = 0
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])

    if not os.path.exists(os.getcwd()+"/cgss"):
        os.makedirs(os.getcwd()+"/cgss")

    cgss_path=os.getcwd()+"/cgss"
    cgss_logs=cgss_path+"/logs"
    csv_header= ['name', 'hash', 'size', 'date', 'manifest_version']

    try:
        await cgss.edit("**CGSS ACB Downloader | Starting!**")
        await cgss.edit("**from @ACA4DFA4 | Update & Maintain by @Nicklas373**")
        url="https://starlight.kirara.ca/api/v1/info"
        r=requests.get(url)
        jsonData=json.loads(r.content)
        version=jsonData['truth_version']
    except Exception as e:
        await cgss.edit("**Starlight kirara was down...**")
        await cgss.edit("**Getting game version from esterTion source...**")
        url="https://raw.githubusercontent.com/esterTion/cgss_master_db_diff/master/!TruthVersion.txt"
        r=requests.get(url)
        version=r.text.rstrip()
    else:
        await cgss.edit("**Unknown exception while getting manifest version !**")
                
    if os.path.exists(cgss_path+"/Static_version"):
        f=Path(cgss_path+"/Static_version")
        f=open(f)
        version_orig = f.read()
        f.close()
    else:
        f = open(cgss_path+"/Static_version", "w")
        f.write("000000")
        f.close()
        version_orig = "000000"
    f.close()

    if version_orig == "":
        version_orig = "000000"

    await cgss.edit("**Current manifest version:** `"+version_orig+"`")
    await cgss.edit("**New manifest version:** `"+version+"`")
    if os.path.exists(version_orig):
        if version_orig < version:
            await cgss.edit("`Current version with the latest manifest is outdated`")
            if not os.path.exists(cgss_path+"/"+version):
                os.mkdir(cgss_path+"/"+version)
            if os.path.exists(cgss_path+"\\"+version_orig):
                old_manifest=os.listdir(cgss_path+"/"+version_orig)
                try:
                    await cgss.edit("`Moving files from current manifest to latest manifest ...`")
                    for x in old_manifest:
                        shutil.move(cgss_path+"/"+version_orig+"/"+x,cgss_path+"/"+version+"/"+x)
                except OSError:
                        await cgss.edit("`Copy files from %s to static directory failed`" % version)
                await cgss.edit("`Removing old manifest files ...`")
                shutil.rmtree(cgss_path+"/"+version_orig)
            else:
                cgss.edit("**Previous manifest files:** `"+version_orig+"` **are not found !**")
                cgss.edit("**Abort moving to new manifests !**")
            f=Path("Static_version")
            f=open(f, 'w')
            f.write(version)
            f.close()
            await cgss.edit("`Re-writing old static manifest with the latest one`")
        elif version_orig == version:
            await cgss.edit("`Current version with the latest manifest is same`")
            await cgss.edit("`Re-checking manifest ...`")
        elif version_orig > version:
            await cgss.edit("`Current version with the latest manifest is unknown`")

    else:
        if not os.path.exists(cgss_path+"/"+version):
            os.mkdir(version)
        f=Path(cgss_path+"/Static_version")
        f=open(f, 'w')
        f.write(version)
        f.close()
        await cgss.edit("`Re-writing static manifest with the latest one`")
    if not os.path.exists(cgss_logs):
        os.makedirs(cgss_logs)
    if not os.path.exists(cgss_path+"/"+version+"/solo"):
        os.makedirs(cgss_path+"/"+version+"/solo")
                        
    dl_headers={'User-Agent': 'BNEI0242/96 CFNetwork/808.2.16 Darwin/16.3.01','RES_VER': version,'APP_VER': '10.3.5','OS_VER': 'iPhone OS 10.2','X-Unity-Version': '2017.4.2f2','Accept-Encoding': 'gzip','Connection' : 'Keep-Alive','Accept' : '*/*','DEVICE_ID': '10FB122A-CC47-4B10-8C78-0D1E6C22119C','DEVICE_NAME': 'iPhone8,1','USER_AGENT': 'BNEI0242/96 CFNetwork/808.2.16 Darwin/16.3.01','IP_ADDRESS': '192.168.12.14','GPU_NAME': 'Apple A9 GPU','KEYCHAIN': '339871861','CARRIER': 'KDDI','IDFA': '3350E88E-ED66-4D46-8B28-D82EA4A6397D'}

    if not os.path.exists(cgss_path+"/manifests"):
        os.mkdir(cgss_path+"/manifests")
    dbname=cgss_path+"/manifests/manifest_"+version+".db"
    lz4name=cgss_path+"/manifests/manifest_"+version+".db.lz4"
    if not os.path.exists(dbname):
        if not os.path.exists(lz4name):
            await cgss.edit("**Downloading lz4-compressed database ...**")
            url="https://asset-starlight-stage.akamaized.net/dl/"+version+"/manifests/iOS_AHigh_SHigh"
            r=requests.get(url,headers=dl_headers)
            with open(lz4name,'wb') as fp:
                fp.write(r.content)
                fp.close()
            ldate=r.headers['Last-Modified']
            timeStruct=time.strptime(ldate,"%a, %d %b %Y %H:%M:%S GMT")
            timestamp=time.mktime(timeStruct)+8*60*60
            os.utime(lz4name,(os.stat(lz4name).st_atime,timestamp))
            dat=r.content[4:]
            r.close()
        else:
            fp=open(lz4name,'rb')
            dat=fp.read()[4:]
            fp.close()
        dat=dat[0:4]+dat[12:]
        dec=block.decompress(dat)
        fp=open(dbname,'wb')
        fp.write(dec)
        fp.close()
        del(dec)
        del(dat)

    await cgss.edit("`Analysing sqlite3 database ...`")
    db=sqlite3.Connection(dbname)

    song_in_folder = np.array(["bgm", "bgm-movie", "sound", "se"])
    song_in_alias = np.array(["b", "m", "l", "s"])
    i = 0
    while i < len(song_in_folder):
        csv_path=cgss_logs+"/csv/"+song_in_folder[i]+".csv"
        await cgss.edit("**Downloading assets for:** `"+song_in_folder[i]+"`")
        query=db.execute("select name,hash,size from manifests where name like '"+song_in_alias[i]+"/%.acb' and size > '7000'")
        cgss_folder=cgss_path+"/"+version+"/"+song_in_folder[i]
        if not os.path.exists(cgss_path+"/"+version+"/"+song_in_folder[i]+"/"):
            os.makedirs(cgss_folder)
        fp1=open(cgss_path+"/"+version+"/"+song_in_folder[i]+"/"+song_in_alias[i]+"_ren1.bat",'w')
        fp2=open(cgss_path+"/"+version+"/"+song_in_folder[i]+"/"+song_in_alias[i]+"_ren2.bat",'w')
        today=date.today()
        if not os.path.exists(csv_path):
            if not os.path.exists(cgss_logs+"/csv/"):
                os.makedirs(cgss_logs+"/csv/")
            f = open(csv_path, 'w', encoding='UTF8', newline='')
            writer = csv.writer(f)
            writer.writerow(csv_header)
            f.close()    
        for name,hash,size in query:
            fp1.write("ren "+hash+' '+name[2:]+'\n')
            fp2.write("ren "+name[2:]+' '+hash+'\n')
            if not os.path.exists(cgss_path+"/"+version+"/"+song_in_folder[i]+"/"+hash):
                csv_rows=[name[2:], hash, humansize(size), today, version]
                f = open(csv_path, 'a', encoding='UTF8', newline='')
                writer = csv.writer(f)
                writer.writerow(csv_rows)
                f.close()        
                url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                dlfilefrmurl(url,cgss_path+"/"+version+"/"+song_in_folder[i]+"/"+hash,dl_headers)
                await cgss.edit("**Downloading assets:** `"+name[2:]+"`")
            else:
                fp=Path(cgss_path+"\\"+version+"\\"+song_in_folder[i]+"\\"+hash)
                fp.touch(exist_ok=True)
                fp=open(fp,'rb')
                buf=fp.read()
                fp.close()
                md5res=hashlib.md5(buf).hexdigest()
                del(buf)
                if md5res!=hash:
                    await cgss.edit("**File** `"+hash+'('+name+')'+"` **didn't pass md5check, delete and re-downloading ...**")
                    url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                    dlfilefrmurl(url,version+"\\"+song_in_folder[i]+"\\"+hash,dl_headers)
                    await cgss.edit("**Downloading assets:** `"+name[2:]+"`")
        fp1.close()
        fp2.close()
        i += 1
        
    query=db.execute("select name,hash,size from manifests where name like 'l/song_%_part/inst_song_%.awb' and name not like 'l/song_%_part/inst_song_%_se.awb' and name not like 'l/song_%_part/inst_song_%_another.awb'")
    
    if not os.path.exists(cgss_logs+"/txt/"):
        os.makedirs(cgss_logs+"/txt/")

    if os.path.exists(cgss_logs+"/txt/"+"solo_list.txt"):
        os.remove(cgss_logs+"/txt/"+"solo_list.txt")

    for name,hash,size in query:
        f=open(cgss_logs+"/txt/"+"solo_list.txt", 'a')
        if "_se" in name:
            f.write(name[2:][:-21]+"\n")
        else:
            f.write(name[2:][:-19]+"\n")
        f.close()

    solo_list = np.loadtxt(cgss_logs+"/txt/"+"solo_list.txt", dtype=str, delimiter=",") 
    for song_in_query in solo_list:
        await cgss.edit("**Downloading assets for:** `"+song_in_query+"`")
        query=db.execute("select name,hash,size from manifests where name like 'l/"+song_in_query+"/%.awb' and name not like 'l/song_%_part/inst_song_%_another.awb'")
        part=cgss_path+"/"+version+"/solo/"+song_in_query
        if not os.path.exists(part):
            os.makedirs(part)
        csv_solo_path=cgss_logs+"/csv/"+song_in_query+".csv"
        today=date.today()
        if not os.path.exists(csv_solo_path):
            if not os.path.exists(cgss_logs+"/csv/"):
                os.makedirs(cgss_logs+"/csv/")
            f = open(csv_solo_path, 'w', encoding='UTF8', newline='')
            writer = csv.writer(f)
            writer.writerow(csv_header)
            f.close() 
        for name,hash,size in query:
            fp1=open(cgss_path+"/"+version+"/solo/"+song_in_query+"/p_ren1.bat",'a')
            fp2=open(cgss_path+"/"+version+"/solo/"+song_in_query+"/p_ren2.bat",'a')
            fp1.write("ren "+hash+' '+name[17:]+'\n')
            fp2.write("ren "+name[17:]+' '+hash+'\n')
            if not os.path.exists(cgss_path+"/"+version+"/solo/"+song_in_query+"/"+hash):
                csv_solo_rows=[name[2:], hash, humansize(size), today, version]
                f = open(csv_solo_path, 'a', encoding='UTF8', newline='')
                writer = csv.writer(f)
                writer.writerow(csv_solo_rows)
                f.close()
                url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                dlfilefrmurl(url,cgss_path+"/"+version+"/solo/"+song_in_query+"/"+hash,dl_headers)
                await cgss.edit("**Downloading assets:** `"+name[17:]+"`")
            else:
                fp=Path(cgss_path+"/"+version+"/solo/"+song_in_query+"/"+hash)
                fp.touch(exist_ok=True)
                fp=open(fp,'rb')
                buf=fp.read()
                fp.close()
                md5res=hashlib.md5(buf).hexdigest()
                del(buf)
                if md5res!=hash:
                    await cgss.edit("**File** `"+hash+'('+name+')'+"` **didn't pass md5check, delete and re-downloading ...**")
                    url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                    dlfilefrmurl(url,cgss_path+"/"+version+"/solo/"+song_in_query+"/"+hash,dl_headers)
                    await cgss.edit("**Downloading assets:** `"+name[17:]+"`")
            fp1.close()
            fp2.close()
        
    query=db.execute("select name,hash,size from manifests where name like 'l/song_%_part/inst_song_%_another.awb'")
    if os.path.isfile(cgss_logs+"/txt/"+"solo_list_another.txt"):
        os.remove(cgss_logs+"/txt/"+"solo_list_another.txt")
        
    for name,hash,size in query:
        f=open(cgss_logs+"/txt/"+"solo_list_another.txt", 'a')
        f.write(name[2:][:-27]+"\n")
        f.close()

    solo_list = np.loadtxt(cgss_logs+"/txt/"+"solo_list_another.txt", dtype=str, delimiter=",") 
    for song_in_query in solo_list:
        new_song_code=song_in_query[5:][:-5]
        await cgss.edit("**Downloading assets for:** `"+song_in_query+"_another`...")
        query=db.execute("select name,hash,size from manifests where name like 'l/"+song_in_query+"/inst_song_"+new_song_code+"_%.awb'")
        part=cgss_path+"/"+version+"/solo/"+song_in_query+"_another"
        if not os.path.exists(part):
            os.makedirs(part)
        csv_solo_path=cgss_logs+"/csv/"+song_in_query+"_another.csv"
        today=date.today()
        if not os.path.exists(csv_solo_path):
            f = open(csv_solo_path, 'w', encoding='UTF8', newline='')
            writer = csv.writer(f)
            writer.writerow(csv_header)
            f.close() 
        for name,hash,size in query:
            fp1=open(cgss_path+"/"+version+"/solo/"+song_in_query+"_another/p_ren1.bat",'a')
            fp2=open(cgss_path+"/"+version+"/solo/"+song_in_query+"_another/p_ren2.bat",'a')
            fp1.write("ren "+hash+' '+name[17:]+'\n')
            fp2.write("ren "+name[17:]+' '+hash+'\n')
            if not os.path.exists(cgss_path+"/"+version+"/solo/"+song_in_query+"_another/"+hash):
                csv_solo_rows=[name[2:], hash, humansize(size), today, version]
                f = open(csv_solo_path, 'a', encoding='UTF8', newline='')
                writer = csv.writer(f)
                writer.writerow(csv_solo_rows)
                f.close()
                url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                dlfilefrmurl(url,cgss_path+"/"+version+"/solo/"+song_in_query+"_another/"+hash,dl_headers)
                await cgss.edit("**Downloading assets:** `"+name[17:]+"`")
            else:
                fp=Path(cgss_path+"/"+version+"/solo/"+song_in_query+"_another/"+hash)
                fp.touch(exist_ok=True)
                fp=open(fp,'rb')
                buf=fp.read()
                fp.close()
                md5res=hashlib.md5(buf).hexdigest()
                del(buf)
                if md5res!=hash:
                    await cgss.edit("**File** `"+hash+'('+name+')'+"` **didn't pass md5check, delete and re-downloading ...**")
                    url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                    dlfilefrmurl(url,cgss_path+"/"+version+"/solo/"+song_in_query+"_another/"+hash,dl_headers)
                    await cgss.edit("**Downloading assets:** `"+name[17:]+"`")
        fp1.close()
        fp2.close()
        
    await cgss.edit("**CGSS ACB Downloader | Finished!**")

@register(outgoing=True, pattern=r"^\.cgssarc$")
async def cgssArc(arc):
    """For .cgssArc command, It will archive all assets data on IM@S Cinderella Girls Starlight Stage JP."""

    await arc.edit("`Initialize...`")
    
    def get_all_file_paths(directory): 
        file_paths = [] 
        for root, files in os.walk(directory): 
            for filename in files: 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 
    
        return file_paths         
  
    cgss_path=os.getcwd()+"/cgss"
    if os.path.exists(cgss_path+"/Static_version"):
        f=Path(cgss_path+"/Static_version")
        f=open(f)
        version_orig = f.read()
        f.close()

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        asset_dir = ["bgm", "se", "solo" , "sound"]
        await arc.edit("`Begin archiving...`") 

        for asset in asset_dir:
            asset_paths = get_all_file_paths(cgss_path + "/" + version_orig + "/" + asset) 
            try:
                for file_name in asset_paths: 
                    await arc.edit("`Archiving: `"+file_name) 

                with ZipFile("downloads/"+asset+"_"+version_orig+".zip",'w') as zip: 
                    for file in asset_paths: 
                        zip.write(file) 
            except Exception:
                await arc.edit("`Archiving error !\nArchive Step: `"+asset) 
        await arc.edit("`Archiving completed !`")
    else:
        await arc.edit("`Abort archiving...`")
        await arc.edit("`Static_version not found !`")

CMD_HELP.update(
    {
        "cgss": ">`.cgss`" "\nUsage: Shows latest revision on IM@S Cinderella Girls Starlight Stage JP dataset.",
        "cgssarc": ">`.cgssarc`" "\nUsage: Archive assets data on IM@S Cinderella Girls Starlight Stage JP dataset.",
        "cgsssync": ">`.cgsssync`" "\nUsage: Download assets data on IM@S Cinderella Girls Starlight Stage JP."
    }
)
