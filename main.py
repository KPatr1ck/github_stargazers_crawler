import argparse
import ast
import json
import os
from time import sleep
from typing import List

from pathos.multiprocessing import ThreadPool

from github_crawler import (get_api_limit, get_github_star_and_fork_count, get_github_stargazers_list,
                            get_github_user_email, set_api_token)
from utils.io import dump_list_to_csv, dump_list_to_file, read_list_from_file
from utils.log import logger

parser = argparse.ArgumentParser(__doc__)
parser.add_argument("--repos", type=str, required=True, help="Target repos to fetch.")
parser.add_argument("--output_dir", type=str, default='./output', help="Output directory to save users' information.")
parser.add_argument("--num_workers", type=int, default=100, help="Number of workers to fetch users' emails.")
parser.add_argument("--api_limit_threshold", type=int, default=200, help="Api requests limit threshold.")

args = parser.parse_args()


def fetch_repo_stargazers(repo: str, page_size: int = 100) -> List[str]:
    stargazers_count, _ = get_github_star_and_fork_count(repo)
    # logger.info(f'[{repo}]Repo stars: {stargazers_count}')

    page_num = 1
    stargazers = []
    while stargazers_count > 0:
        # logger.info(f'[{repo}]Fetching page: {page_num}')
        fetch_list = get_github_stargazers_list(repo=repo, page_size=page_size, page_num=page_num)
        assert isinstance(fetch_list, list) and len(fetch_list) > 0, \
            f'Fetch stargazers list failed, repo: {repo}, page_size: {page_size}, page_num: {page_num}'
        stargazers.extend(fetch_list)

        stargazers_count -= page_size
        page_num += 1

    logger.info(f'[{repo}]Number of stargazers fetched: {len(stargazers)}')
    return stargazers


def wait(sec: int = 3600, limit: int = 0):
    logger.info(f'Sleep {sec} secs to wait api limit, current remains: {limit}')
    sleep(sec)


def fetch_user_email(user: str) -> str:
    limit, email = get_github_user_email(user)
    if limit < args.api_limit_threshold:
        # TODO: Multi tokens switching supported.
        wait(3600, limit)

    if isinstance(email, str) and '@' in email:
        return email
    else:
        return None


if __name__ == "__main__":
    # Convert to abs path
    json_file = os.path.expanduser(args.repos) if args.repos.startswith('~/') else os.path.abspath(args.repos)
    output_dir = os.path.expanduser(args.output_dir) if args.output_dir.startswith('~/') else os.path.abspath(
        args.output_dir)

    assert os.path.isfile(args.repos) and args.repos.endswith('.json'), \
        f'Repos file is invalid: {args.repos}'
    with open(args.repos, 'r') as f:
        info_dict = json.load(f)
        token = info_dict['token']
        repo_urls = info_dict['repos']

    set_api_token(token)
    repo_names = {item: '/'.join(url.split('/')[-2:]) for item, url in repo_urls.items()}

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Fetch repos stargazers
    fetch_repos = []
    for repo_name in repo_names.values():  # Check whether stargazers list exists.
        if not os.path.exists(os.path.join(output_dir, f'{repo_name.replace("/", "_")}_stargazers.txt')):
            fetch_repos.append(repo_name)

    if len(fetch_repos) > 0:
        logger.info(f'Start fetching stargazers from: {fetch_repos}')
        pool = ThreadPool(len(fetch_repos))
        res = pool.map(fetch_repo_stargazers, fetch_repos)
        pool.close()
        pool.join()

        for repo_name, stargazers in zip(fetch_repos, res):
            dump_list_to_file(stargazers, os.path.join(output_dir, f'{repo_name.replace("/", "_")}_stargazers.txt'))

    # Fetch user email
    for repo_name in repo_names.values():
        # Read stargazers from *.txt file
        stargazers = read_list_from_file(os.path.join(output_dir, f'{repo_name.replace("/", "_")}_stargazers.txt'))

        logger.info(f'[{repo_name}]Start fetching emails of {len(stargazers)} users...')
        pool = ThreadPool(args.num_workers)
        emails = pool.map(fetch_user_email, stargazers)

        # Save to *.csv file
        output_file = os.path.join(output_dir, f'{repo_name.replace("/", "_")}_stargazers_with_emails.csv')
        dump_list_to_csv([(name, email if email is not None else 'None') for name, email in zip(stargazers, emails)],
                         output_file,
                         header=['github user', 'email'])
        logger.info(f'[{repo_name}]Output saved to: {output_file}')
