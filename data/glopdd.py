#!/usr/bin/python
# Copyright (c) 2023-2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Compute glacial inception threshold from global climatologies."""

import hashlib
import json
import os.path
import urllib.request
import warnings
import cdsapi
import dask.distributed
import netCDF4
import numpy as np
import scipy.special as sc
import xarray as xr
import hyoga


# Aggregate climatologies
# -----------------------

def aggregate_cera5(var='tas'):
    """Convert CHELSA-ERA5 geotiff to netcdf for efficient chunking."""
    # FIXME: eventually we may want to recompute the climatologies to fit
    # a custom subinterval of 1980-2019 instead of the default 1981-2010.

    # if file exists, return path
    filepath = f'external/cera5/clim/cera5.{var}.mon.8110.avg.nc'
    if os.path.isfile(filepath):
        return filepath

    # convert climatology
    hyoga.open.reprojected._open_climatology(
        source='chelsa', variable=var).to_dataset(name=var).to_netcdf(
            filepath, encoding={var: {'zlib': True}})

    # return file path
    return filepath


def aggregate_cw5e5(month, var='tas', func='avg', start=1981, end=2010):
    """Compute multiyear monthly aggregate from daily means."""

    # if file exists, return path
    filepath = (
        'external/cw5e5/clim/cw5e5.'
        f'{var}.day.{start%100:02d}{end%100:02d}.{func}.{month:02d}.nc')
    if os.path.isfile(filepath):
        return filepath

    # compute multiyear statistic (use preprocess to work around
    # precision errors, see https://github.com/pydata/xarray/issues/2217)
    # FIXME implement avg of monthly precip sum
    paths = [
        download_cw5e5_daily(year, month, var) for year in range(start, end+1)]
    print(f"Computing {filepath} ...")
    with xr.open_mfdataset(
            paths, chunks={'lat': 300, 'lon': 300},
            preprocess=lambda ds: ds.assign(
                lat=ds.lat.astype('f4'), lon=ds.lon.astype('f4'))) as ds:
        ds = getattr(ds, func.replace('avg', 'mean'))('time', keep_attrs=True)
        ds.to_netcdf(filepath, encoding={var: {'zlib': True}})

    # return file path
    return filepath


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
    func = download_era5_daily if freq == 'day' else download_era5_hourly
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

def download_cw5e5_daily(year, month, var='tas', res='300arcsec'):
    """Download daily means for a single month."""
    # NOTE: these files will be useful in hyoga
    # - chelsa/w5e5v1.0_obsclim_mask_30arcsec_global.nc
    # - chelsa/w5e5v1.0_obsclim_orog_30arcsec_global.nc

    # online url and local file path
    basename = \
        f'chelsa-w5e5_obsclim_{var}_{res}_global_daily_{year:d}{month:02d}'
    url = \
        f'https://files.isimip.org/ISIMIP3a/InputData/climate/atmosphere/' \
        f'obsclim/global/daily/historical/CHELSA-W5E5/{basename}'
    path = f'external/cw5e5/daily/{basename}'

    # download if missing
    for ext in ('.json', '.nc'):
        if not os.path.isfile(path+ext):
            print(f"Downloading {path+ext} ...")
            urllib.request.urlretrieve(url+ext, path+ext)

    # verify downloaded files
    print(f"Checking {path}.nc ...")
    with open(path+'.json', 'rb') as file:
        provided = json.load(file)['checksum']
    with open(path+'.nc', 'rb') as file:
        computed = hashlib.sha512(file.read()).hexdigest()
    assert computed == provided

    # return filepath
    return path + '.nc'


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


# Compute main outputs
# --------------------

