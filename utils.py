import os


def aqueduct_rp(path: str) -> int:
    """
    Get return period from aqueduct flood map name, for example:
    'data/bgd/wri_aqueduct/inuncoast_rcp4p5_wtsub_2050_rp0010_5.tif' -> 10
    """
    return int(os.path.basename(path).split("_")[-2][-4:])
