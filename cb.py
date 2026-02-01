import asyncio
import base64
import os

import aiohttp
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("base_cb_api")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


async def login(username, password):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}sessions",
                headers={
                    **headers,
                    "authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode('ascii')}".strip(
                        "b'"
                    ),
                },
            ) as response:
                if response.status < 400:
                    jsonData = await response.json()
                    if jsonData and "jwt" in jsonData:
                        print(f"{username} logged in successfully")
                        return jsonData
                print(f"Login failed for {username}")
                return None
    except Exception as e:
        print(f"Login has an error occurred: {e}")
        return None


async def getOrganizations(headers):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}v2/organizations", headers=headers
            ) as response:
                if response.status < 400:
                    jsonData = await response.json()
                    if jsonData and "data" in jsonData:
                        return jsonData["data"]
                return None
    except Exception as e:
        print(f"getOrganizations has an error occurred: {e}")
        return None


async def getClusters(headers, organizationId):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}v2/organizations/{organizationId}/clusters?perPage=100&page=1&sortBy=name&sortDirection=desc",
                headers=headers,
            ) as response:
                if response.status < 400:
                    jsonData = await response.json()
                    if jsonData and "data" in jsonData:
                        return jsonData["data"]
                return None
    except Exception as e:
        print(f"getClusters has an error occurred: {e}")
        return None


async def getProjects(headers, organizationId):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}v2/organizations/{organizationId}/projects?perPage=100&page=1",
                headers=headers,
            ) as response:
                if response.status < 400:
                    jsonData = await response.json()
                    if jsonData and "data" in jsonData:
                        return jsonData["data"]
                return None
    except Exception as e:
        print(f"getProjects has an error occurred: {e}")
        return None


async def turnOnCluster(headers, organizationId, projectId, clusterId):
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"turnOnAppService": True}
            async with session.post(
                f"{BASE_URL}v2/organizations/{organizationId}/projects/{projectId}/clusters/{clusterId}/on",
                headers=headers,
                json=payload,
            ) as response:
                if response.status == 202:
                    print(f"Cluster {clusterId} turned on successfully")
                    return True
                print(f"Cluster {clusterId} turned on failed")
                return None
    except Exception as e:
        print(f"turnOnCluster has an error occurred: {e}")
        return None


async def checkClusterHealth(headers, dataConnectUrl):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{dataConnectUrl}/v1/callerIdentity",
                headers=headers,
            ) as response:
                if response.status < 400:
                    print(f"Cluster is healthy")
                    return True
                print(f"Cluster is bad")
                return None
    except Exception as e:
        print(f"checkClusterHealth has an error occurred: {e}")
        return None