def open_climatology(source='era5', freq='day', test=False):
    """Open temp, prec, stdv climatology on a consistent grid."""

    # open climatology (600x600 chunks raise memory warning on rigil)
    shortnames = ('t2m', 'tp') if source == 'era5' else ('tas', 'pr')
    if source == 'cw5e5':
        # FIXME combine cw5e5 data in preprocessing?
        time = xr.DataArray(data=range(1, 13), dims='time')
        temp, prec = (xr.open_mfdataset(
            f'external/{source}/clim/{source}.{var}.day.8110.avg.??.nc',
            concat_dim=time, combine='nested',
            chunks={'lon': 300, 'lat': 300})[var] for var in shortnames)
        stdv = xr.open_mfdataset(
            f'external/{source}/clim/{source}.tas.day.8110.std.??.nc',
            concat_dim=time, combine='nested',
            chunks={'lon': 300, 'lat': 300}).tas
    else:
        temp, prec = (xr.open_dataset(
            f'external/{source}/clim/{source}.{var}.mon.8110.avg.nc',
            chunks={'x': 300, 'y': 300})[var] for var in shortnames)

    # homogenize coordinate names to cera5 data
    # FIXME default to era5 (month, longitude, latitude) or cw5e5 (lat, lon)
    if source == 'era5':
        temp = temp.rename(month='time', longitude='x', latitude='y')
        prec = prec.rename(month='time', longitude='x', latitude='y')
        temp['x'] = (temp.x + 180) % 360 - 180
        prec['x'] = (prec.x + 180) % 360 - 180
        temp = temp.drop('time')
        prec = prec.drop('time')
    elif source == 'cw5e5':
        temp = temp.rename(lon='x', lat='y')
        prec = prec.rename(lon='x', lat='y')
        stdv = stdv.rename(lon='x', lat='y')

    # crop a small region for a test
    if test:
        mask = (5 < temp.x) & (temp.x < 10) & (43 < temp.y) & (temp.y < 48)
        temp = temp.where(mask, drop=True)
        prec = prec.where(mask, drop=True)

    # FIXME this function has become a mess...
    if source == 'cw5e5':
        return temp, prec, stdv

    # load era5 standard deviation
    # FIXME also use cw5e5 standard deviation
    with xr.open_dataarray(
            f'external/era5/clim/era5.t2m.{freq}.8110.std.nc') as era5:
        if freq == 'day':
            era5 = era5.rename(month='time', lon='x', lat='y')
            era5 = era5.drop(['realization', 'time'])
        else:
            era5 = era5.rename(month='time', longitude='x', latitude='y')
            era5['x'] = (era5.x + 180) % 360 - 180
            era5 = era5.drop('time')

    # interpolate to temperature grid (interp loads all chunks by default
    # overloading the memory https://github.com/pydata/xarray/issues/6799)
    # FIXME: could perhaps use interp_like if coordinates are consistent?
    if source == 'era5':
        stdv = era5.chunk({'x': 300, 'y': 300})
    else:
        stdv = temp.map_blocks(
            lambda array: era5.interp(x=array.x, y=array.y), template=temp)

    # return temperature, precipitation, standard deviation
    return temp, prec, stdv


def open_climate_tile(tile, chunks=None, source='cw5e5'):
    """Open temp, prec, stdv climatology for a 30x30 degree tile.

    Chunks default to 1800x1800. Benchmarks on rigil, one tile, twelve offsets.
    When using 24 offsets instead, chunks should be half-sized, etc.

    - 1 workers, 1 threads, 3600x3600: 84 secs -> global 101 min
    - 2 workers, 2 threads, 3600x3600: 53 secs
    - 4 workers, 4 threads, 3600x3600: 35 secs, mem warnings
    - 4 workers, 4 threads, 1800x1800: 32 secs
    - 8 workers, 8 threads, 1800x1800: 22 secs -> global 26 min
    - 8 workers, 8 threads, 1200x1200: 23 secs
    - 16 workers, 16 threads, 900x900: 24 secs, one tcp error
    - 8 workers, 24 threads, 900x900: 25 secs
    - 8 workers, 24 threads, 1200x1200: 31 secs
    """

    # open climatology from hyoga cache directory
    prefix = os.path.join('~', '.cache', 'hyoga', 'cw5e5', 'clim', 'cw5e5')
    chunks = chunks or {'lat': 1800, 'lon': 1800}
    temp = xr.open_mfdataset(
        f'{prefix}.tas.mon.8110.avg.{tile}.??.nc', chunks=chunks).tas
    prec = xr.open_mfdataset(
        f'{prefix}.pr.mon.8110.avg.{tile}.??.nc', chunks=chunks).pr
    stdv = xr.open_mfdataset(
        f'{prefix}.tas.mon.8110.std.{tile}.??.nc', chunks=chunks).tas

    # homogenize coordinate names to cw5e5 data
    # if source == 'cera5':
    #     temp = temp.rename(x='lon', y='lat')
    #     prec = prec.rename(x='lon', y='lat')
    #     stdv = stdv.rename(x='lon', y='lat')

    # load era5 standard deviation
    # if source == 'cera5':
    #     interp_era5_stdev()

    # return temperature, precipitation, standard deviation
    return temp, prec, stdv


