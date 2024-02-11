from dotenv import load_dotenv
load_dotenv()

import os
import re
import requests
from fastapi import HTTPException
from loguru import logger

logger.add("1_week.log", rotation="1 week")


# BING_MKT = "en-US"
BING_MKT = "zh-CN"
REFERENCE_COUNT = 8


def parse_list(text: str):
    out = []
    arr = text.split("\n")
    for i in arr:
        # print(i)
        _i = re.sub(r"\d+\.\s+", "", i)
        out.append(_i)
    return out


def get_context_search_bing(query: str):
    contexts = search_with_bing(query)
    # print(contexts)
    context = "\n\n".join(
        [f"[{i+1}] {c['snippet']}" for i, c in enumerate(contexts)]
    )
    # print(context)
    sources = []
    for i in contexts:
        _i = {
            "name": i["name"],
            "url": i["url"],
            "snippet": i["snippet"]
        }
        sources.append(_i)
    return context, sources


def search_with_bing(query: str):
    """
    Search with bing and return the contexts.
    """
    search_api_key = os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
    params = {"q": query, "mkt": BING_MKT}
    response = requests.get(
        "https://api.bing.microsoft.com/v7.0/search",
        headers={"Ocp-Apim-Subscription-Key": search_api_key},
        params=params,
        timeout=5,
    )
    if not response.ok:
        logger.error(f"{response.status_code} {response.text}")
        raise HTTPException(response.status_code, "Search engine error.")
    json_content = response.json()
    try:
        contexts = json_content["webPages"]["value"][:REFERENCE_COUNT]
        # logger.info(f"bing: {contexts}")
    except KeyError:
        logger.error(f"Error encountered: {json_content}")
        return []
    return contexts


def search_with_google(query: str):
    """
    Search with google and return the contexts.
    """
    search_api_key = os.environ["GOOGLE_SEARCH_API_KEY"]
    params = {
        "key": search_api_key,
        "cx": "",
        "q": query,
        "num": REFERENCE_COUNT,
    }
    response = requests.get(
        "https://customsearch.googleapis.com/customsearch/v1", params=params, timeout=5
    )
    if not response.ok:
        logger.error(f"{response.status_code} {response.text}")
        raise HTTPException(response.status_code, "Search engine error.")
    json_content = response.json()
    try:
        contexts = json_content["items"][:REFERENCE_COUNT]
        print(f"google: {contexts}")
    except KeyError:
        logger.error(f"Error encountered: {json_content}")
        return []
    return contexts

