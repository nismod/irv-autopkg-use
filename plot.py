import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import rioxarray
import xarray as xr

from utils import aqueduct_rp


def plot_aqueduct_flood_depth_distributions(raster_paths: list[str], title: str) -> None:
    """
    Plot distributions of non-zero flood depth for Aqueduct flood maps
    """

    if not isinstance(raster_paths, list):
        ValueError("first argument must be a list of file paths (to raster flood maps)")

    # sort our flood maps by return period (most frequent to least)
    raster_paths: list[str] = sorted(raster_paths, key=aqueduct_rp)

    # find the most extreme flood value
    most_extreme_map: np.ndarray = rioxarray.open_rasterio(raster_paths[-1]).squeeze().values
    max_depth_all_rp: float = most_extreme_map.max()

    # create a set of bins from 0 to this extreme value
    bins: np.ndarray = np.linspace(0, max_depth_all_rp, 20)

    # make a grid of axes to handle our (many) maps
    n = len(raster_paths)
    ncols = min([n, 3])
    nrows = (n // ncols) + (n % ncols)
    f, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(16, 2 + 3 * nrows), squeeze=False)

    # loop over rows and columns
    max_count = 0
    for row in range(nrows):
        for col in range(ncols):

            # bin the flood depth values and plot as histograms for each return period
            i = col + (row * ncols)
            if i < n:

                flood_map: str = raster_paths[i]
                return_period: int = aqueduct_rp(flood_map)

                ds = rioxarray.open_rasterio(flood_map)
                arr: np.ndarray = ds.squeeze().values
                arr = arr[arr > 0]

                counts, _, _ = axes[row, col].hist(arr, bins=bins, alpha=0.5, color='purple')
                axes[row, col].set_xlim(0, max_depth_all_rp)

                max_count = max([max(counts), max_count])

                axes[row, col].set_title(f"1 in {return_period} year flood", fontsize=10)
                axes[row, col].grid()

            # disable any axes we don't need
            else:
                axes[row, col].set_axis_off()

    # set y-axis limits the same for all histograms
    for row in range(nrows):
        for col in range(ncols):
            if col + (row * ncols) < n:
                axes[row, col].set_ylim(0, max_count * 1.1)

    # label the plot
    f.suptitle(title)
    f.supylabel("Frequency")
    f.supxlabel("Flood depth [meters]")

    plt.subplots_adjust(left=0.1, hspace=0.6, wspace=0.2)


def plot_flood_map(
    title: str,
    flood_map: xr.DataArray,
    network: gpd.GeoDataFrame = None,
    border: gpd.GeoDataFrame = None
) -> None:
    """Overplot a flood map raster with optional network and territory boundary"""

    ppi = 25.4  # pixels per inch
    f, ax = plt.subplots(figsize=(len(flood_map.x) / ppi, len(flood_map.y) / ppi))

    cmap = plt.get_cmap("viridis")
    cmap.set_under("white")
    img = flood_map.sel(dict(band=1)).plot.imshow(
        vmin=1E-3,
        vmax=flood_map.quantile(0.99),
        cmap=cmap,
        ax=ax,
        alpha=0.3
    )
    img.colorbar.ax.set_ylabel("Flood depth [meters]")

    if border is not None:
        border.plot(
            ax=ax,
            alpha=0.5,
            ls="--",
            color="black"
        )

    if network is not None:
        network.plot(
            ax=ax,
            column="layer",
            legend=True,
            alpha=1
        )

    ax.grid()
    ax.set_title(title)
    ax.set_xlabel("Longitude [deg]")
    ax.set_ylabel("Latitude [deg]")
