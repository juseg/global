#!/usr/bin/python
# Copyright (c) 2023-2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Compute global mass balance from CHELSA climatology."""

import os.path
import dask.diagnostics
import dask.distributed
import numpy as np
import scipy.special as sc
import xarray as xr
import hyoga


def write_climatology(source='chelsa'):
    """Write global climatology to disk, return file path."""

    # if file exists, return path
    filepath = f'processed/glopdd.atm.{source}.nc'
    if os.path.isfile(filepath):
        return filepath

    # if missing, create directory
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # open chelsa global climatology as a dataset
    # FIXME could store as original (f4?) and cache
    atm = xr.Dataset({
        'prec': hyoga.open.reprojected._open_climatology(
            source=source, variable='pr'),
        'temp': hyoga.open.reprojected._open_climatology(
            source=source, variable='tas')})

    # write to disk as a single file using threaded scheduler, as distributed
    # scheduler overloads memory, unless we chunk in time and space, but that
    # results in only one worker working at a time, probably because two
    # workers can't read the same geotiff file at the same time.
    delayed = atm.to_netcdf(filepath, compute=False, encoding={
        name: {'zlib': True} for name in atm})
    with dask.diagnostics.ProgressBar():
        print(f"Writing {source} global climatology...")
        delayed.compute()

    # return file path
    return filepath


def open_climatology(source='chelsa', freq='day'):
    """Write global mass balance to disk, return file path."""

    # load era5 standard deviation
    with xr.open_dataarray(
            f'external/era5/clim/era5.t2m.{freq}.monstd.8110.nc') as era5:
        if freq == 'day':
            era5 = era5.rename(month='time', lon='x', lat='y')
            era5 = era5.drop(['realization', 'time'])
        else:
            era5 = era5.rename(month='time', longitude='x', latitude='y')
            era5['x'] = (era5.x + 180) % 360 - 180
            era5 = era5.drop('time')

    # open climatology (600x600 chunks raise memory warning on rigil)
    atm = xr.open_dataset(
        write_climatology(source=source), chunks={'x': 300, 'y': 300})

    # interpolate to temperature grid (interp loads all chunks by default
    # overloading the memory https://github.com/pydata/xarray/issues/6799)
    stdv = atm.temp.map_blocks(
        lambda array: era5.interp(x=array.x, y=array.y), template=atm.temp)

    # return temperature, precipitation, standard deviation
    return atm.temp, atm.prec, stdv


def compute_mass_balance(temp, prec, stdv):
    """Compute mass balance from climatology."""

    # FIXME temporary fix
    atm = xr.Dataset({'prec': prec, 'temp': temp})

    # apply temperature offset
    offset = xr.DataArray(range(12), coords=[range(12)], dims=['offset'])

    # convert precipitation from kg m-2 month-1 to kg m-2 a-1
    months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    months = xr.DataArray(months, coords={'time': atm.time})

    # compute normalized temp and snow accumulation in kg m-2
    norm = (atm.temp-offset) / (2**0.5*stdv)
    snow = atm.prec * sc.erfc(norm) / 2

    # compute pdd and melt in kg m-2
    teff = (stdv/2**0.5) * (np.exp(-norm**2)/np.pi**0.5 + norm*sc.erfc(-norm))
    ddf = 3  # kg m-2 K-1 day-1 (~mm w.e. K-1 day-1)
    pdd = teff * months
    melt = ddf * pdd  # kg m-2

    # surface mass balance in kg m-2
    smb = (snow - melt).sum('time')
    smb = smb.transpose('offset', 'y', 'x')

    # return surface mass balance
    return smb


def compute_glacial_threshold(smb, source='chelsa'):
    """Compute glacial inception threshold from surface mass balance."""

    # use argmax because idxmax triggers rechunking
    git = (smb > 0).argmax(dim='offset').where(smb[-1] > 0).rename('git')
    git.attrs.update(long_name='glacial inception threshold', units='K')

    # return glacial inception threshold
    return git


def main(source='chelsa'):
    """Main program called during execution."""

    # use dask distributed
    dask.distributed.Client()

    # unless file exists
    filepath = f'processed/glopdd.git.{source}.nc'
    if not os.path.isfile(filepath):
        print(f"Writing {source} glacial inception threshold...")

        # compute glacial threshold
        temp, prec, stdv = open_climatology(source='chelsa')
        smb = compute_mass_balance(temp, prec, stdv)
        git = compute_glacial_threshold(smb)
        git.astype('f4').to_netcdf(filepath, encoding={'git': {'zlib': True}})

        # reopen and save tiled geotiff
        git = xr.open_dataarray(filepath, chunks={'y': 240})
        git.rio.to_raster(filepath[:-3]+'.tif', compress='LZW', tiled=True)


if __name__ == '__main__':
    main()