def compute_mass_balance(temp, prec, stdv):
    """Compute mass balance from climatology."""

    # number of days per months to convert precip and compute pdd
    months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    months = xr.DataArray(months, coords={'month': temp.month})

    # convert temperature to degC
    if 'units' not in temp.attrs:
        temp = temp.assign_attrs(units='degC')  # CHELSA-ERA5
    elif temp.units == 'K':
        temp = temp.assign_attrs(units='degC') - 273.15
    else:
        raise ValueError(f'Unknown temperature units {temp.units}.')

    # convert precipitation to kg m-2
    if 'units' not in prec.attrs:
        prec = prec.assign_attrs(units='kg m-2')  # CHELSA-ERA5
    elif prec.units == 'kg m-2 s-1':
        # FIXME unit 'm' specific to ERA5 is a monthly average of daily totals
        prec = prec.assign_attrs(units='kg m-2') * 3600 * 24 * months
    elif prec.units == 'm':
        # FIXME unit 'm' specific to ERA5 is a monthly average of daily totals
        prec = prec.assign_attrs(units='kg m-2') * 1e3 * months
    else:
        raise ValueError(f'Unknown precipitation units {prec.units}.')

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
    git = (smb > 0).argmax(dim='offset').where(smb[-1] > 0).rename('git')
    git.attrs.update(long_name='glacial inception threshold', units='K')

    # return glacial inception threshold
    return git


# Main program
# ------------

def main(source='cw5e5'):
    """Main program called during execution."""

    # warn if netCDF >= 1.6.1 (https://github.com/pydata/xarray/issues/7079)
    if netCDF4.__version__ >= '1.6.1':
        warnings.warn(
            "Frequent HDF errors have been reported on netCDF4 >= 1.6.1, "
            "consider downgrading (xarray issues #7079, #3961).")

    # use dask distributed, retry on CommClosedError
    dask.config.set({"distributed.comm.retry.count": 10})
    dask.config.set({"distributed.comm.timeouts.connect": '30'})
    dask.config.set({"distributed.comm.timeouts.tcp": '30'})
    dask.distributed.Client(n_workers=8, threads_per_worker=1)

    # create directories if missing
    # FIXME only create as needed
    os.makedirs('external/era5/clim', exist_ok=True)
    os.makedirs('external/era5/daily', exist_ok=True)
    os.makedirs('external/era5/hourly', exist_ok=True)
    os.makedirs('external/era5/monthly', exist_ok=True)
    os.makedirs('processed', exist_ok=True)

    # for corner coordinates of each tile
    lats = range(-90, 90, 30)
    lons = range(-180, 180, 30)
    for (lat, lon) in zip(lats, lons):

        # get tile name from literal lat and lon
        llat = f'{"n" if (lat >= 0) else "s"}{abs(lat):02d}'
        llon = f'{"e" if (lon >= 0) else "w"}{abs(lon):03d}'
        tile = llat + llon

        # unless file exists
        filepath = f'processed/glopdd.git.{source}.{tile}.nc'
        if os.path.isfile(filepath):
            continue
        print(f"Computing {filepath} ...")

        # compute glacial threshold
        temp, prec, stdv = open_climate_tile(tile)
        smb = compute_mass_balance(temp, prec, stdv)
        git = compute_glacial_threshold(smb)
        git.astype('f4').to_netcdf(filepath, encoding={'git': {'zlib': True}})



if __name__ == '__main__':
    main()
