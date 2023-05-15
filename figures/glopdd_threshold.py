#!/usr/bin/python

"""Plot global PDD glacial inception threshold."""

import matplotlib.pyplot as plt
import xarray as xr

git = xr.open_dataset('../data/processed/glopdd.git.chelsa.nc').git
# git = git.sel(x=slice(-15, 45), y=slice(60, 30))
git.attrs.update(long_name='glacial inception threshold (°C)')
git.plot.imshow(cmap='Spectral')
plt.title('')
plt.savefig(__file__[:-3], dpi=300)
plt.show()
