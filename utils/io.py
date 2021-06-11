import csv
import os
from typing import List, Tuple

from .log import logger


def dump_list_to_csv(infos: List[Tuple[str, str]], output_file: str, header: List[str] = None):
    output_file = os.path.abspath(output_file)
    with open(output_file, "w") as f:
        writer = csv.writer(f)
        if header is not None and isinstance(header, list):
            writer.writerow(header)
        else:
            logger.warning('Writing csv file without header.')
        writer.writerows(infos)


def dump_list_to_file(infos: List[str], output_file: str):
    with open(output_file, 'w') as f:
        for info in infos:
            f.write(f'{info}\n')


def read_list_from_file(file: str) -> List[str]:
    names = []
    with open(file, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            names.append(line)
    return names
