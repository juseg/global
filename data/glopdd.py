#!/usr/bin/python
# Copyright (c) 2023-2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Compute glacial inception threshold from global climatologies."""

import argparse
import os.path
import warnings
import cdsapi
import dask.diagnostics
import dask.distributed
import netCDF4
import numpy as np
import scipy.special as sc
import xarray as xr


# Aggregate climatologies
# -----------------------

def aggregate_era5_avg(var='t2m', start=1981, end=2010):
    """Compute ERA5 multiyear monthly averages from monthly means."""

    # if file exists, return path
    filepath = \
        f'external/era5/clim/era5.{var}.mon.{start%100:d}{end%100:d}.avg.nc'
    if os.path.isfile(filepath):
        return filepath

    # compute monthly mean
    print(f"Computing {filepath} ...")
    paths = [
        download_era5_monthly(year, var=var) for year in range(start, end+1)]
    with xr.open_mfdataset(paths) as ds:
        ds.groupby('time.month').mean().to_netcdf(
            filepath, encoding={var: {'zlib': True}})

    # return file path
    return filepath


def aggregate_era5_std(freq='day', start=1981, end=2010):
    """Compute ERA5 multiyear monthly standard deviation from frequency."""

    # if file exists, return path
    filepath = (
        f'external/era5/clim/era5.t2m.{freq}.{start%100:d}{end%100:d}.std.nc')
    if os.path.isfile(filepath):
        return filepath

    # compute monthly standard deviation
    func = {'day': download_era5_daily, 'hour': download_era5_hourly}[freq]
    paths = [func(a, m) for m in range(1, 13) for a in range(start, end+1)]
    with dask.distributed.Client():
        with xr.open_mfdataset(paths, chunks={'latitude': 103}) as ds:
            print(f"Computing {filepath} ...")
            ds.groupby('time.month').std('time').to_netcdf(
                filepath, encoding={'t2m': {'zlib': True}})

    # return file path
    return filepath


# Download weather data
# ---------------------

def download_era5_daily(year, month):
    """Download ERA5 daily means for a single month."""

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


def download_era5_hourly(year, month):
    """Download ERA5 hourly means for a single month."""

    # if file exists, return path
    filepath = f'external/era5/hourly/era5.t2m.hour.{year:d}.{month:02d}.nc'
    if os.path.isfile(filepath):
        return filepath

    # else retrieve the file
    client = cdsapi.Client()
    client.retrieve(
        'reanalysis-era5-single-levels', {
            'product_type': 'reanalysis', 'format': 'netcdf',
            'variable': '2m_temperature',
            'year': f'{year:d}', 'month': f'{month:02d}',
            'day': [f'{i:02d}' for i in range(1, 32)],
            'time': [f'{i:02d}:00' for i in range(24)]},
        filepath)

    # return filepath
    return filepath


def download_era5_monthly(year, var='t2m'):
    """Download ERA5 monthly means for a single month."""

    # if file exists, return path
    filepath = f'external/era5/monthly/era5.{var}.mon.{year:d}.nc'
    if os.path.isfile(filepath):
        return filepath

    # variable name in CDS
    variable = {'t2m': '2m_temperature', 'tp': 'total_precipitation'}[var]

    # request download from CDS
    print(f"Downloading {filepath} ...")
    client = cdsapi.Client()
    client.retrieve('reanalysis-era5-single-levels-monthly-means', {
        'format': 'netcdf', 'month': [f'{i}' for i in range(1, 13)],
        'product_type': 'monthly_averaged_reanalysis', 'time': '00:00',
        'variable': variable, 'year': f'{year:d}'}, filepath)
    return filepath


# Open input climatologies
# ------------------------

def open_climate_tile(tile, freq='day', source='cw5e5'):
    """Open temp, prec, stdv climatology for a 30x30 degree tile."""

    # open climatology from hyoga cache directory
    prefix = os.path.join('~', '.cache', 'hyoga', source, 'clim', source)
    kwargs = {'chunks': {}, 'decode_coords': 'all'}
    temp = xr.open_dataarray(f'{prefix}.tas.mon.8110.avg.{tile}.nc', **kwargs)
    prec = xr.open_dataarray(f'{prefix}.pr.mon.8110.avg.{tile}.nc', **kwargs)

    # align coordinate names and values to cw5e5 data
    # FIXME do that in hyoga?
    if source == 'cera5':
        temp = temp.assign_coords(month=range(1, 13))
        prec = prec.assign_coords(month=range(1, 13))
        temp = temp.rename(x='lon', y='lat')
        prec = prec.rename(x='lon', y='lat')
        temp['lat'] = temp.lat.astype('f4')
        temp['lon'] = temp.lon.astype('f4')
        prec['lat'] = prec.lat.astype('f4')
        prec['lon'] = prec.lon.astype('f4')

    # convert units to degC and kg m-2 (per month)
    # FIXME assign cera5 units in hyoga, e.g.
    # temp = temp.assign_attrs(units='K') + 273.15
    # prec = prec.assign_attrs(units='kg m-2 s-1') / 24 / 3600 / months
    if source == 'cera5':
        assert 'units' not in temp.attrs
        assert 'units' not in prec.attrs
        temp = temp.assign_attrs(units='degC')
        prec = prec.assign_attrs(units='kg m-2')
    if source == 'cw5e5':
        assert temp.units == 'K'
        assert prec.units == 'kg m-2 s-1'
        months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        months = xr.DataArray(months, coords={'month': temp.month})
        temp = temp.assign_attrs(units='degC') - 273.15
        prec = prec.assign_attrs(units='kg m-2') * 3600 * 24 * months

    # open matching or interpolated standard deviation
    if source == 'cera5':
        stdv = open_interp_stdev(temp, freq=freq)
    else:
        stdv = xr.open_dataarray(
            f'{prefix}.tas.mon.8110.std.{tile}.nc', **kwargs)

    # return temperature, precipitation, standard deviation
    return temp, prec, stdv


