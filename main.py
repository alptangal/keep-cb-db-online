import asyncio
import base64
import os
import queue
import random
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta

import aiohttp
import discord
import requests
import streamlit as st
from discord.ext import commands, tasks
from dotenv import load_dotenv

import cb

load_dotenv()
if "log_queue" not in st.session_state:
    st.session_state["log_queue"] = queue.Queue()

if "logs" not in st.session_state:
    st.session_state["logs"] = []

if "task_running" not in st.session_state:
    st.session_state["task_running"] = False
BOT_TOKEN = os.getenv("bot_token")
GUILD_NAME = os.getenv("guild_name")
RAW_CH = None
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def myStyle():
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
                    await cb.checkClusterHealth(
                        headers_basic, dataConnectUrl=cluster_url
                    )
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


thread = None


@st.cache_resource
def initialize_heavy_stuff():
    global thread
    # Đây là phần chỉ chạy ĐÚNG 1 LẦN khi server khởi động (hoặc khi cache miss)
    with st.spinner("running your scripts..."):
        thread = threading.Thread(target=myStyle, args=(st.session_state.log_queue,))
        thread.start()
        print(
            "Heavy initialization running..."
        )  # bạn sẽ thấy log này chỉ 1 lần trong console/cloud log

        return {
            "model": "loaded_successfully",
            "timestamp": time.time(),
            "db_status": "connected",
        }


st.title("my style")

# Dòng này đảm bảo: chạy 1 lần duy nhất, mọi user đều dùng chung kết quả
result = initialize_heavy_stuff()

st.success("The system is ready!")
st.write("Result:")
st.json(result)
with st.status("Processing...", expanded=True) as status:
    placeholder = st.empty()
    logs = []
    while (thread and thread.is_alive()) or not st.session_state.log_queue.empty():
        try:
            level, message = st.session_state.log_queue.get_nowait()
            logs.append((level, message))

            with placeholder.container():
                for lvl, msg in logs:
                    if lvl == "info":
                        st.write(msg)
                    elif lvl == "success":
                        st.success(msg)
                    elif lvl == "error":
                        st.error(msg)

            time.sleep(0.2)
        except queue.Empty:
            time.sleep(0.3)

    status.update(label="Hoàn thành!", state="complete", expanded=False)
