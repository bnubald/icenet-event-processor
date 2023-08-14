import logging


def output_forecast(da: xr.DataArray,
                    output_config: dict):
    logging.info("Called output_forecast")


def output_histogram(da: xr.DataArray,
                     output_config: dict):
    logging.info("Called output_histogram(")


def output_sie_growth(da: xr.DataArray,
                      output_config: dict):
    logging.info("Called output_sie_growth")


def output_trend(da: xr.DataArray,
                 output_config: dict):
    logging.info("Called output_forecast")


def list_assets(da: xr.DataArray,
                output_config: dict):
    logging.info("Called list_assets")
