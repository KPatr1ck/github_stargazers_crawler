from typing import List, Tuple

from utils.log import logger
from utils.network import (get_api_content, get_headers, get_proxy,
                           get_respone_headers, get_webpage_content)

repo_api_base_url = 'https://api.github.com/repos/'
user_api_base_url = 'https://api.github.com/users/'
token = None  # Generated from https://github.com/settings/tokens


def set_api_token(t: str):
    global token
    assert isinstance(t, str), f'Type of token type must be str, but got {type(t)}: {t}.'
    logger.info(f'Set api token from {token} to {t}')
    token = t


def get_github_star_and_fork_count(repo: str = 'PaddlePaddle/PaddleHub') -> int:
    url = repo_api_base_url + repo
    try:
        headers, proxy = get_headers(), None  # api request with token
        headers.update({'Authorization': 'token ' + token})
        _, res = get_api_content(url, headers=headers, proxy=proxy)
        return int(res['stargazers_count']), int(res['forks_count'])
    except Exception as e:
        logger.error(f'Fail to parse page: {url}')
        logger.error(e)
        return -1


def get_github_stargazers_list(repo: str = 'PaddlePaddle/PaddleHub', page_size: int = 100,
                               page_num: int = 1) -> List[str]:
    url = repo_api_base_url + repo + f'/stargazers?per_page={page_size}&page={page_num}'
    try:
        headers, proxy = get_headers(), None  # api request with token
        headers.update({'Authorization': 'token ' + token})
        _, res = get_api_content(url, headers=headers, proxy=proxy)
        return [item['login'] for item in res]
    except Exception as e:
        logger.error(f'Fail to parse page: {url}')
        logger.error(e)
        return -1


def get_github_user_email(user: str = 'shayan-taheri') -> Tuple[int, str]:
    url = user_api_base_url + user
    try:
        headers, proxy = get_headers(), None  # api request with token
        headers.update({'Authorization': 'token ' + token})
        respone_headers, res = get_api_content(url, headers=headers, proxy=proxy)
        return int(respone_headers['X-RateLimit-Remaining']), res['email']
    except Exception as e:
        logger.error(f'Fail to parse page: {url}')
        logger.error(e)
        return -1, -1


def get_api_limit() -> int:
    url = 'https://api.github.com'
    try:
        headers, proxy = get_headers(), None  # api request with token
        headers.update({'Authorization': 'token ' + token})
        respone_headers = get_respone_headers(url, headers=headers, proxy=proxy)
        return int(respone_headers['X-RateLimit-Remaining'])
    except Exception as e:
        logger.error(f'Fail to parse page: {url}')
        logger.error(e)
        return -1
