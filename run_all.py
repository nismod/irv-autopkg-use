import logging
import sys
import time

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)
import irv_autopkg_client
from requests.exceptions import HTTPError
from tqdm import tqdm

logger = logging.getLogger(__file__)

client = irv_autopkg_client.Client()
countries = [country["name"] for country in client.boundary_list()]

all_datasets = set(
    [
        dataset
        for dataset in client.dataset_list()
        if "test_fail_processor" not in dataset
    ]
)
remaining_countries = {iso: [] for iso in set(countries)}
logger.info("%s of %s remaining.", len(remaining_countries), len(countries))
logger.info(all_datasets)


def extract_datasets(country_iso):
    """Query which datasets have already been processed for a boundary"""
    existing_meta = client.extract(country_iso)
    datasets = [
        f"{r['name']}.{r['version']}" for r in existing_meta["datapackage"]["resources"]
    ]
    return set(datasets)


# check all datasets
for country_iso in countries:
    # poll for job completion
    try:
        computed_datasets = extract_datasets(country_iso)
    except HTTPError:
        continue

    if len(computed_datasets) == len(all_datasets):
        del remaining_countries[country_iso]
    else:
        remaining_countries[country_iso] = all_datasets - computed_datasets
        logger.info("%s : %s remaining.", country_iso, remaining_countries[country_iso])


logger.info(countries)

logger.info("%s of %s remaining.", len(remaining_countries), len(countries))


while True:
    try:
        # submit jobs for all remaining countries
        job_ids = {}
        for country_iso in tqdm(remaining_countries):
            job_id = client.job_submit(
                country_iso, list(remaining_countries[country_iso])
            )
            job_ids[country_iso] = job_id
            time.sleep(10)

        while True:
            # check all jobs
            tmp = job_ids.copy()
            for country_iso, job_id in tqdm(tmp.items()):
                # poll for job completion
                if client.job_complete(job_id):
                    del job_ids[country_iso]
                    del remaining_countries[country_iso]
                time.sleep(1)

            logger.debug(remaining_countries)
            logger.info(f"{len(remaining_countries)} of {len(countries)} remaining.")

            if len(remaining_countries) == 0:
                break

        break
    except HTTPError as err:
        logger.error("%s", err)
        time.sleep(10)
        continue
