import datetime as dt
import logging
import os

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from icenet.plotting.utils import (
    show_img,
    get_plot_axes,
)

from EventGridProcessor.utils import downstream_process


@downstream_process
def output_metadata(ds: xr.Dataset,
                    output_config: dict,
                    *args,
                    **kwargs) -> dict:
    logging.info("Called output_metadata")
    return ds.attrs


@downstream_process
def output_forecast(ds: xr.Dataset,
                    output_config: dict,
                    *args,
                    output_directory: str = None,
                    **kwargs) -> dict:
    logging.info("Called output_forecast")

    for leadtime in ds.leadtime:
        pred_da = ds.sel(leadtime=leadtime).sic_mean
        plot_date = pd.to_datetime(pred_da.time.values) + dt.timedelta(int(leadtime))

        output_filename = os.path.join(output_directory, "{}.png".format(
            plot_date.strftime("%Y%m%d"),
        ))
        if os.path.exists(output_filename):
            logging.warning("Skipping {} as already exists".format(output_filename))
            continue

        ax = get_plot_axes(do_coastlines=True)

        cmap = cm.get_cmap("Blues_r")
        cmap.set_bad("dimgrey")
        bound_args = dict(cmap=cmap)

        im = show_img(ax, pred_da, **bound_args, vmax=1., do_coastlines=True)

        plt.colorbar(im, ax=ax)
        ax.set_title("{:04d}/{:02d}/{:02d}".format(plot_date.year,
                                                   plot_date.month,
                                                   plot_date.day))

        logging.info("Saving to {}".format(output_filename))
        plt.savefig(output_filename)
        plt.clf()
    return None


@downstream_process
def output_sie_growth(ds: xr.Dataset,
                      output_config: dict,
                      *args,
                      **kwargs) -> dict:
    logging.info("Called output_sie_growth")
    grid_area_size = output_config["grid_area_size"] if "grid_area_size" in output_config else 25
    threshold = output_config["threshold"] if "threshold" in output_config else 0.15

    fc_da = ds.sic_mean
    binary_fc_da = (fc_da > threshold).astype(int)

    sie_by_leadtime = binary_fc_da.sum(['xc', 'yc']) * grid_area_size ** 2

    return sie_by_leadtime.to_pandas().to_dict()


@downstream_process
def output_trend(ds: xr.Dataset,
                 output_config: dict,
                 *args,
                 **kwargs) -> dict:
    logging.info("Called output_trend")
    return dict(
      mean=ds.sic_mean.where(ds.sic_mean != 0, np.nan).mean(dim=["xc", "yc"]).to_pandas().to_dict(),
      stddev=ds.sic_stddev.where(ds.sic_stddev != 0, np.nan).mean(dim=["xc", "yc"]).to_pandas().to_dict()
    )



