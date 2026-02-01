import asyncio
import base64
import os
import sys
import time
from datetime import datetime, timedelta

import aiohttp
import discord
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

import cb

load_dotenv()
BOT_TOKEN = os.getenv("bot_token")
GUILD_NAME = os.getenv("guild_name")
RAW_CH = None
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    global RAW_CH
    for guild in client.guilds:
        if guild.name == GUILD_NAME:
            categories = guild.categories
            if categories:
                for category in categories:
                    for channel in category.channels:
                        if channel.name == "raw":
                            RAW_CH = channel
                            if not checkClusters.is_running():
                                checkClusters.start(guild)


@tasks.loop(seconds=60)  # Chỉnh thời gian ở đây (seconds, minutes, hours)
async def checkClusters(guild):
    if RAW_CH:
        async for msg in RAW_CH.history():
            username = msg.content.split("|")[0]
            password = msg.content.split("|")[1]
            bearer_token = msg.content.split("|")[2]
            username_cluster = msg.content.split("|")[3]
            password_cluster = msg.content.split("|")[4]
            cluster_url = None
            headers_basic = {
                "authorization": f"Basic {base64.b64encode(f'{username_cluster}:{password_cluster}'.encode()).decode('ascii')}".strip(
                    "b'"
                )
            }
            if len(msg.content.split("|")) > 4:
                cluster_url = msg.content.split("|")[5]
            if cluster_url:
                await cb.checkClusterHealth(headers_basic, dataConnectUrl=cluster_url)
            # result = await cb.login(username, password)
            # if result:
            #     headers_bearer = {"authorization": f"Bearer {result['jwt']}"}
            #     organizations = await cb.getOrganizations(headers_bearer)
            #     if organizations:
            #         for organization in organizations:
            #             projects = await cb.getProjects(
            #                 headers_bearer, organization["data"]["id"]
            #             )
            #             clusters = await cb.getClusters(
            #                 headers_bearer, organization["data"]["id"]
            #             )
            #             if clusters:
            #                 for cluster in clusters:
            #                     if cluster["data"]["status"]["state"] == "turned_off":
            #                         projectId = cluster["data"]["project"]["id"]
            #                         await cb.turnOnCluster(
            #                             headers_bearer,
            #                             organization["data"]["id"],
            #                             projectId,
            #                             cluster["data"]["id"],
            #                         )
            #                     else:
            #                         await cb.checkClusterHealth(
            #                             headers_basic,
            #                             dataConnectUrl=cluster["data"][
            #                                 "dataApiHostname"
            #                             ],
            #                         )


if BOT_TOKEN:
    client.run(BOT_TOKEN)
