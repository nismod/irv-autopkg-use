from typing import Callable

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from snail.core.intersections import split_linestring
from snail.core.intersections import get_cell_indices as get_cell_indicies_of_midpoint


def check_raster_grid_consistent(raster_paths: list[str]) -> None:
    """
    Check a set of rasters are on the same grid.
    """
    if len(raster_paths) > 1:
        reference, *others = raster_paths

        with rasterio.open(reference) as dataset:
            raster_width = dataset.width
            raster_height = dataset.height
            raster_transform = list(dataset.transform)

        # check all raster files use the same grid
        for raster_path in others:
            with rasterio.open(raster_path) as raster:
                if (
                    raster_width != raster.width
                    or raster_height != raster.height
                    or raster_transform != list(raster.transform)
                ):
                    raise AttributeError(
                        (
                            f"Raster attribute mismatch in file {raster_path}:\n"
                            f"Height: expected={raster_height}; actual={raster.height}\n"
                            f"Width: expected={raster_width}; actual={raster.width}\n"
                            f"Transform equal? {'True' if list(raster.transform) == raster_transform else 'False'}"
                        )
                    )


def split_linestrings(
    features: gpd.GeoDataFrame, raster: rasterio.io.DatasetReader
) -> gpd.GeoDataFrame:
    """
    Split feature linestrings on a raster grid
    """

    if set(features.geometry.type) != {"LineString"}:
        raise ValueError("Can only split LineString geometries")

    all_splits = []
    all_indicies = []
    for edge in features.itertuples():
        split_geoms = split_linestring(
            edge.geometry,
            raster.width,
            raster.height,
            list(raster.transform),
        )
        all_splits.extend(split_geoms)
        all_indicies.extend([edge.Index] * len(split_geoms))

    return gpd.GeoDataFrame({"original_index": all_indicies, "geometry": all_splits})


def cell_indicies_assigner(raster: rasterio.io.DatasetReader) -> Callable:
    """
    Given an open raster, return a function that can check a geometry against the
    raster grid and return grid cell indicies for that geometry.
    """

    def cell_indicies_of_split_geometry(geometry, *args, **kwargs) -> pd.Series:
        """
        Given a geometry, find the cell index (i, j) of its midpoint for the
        enclosing raster parameters.

        N.B. There is no checking whether a geometry spans more than one cell.
        """

        # integer indicies
        i, j = get_cell_indicies_of_midpoint(
            geometry, raster.height, raster.width, raster.transform
        )

        # die if we're out of bounds somehow
        assert 0 <= i < raster.width
        assert 0 <= j < raster.height

        # return a series with labels so we can unpack neatly into two dataframe columns
        return pd.Series(index=("raster_i", "raster_j"), data=[i, j])

    return cell_indicies_of_split_geometry


def raster_lookup(df: pd.DataFrame, fname: str, band_number: int = 1) -> pd.Series:
    """
    For each split geometry, lookup the relevant raster value. Cell indicies
    must have been previously calculated and stored as "raster_i" and "raster_j".

    Args:
        df (pd.DataFrame): Table of features, each with cell indicies pertaining
            to relevant raster pixel. Indicies must be stored under columns with
            names referenced by fields.RASTER_I and fields.RASTER_J
        fname (str): Filename of raster file to read data from
        band_number (int): Which band of the raster file to read

    Returns:
        pd.Series: Series of raster values, with same row indexing as df.
    """

    with rasterio.open(fname) as dataset:

        band_data: np.ndarray = dataset.read(band_number)

        # set non-positive values to NaN
        band_data[band_data < 1e-6] = np.nan

        # 2D numpy indexing is j, i (i.e. row, column)
        return pd.Series(index=df.index, data=band_data[df["raster_j"], df["raster_i"]])
