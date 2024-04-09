#!/usr/bin/python
# Copyright (c) 2023, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Compute ERA5 monthly standard deviation of daily mean temperature."""

import os
import cdsapi
import xarray as xr
import dask.diagnostics


def compute_std(start=1981, end=2010):
    """Compute multiyear monthly standard deviation of daily means."""

    # if file exists, return path
    filepath = \
        f'external/era5/clim/era5.t2m.day.monstd.{start%100:d}{end%100:d}.nc'
    if os.path.isfile(filepath):
        return filepath

    # compute monthly standard deviation
    func = download_daily
    paths = [func(a, m) for m in range(1, 13) for a in range(start, end+1)]
    with dask.diagnostics.ProgressBar():
        with xr.open_mfdataset(paths) as ds:
            print(f"Computing {filepath} ...")
            ds.groupby('time.month').std('time').to_netcdf(
                filepath, encoding={'t2m': {'zlib': True}})

    # return file path
    return filepath


def download_daily(year, month):
    """Download daily means for a single month."""

    # if file exists, return path
    filepath = f'external/era5/daily/era5.t2m.day.{year:d}.{month:02d}.nc'
    if os.path.isfile(filepath):
        return filepath

    # query daily stats application
    client = cdsapi.Client()
    result = client.service('tool.toolbox.orchestrator.workflow', params={
        'realm': 'user-apps', 'project': 'app-c3s-daily-era5-statistics',
        'version': 'master', 'workflow_name': 'application', 'kwargs': {
            'dataset': 'reanalysis-era5-single-levels',
            'variable': '2m_temperature', 'statistic': 'daily_mean',
            'year': f'{year:d}', 'month': f'{month:02d}'}})

    # download the result
    print(f"Downloading {filepath} ...")
    client.download(result, [filepath])
    return filepath


if __name__ == "__main__":

    # if missing, create directory
    if not os.path.exists('external'):
        os.makedirs('external')

    # compute monthly standard deviation
    compute_std()
