import logging

from icenet.results.threshold import threshold_exceeds

import numpy as np
import pandas as pd
import xarray as xr

from EventGridProcessor.utils import downstream_process, send_email


@downstream_process
def threshold_check(da: xr.DataArray,
                    check_config: dict,
                    *args,
                    **kwargs) -> object:
    """

    :param da:
    :param check_config:
    """
    results = list()

    for threshold in check_config["thresholds"]:
        threshold_years = []
        threshold_result = dict()

        months = [m for m in threshold['months'] if m in da["forecast_date.month"]]
        threshold_da = xr.combine_by_coords(
            [da.where(da["forecast_date.month"] == month, drop=True) for month in months]).sic_mean

        for year, year_region in check_config["history"].items():
            logging.debug("Checking against region from {} for {} over {} days".format(
                year_region, threshold["threshold"], threshold["threshold_held"]))

            result = threshold_exceeds(threshold_da,
                                       threshold["threshold"],
                                       threshold["threshold_held"],
                                       dimensions={k: slice(*v) for k, v in year_region.items()})

            logging.debug("Year {} has {}/{} violations of threshold".format(year, len(result),
                                                                             np.prod(threshold_da.shape)))

            if len(result) > 0:
                threshold_years.append(year)
                threshold_result[year] = result

        if len(threshold_result) > 0:
            results.append({year: len(arr)
                            for year, arr in threshold_result.items()})

        if len(threshold_years) > 0:
            start = pd.to_datetime(threshold_da.forecast_date.values[0]).strftime("%F")
            end = pd.to_datetime(threshold_da.forecast_date.values[-1]).strftime("%F")
            threshold_subject = "{} exceptions in forecast for {} - {}".format(
                len(threshold_years), start, end
            )
            threshold_message = f"""
    Forecast from {start} to {end} has regions that exceed the SIC threshold {threshold["threshold"]} for {threshold["threshold_held"]} in relation to previous years, where there were crossings.

    The years that compare are {threshold_years}. You might want to get yourself over to the IceNet dashboard for a look at the latest forecast.


    Thanks,

    The IceNet Team"""
            logging.info("We have message going to {}:\n{}".format(", ".join(threshold["email"]), threshold_message))
            send_email(threshold_subject,
                       threshold_message,
                       to_addr=threshold["email"])
            logging.info("Email sent, no further threshold checks will be carried out")
            break

    return results if len(results) > 0 else None
