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
from zipfile import ZipFile 
import csv
import json
import numpy as np
import requests
import shutil
import sqlite3,hashlib
import os, sys, os.path
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
        await cgss.edit("\tCGSS ACB Downloader | Starting!")
        await cgss.edit("\tfrom @ACA4DFA4 | Update & Maintain by @Nicklas373")
        url="https://starlight.kirara.ca/api/v1/info"
        r=requests.get(url)
        jsonData=json.loads(r.content)
        version=jsonData['truth_version']
    except Exception as e:
        await cgss.edit("\tStarlight kirara was down...")
        await cgss.edit("\tGetting game version from esterTion source...")
        url="https://raw.githubusercontent.com/esterTion/cgss_master_db_diff/master/!TruthVersion.txt"
        r=requests.get(url)
        version=r.text.rstrip()
    else:
        await cgss.edit("Unknown exception while getting manifest version !")
                
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
    await cgss.edit("\tCurrent manifest version = "+version_orig)
    await cgss.edit("\tNew manifest version = "+version)
    if path.exists(version_orig):
        if version_orig < version:
            await cgss.edit("\tCurrent version with the latest manifest is outdated")
            os.mkdir("./"+version)
            old_manifest=os.listdir("./"+version_orig)
            try:
                await cgss.edit("\tMoving files from current manifest to latest manifest ...")
                for x in old_manifest:
                    shutil.move("./"+version_orig+"/"+x,"./"+version+"/"+x)
            except OSError:
                    await cgss.edit("\tCopy files from %s to static directory failed" % version)
            await cgss.edit("\tRemoving old manifest files ...")
            shutil.rmtree("./"+version_orig)
            f=Path("Static_version")
            f=open(f, 'w')
            f.write(version)
            f.close()
            await cgss.edit("\tRe-writing old static manifest with the latest one")
        elif version_orig == version:
            await cgss.edit("\tCurrent version with the latest manifest is same")
            await cgss.edit("\tRe-checking manifest ...")
        elif version_orig > version:
            await cgss.edit("\tCurrent version with the latest manifest is unknown")

    else:
        os.mkdir(version)
        f=Path(cgss_path+"/Static_version")
        f=open(f, 'w')
        f.write(version)
        f.close()
        await cgss.edit("\tRe-writing static manifest with the latest one")
    if not os.path.exists(cgss_logs):
        os.makedirs(cgss_logs)
    if not os.path.exists(cgss_path+"/"+version+"/solo"):
        os.makedirs(cgss_path+"/"+version+"/solo")
                        
    dl_headers={'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.0; Nexus 42 Build/XYZZ1Y)','X-Unity-Version': '2017.4.2f2','Accept-Encoding': 'gzip','Connection' : 'Keep-Alive','Accept' : '*/*'}

    if not os.path.exists("./manifests"):
        os.mkdir("./manifests")
    dbname="./manifests/manifest_"+version+".db"
    lz4name="./manifests/manifest_"+version+".db.lz4"
    if not os.path.exists(dbname):
        if not os.path.exists(lz4name):
            await cgss.edit("\tDownloading lz4-compressed database ...")
            url="https://asset-starlight-stage.akamaized.net/dl/"+version+"/manifests/Android_AHigh_SHigh"
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

    await cgss.edit("\tAnalysing sqlite3 database ...\n")
    db=sqlite3.Connection(dbname)

    song_in_folder = np.array(["bgm", "sound", "se"])
    song_in_alias = np.array(["b", "l", "s"])
    i = 0
    while i < 3:
        csv_path=cgss_logs+"/csv/"+song_in_folder[i]+".csv"
        await cgss.edit("\tDownloading assets for: "+song_in_folder[i]+"...")
        query=db.execute("select name,hash,size from manifests where name like '"+song_in_alias[i]+"/%.acb' and size > '7000'")
        cgss_folder=cgss_path+"/"+version+"/"+song_in_folder[i]
        if not os.path.exists(version+"/"+song_in_folder[i]+"/"):
            os.makedirs(cgss_folder)
        fp1=open(version+"/"+song_in_folder[i]+"/"+song_in_alias[i]+"_ren1.bat",'w')
        fp2=open(version+"/"+song_in_folder[i]+"/"+song_in_alias[i]+"_ren2.bat",'w')
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
            if not os.path.exists(version+"/"+song_in_folder[i]+"/"+hash):
                csv_rows=[name[2:], hash, humansize(size), today, version]
                f = open(csv_path, 'a', encoding='UTF8', newline='')
                writer = csv.writer(f)
                writer.writerow(csv_rows)
                f.close()        
                url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                dlfilefrmurl(url,version+"/"+song_in_folder[i]+"/"+hash,dl_headers)
        fp1.close()
        fp2.close()
        i += 1
        
    query=db.execute("select name,hash,size from manifests where name like 'l/song_%_part/inst_song_%.awb' and name not like 'l/song_%_part/inst_song_%_se.awb' and name not like 'l/song_%_part/inst_song_%_another.awb'")
    
    if not os.path.exists(cgss_logs+"/txt/"):
        os.makedirs(cgss_logs+"/txt/")

    if os.path.isfile(cgss_logs+"/txt/"+"solo_list.txt"):
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
        await cgss.edit("\tDownloading assets for: "+song_in_query+"...")
        query=db.execute("select name,hash,size from manifests where name like 'l/"+song_in_query+"/%.awb' and name not like 'l/song_%_part/inst_song_%_another.awb'")
        part=version+"/solo/"+song_in_query
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
            fp1=open(version+"/solo/"+song_in_query+"/p_ren1.bat",'a')
            fp2=open(version+"/solo/"+song_in_query+"/p_ren2.bat",'a')
            fp1.write("ren "+hash+' '+name[17:]+'\n')
            fp2.write("ren "+name[17:]+' '+hash+'\n')
            if not os.path.exists(version+"/solo/"+song_in_query+"/"+hash):
                csv_solo_rows=[name[2:], hash, humansize(size), today, version]
                f = open(csv_solo_path, 'a', encoding='UTF8', newline='')
                writer = csv.writer(f)
                writer.writerow(csv_solo_rows)
                f.close()
                url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                dlfilefrmurl(url,version+"/solo/"+song_in_query+"/"+hash,dl_headers)
            else:
                fp=Path(cgss_path+"/"+version+"/solo/"+song_in_query+"/"+hash)
                fp.touch(exist_ok=True)
                fp=open(fp,'rb')
                buf=fp.read()
                fp.close()
                md5res=hashlib.md5(buf).hexdigest()
                del(buf)
                if md5res!=hash:
                    await cgss.edit("\tFile "+hash+'('+name+')'+" didn't pass md5check, delete and re-downloading ...")
                    url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                    dlfilefrmurl(url,version+"/solo/"+song_in_query+"/"+hash,dl_headers)
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
        await cgss.edit("\tDownloading assets for: "+song_in_query+"_another...")
        query=db.execute("select name,hash,size from manifests where name like 'l/"+song_in_query+"/inst_song_"+new_song_code+"_%.awb'")
        part=version+"/solo/"+song_in_query+"_another"
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
            fp1=open(version+"/solo/"+song_in_query+"_another/p_ren1.bat",'a')
            fp2=open(version+"/solo/"+song_in_query+"_another/p_ren2.bat",'a')
            fp1.write("ren "+hash+' '+name[17:]+'\n')
            fp2.write("ren "+name[17:]+' '+hash+'\n')
            if not os.path.exists(version+"/solo/"+song_in_query+"_another/"+hash):
                csv_solo_rows=[name[2:], hash, humansize(size), today, version]
                f = open(csv_solo_path, 'a', encoding='UTF8', newline='')
                writer = csv.writer(f)
                writer.writerow(csv_solo_rows)
                f.close()
                url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                dlfilefrmurl(url,version+"/solo/"+song_in_query+"_another/"+hash,dl_headers)
            else:
                fp=Path(cgss_path+"/"+version+"/solo/"+song_in_query+"_another/"+hash)
                fp.touch(exist_ok=True)
                fp=open(fp,'rb')
                buf=fp.read()
                fp.close()
                md5res=hashlib.md5(buf).hexdigest()
                del(buf)
                if md5res!=hash:
                    await cgss.edit("\tFile "+hash+'('+name+')'+" didn't pass md5check, delete and re-downloading ...")
                    url="http://asset-starlight-stage.akamaized.net/dl/resources/Sound/"+hash[:2]+"/"+hash
                    dlfilefrmurl(url,version+"/solo/"+song_in_query+"_another/"+hash,dl_headers)
        fp1.close()
        fp2.close()
        
    await cgss.edit("\tCGSS ACB Downloader | Finished!")

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

        for asset in asset_dir:
            asset_paths = get_all_file_paths(version_orig + "/" + asset) 

            await arc.edit("`Begin archiving...`") 
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
