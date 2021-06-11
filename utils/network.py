import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

from .env import agent_list, http_proxy_list, https_proxy_list

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=5))
s.mount('https://', HTTPAdapter(max_retries=5))

import json
import random
from time import sleep

from .log import logger


def get_headers() -> dict:
    return {
        'User-Agent': random.choice(agent_list),
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }


def get_proxy(proxy_type: str = 'https') -> dict:
    proxy_list = https_proxy_list if proxy_type == 'https' else http_proxy_list
    if proxy_list:
        return {proxy_type: random.choice(proxy_list)}
    else:
        logger.warning(f'no valid {proxy_type} proxies...')
        return None


def get_proxy_online(proxy_type: str = 'https') -> dict:
    try:
        online_proxy_info = get_api_content(url='http://127.0.0.1:5010/get/', headers=get_headers())
        return {proxy_type: online_proxy_info['proxy']}
    except Exception as e:
        logger.warning(f'no valid online {proxy_type} proxies, use default...')
        return None


def get_webpage_content(url: str, headers: dict, proxy: dict = None, timeout=3) -> BeautifulSoup:
    try:
        sleep(random.randrange(start=0, stop=10, step=1) / 10)
        r = s.get(url, headers=headers, timeout=timeout, proxies=proxy)
        r.encoding = 'utf8'
        return BeautifulSoup(r.text, 'lxml')
    except requests.exceptions.RequestException as e:
        logger.error(f'Timeout when requesting page: {url}, proxy: {proxy}')
        logger.error(e)
        return None


def get_api_content(url: str, headers: dict, proxy: dict = None, auth: tuple = None, timeout=3) -> dict:
    try:
        sleep(random.randrange(start=0, stop=10, step=1) / 10)
        r = s.get(url, headers=headers, timeout=timeout, proxies=proxy, auth=auth)
        return r.headers, r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f'Timeout when requesting api: {url}, proxy: {proxy}')
        logger.error(e)
        return None


def get_respone_headers(url: str, headers: dict, proxy: dict = None, auth: tuple = None, timeout=3) -> dict:
    try:
        sleep(random.randrange(start=0, stop=10, step=1) / 10)
        r = s.get(url, headers=headers, timeout=timeout, proxies=proxy, auth=auth)
        return dict(r.headers)
    except requests.exceptions.RequestException as e:
        logger.error(f'Timeout when requesting respone headers: {url}, proxy: {proxy}')
        logger.error(e)
        return None
