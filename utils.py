import os
import re

import requests


def aqueduct_rp(path: str) -> int:
    """
    Get return period from aqueduct flood map name, for example:
    'data/bgd/wri_aqueduct/inuncoast_rcp4p5_wtsub_2050_rp0010_5.tif' -> 10
    """
    return int(os.path.basename(path).split("_")[-2][-4:])


def download_file(url, file_path):
    with open(file_path, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


def download_data(paths: list[str], directory: str, filter_regex: str = "") -> None:
    """
    Download files hosted as `paths` to `directory`, filtered by an optional `filter_regex`.
    """

    to_download = filter(lambda s: re.search(filter_regex, s), paths)

    os.makedirs(directory, exist_ok=True)
    for url in to_download:
        filename = url.split("/")[-1]
        filepath = os.path.join(directory, filename)
        download_file(url, filepath)
