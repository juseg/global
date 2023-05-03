#!/usr/bin/python

"""Compute global mass balance from CHELSA climatology."""

import os.path
import dask.diagnostics
import dask.distributed
import numpy as np
import xarray as xr
import hyoga
import pypdd


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
        delayed.compute(scheduler='threads')

    # return file path
    return filepath


def write_massbalance(source='chelsa', offset=0):
    """Write global mass balance to disk, return file path."""

    # if file exists, return path
    filepath = f'processed/glopdd.smb.{source}.{offset*100:04d}.nc'
    if os.path.isfile(filepath):
        return filepath

    # open climatology (y>=40 chunks use too much memory on polaris)
    atm = xr.open_dataset(write_climatology(source=source), chunks={'y': 25})

    # apply temperature offset
    atm['temp'] -= offset

    # convert precipitation from kg m-2 month-1 to m a-1
    months = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    months = xr.DataArray(months, coords={'time': atm.time})
    atm['prec'] *= 0.365 / months

    # delay smb (use dask='parallelized' as pdd does not support dask arrays)
    pdd = pypdd.PDDModel()
    smb = xr.apply_ufunc(
        lambda t, p: pdd(t.transpose(2, 0, 1), p.transpose(2, 0, 1))['smb'],
        atm.temp, atm.prec, dask='parallelized', input_core_dims=[['time']]*2)

    # write output to disk
    delayed = smb.astype('f4').to_dataset(name='smb').to_netcdf(
        filepath, compute=False, encoding={'smb': {'zlib': True}})
    with dask.diagnostics.ProgressBar():
        print(f"Writing {source} - {offset:g} global mass balance...")
        delayed.compute(rerun_exceptions_locally=True)

    # return file path
    return filepath


def write_glacial_inception_threshold(source='chelsa'):

    # if file exists, return path
    filepath = f'processed/glopdd.git.{source}.nc'
    if os.path.isfile(filepath):
        return filepath

    # open (offset, x, y) surface mass balance array
    offset = xr.DataArray(range(10), dims=['offset'])
    paths = [write_massbalance(source=source, offset=dt) for dt in offset]
    smb = xr.open_mfdataset(paths, combine='nested', concat_dim=offset).smb
    print(smb.dtype)

    # compute glacial inception threshold
    git = (smb > 0).idxmax(dim='offset').where(smb[-1] > 0).rename('git')
    delayed = git.astype('f4').to_netcdf(
        filepath, compute=False, encoding={'git': {'zlib': True}})
    print(f"Writing {source} glaciation threshold...")
    delayed.compute(rerun_exceptions_locally=True)


if __name__ == '__main__':
    dask.distributed.Client()
    write_glacial_inception_threshold(source='chelsa')