def open_interp_stdev(temp, freq='day'):
    """Open interpolated ERA5 standard deviation."""

    # open era5 standard deviation
    filepath = aggregate_era5_std(freq='day')
    da = xr.open_dataarray(filepath, chunks={})

    # align coordinate names and values to cw5e5
    if freq == 'day':
        da = da.drop_vars('realization')
    else:
        da = da.rename(longitude='lon', latitude='lat')
        # da['lon'] = (da.lon + 180) % 360 - 180  # still needed?

    # interpolate (for larger grids use map_blocks as interp loads all chunks
    # overloading the memory https://github.com/pydata/xarray/issues/6799)
    # temp.map_blocks(lambda a: da.interp_like(temp), template=temp)
    stdv = da.interp_like(temp)

    # return interpolated standard deviation
    return stdv


# Compute main outputs
# --------------------

def compute_mass_balance(temp, prec, stdv):
    """Compute mass balance from climatology."""

    # number of days per months to convert precip and compute pdd
    # FIXME duplicates open_climate_tile, fix with interpolation
    months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    months = xr.DataArray(months, coords={'month': temp.month})

    # apply temperature offset
    temp = temp - xr.DataArray(range(12), coords=[range(12)], dims=['offset'])

    # compute normalized temp and snow accumulation in kg m-2
    norm = temp / (2**0.5*stdv)
    snow = prec * sc.erfc(norm) / 2

    # compute pdd and melt in kg m-2
    teff = (stdv/2**0.5) * (np.exp(-norm**2)/np.pi**0.5 + norm*sc.erfc(-norm))
    ddf = 3  # kg m-2 K-1 day-1 (~mm w.e. K-1 day-1)
    pdd = teff * months
    melt = ddf * pdd  # kg m-2

    # surface mass balance in kg m-2
    smb = (snow - melt).sum('month')
    smb = smb.transpose('offset', 'lat', 'lon')

    # return surface mass balance
    return smb


def compute_glacial_threshold(smb, source='chelsa'):
    """Compute glacial inception threshold from surface mass balance."""

    # use argmax because idxmax triggers rechunking
    git = (smb > 0).argmax(dim='offset').where(smb.isel(offset=-1) > 0)
    git = git.rename('git')
    git.attrs.update(long_name='glacial inception threshold', units='K')

    # return glacial inception threshold
    return git


# Main program
# ------------

def main():
    """Main program called during execution."""

    # parse command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-d', '--distributed', action='store_true', help='use distributed')
    parser.add_argument(
        '-o', '--overwrite', action='store_true', help='replace old files')
    parser.add_argument(
        '-f', '--freq', choices=['day', 'hour'], default='day')
    parser.add_argument(
        '-s', '--source', choices=['cera5', 'cw5e5'], default='cw5e5')
    parser.add_argument(
        '-t', '--tiles', action='extend', metavar='n30e000', nargs='*')
    args = parser.parse_args()

    # warn if netCDF >= 1.6.1 (https://github.com/pydata/xarray/issues/7079)
    if netCDF4.__version__ >= '1.6.1':
        warnings.warn(
            "Frequent HDF errors have been reported on netCDF4 >= 1.6.1, "
            "consider downgrading (xarray issues #7079, #3961).")

    # set up dask distributed client or local progress bar
    if args.distributed:
        dask.config.set({"distributed.comm.retry.count": 10})
        dask.config.set({"distributed.comm.timeouts.connect": '30'})
        dask.config.set({"distributed.comm.timeouts.tcp": '30'})
        Context = dask.distributed.Client
        options = {'n_workers': 4, 'threads_per_worker': 1}
    else:
        Context = dask.diagnostics.ProgressBar
        options = {}

    # create directories if missing
    # FIXME only create as needed
    os.makedirs('external/era5/clim', exist_ok=True)
    os.makedirs('external/era5/daily', exist_ok=True)
    os.makedirs('external/era5/hourly', exist_ok=True)
    os.makedirs('external/era5/monthly', exist_ok=True)
    os.makedirs('processed', exist_ok=True)

    # list climate tiles to process
    tiles = args.tiles or [
        f'{"n" if (lat >= 0) else "s"}{abs(lat):02d}'
        f'{"e" if (lon >= 0) else "w"}{abs(lon):03d}'
        for lat in range(-90, 90, 30) for lon in range(-180, 180, 30)]
    paths = [f'processed/glopdd.git.{args.source}.{tile}.nc' for tile in tiles]

    # start distributed client of progress bar
    with Context(**options):

        # for each tile and corresponding path
        for tile, filepath in zip(tiles, paths):

            # unless file exists
            if args.overwrite or os.path.isfile(filepath):

                # compute glacial threshold
                print(f"Computing {filepath} ...")
                temp, prec, stdv = open_climate_tile(
                    tile, freq=args.freq, source=args.source)
                smb = compute_mass_balance(temp, prec, stdv)
                git = compute_glacial_threshold(smb)
                git.astype('f4').to_netcdf(
                    filepath, encoding={'git': {'zlib': True}})

                # close files after computation (xarray #4131)
                for da in temp, prec, stdv:
                    da.close()

        # reopen and save global geotiff
        filepath = f'processed/glopdd.git.{args.source}.tif'
        print(f"Aggregating {filepath} ...")
        git = xr.open_mfdataset(paths).git
        git = git.rio.set_spatial_dims(x_dim='lon', y_dim='lat')
        git.rio.to_raster(filepath, compress='LZW', tiled=True)


if __name__ == '__main__':
    main()
