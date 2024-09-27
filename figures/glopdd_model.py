#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD snow fraction methods."""

import numpy as np
import scipy.special as sc
import matplotlib.pyplot as plt


def melt_teff(temp, stdv=1):
    """Compute effective temperature for melt (melt = ddf * teff)."""
    if stdv == 0:
        return temp * (temp > 0)
    norm = temp / (2**0.5*stdv)
    return (stdv/2**0.5) * (np.exp(-norm**2)/np.pi**0.5 + norm*sc.erfc(-norm))


def snow_frac(temp, median=1, dispersion=1, method='linear'):
    """Compute fraction of precipitation that falls as snow."""

    # classic piecewise-linear method
    if method == 'linear':
        return (0.5-(temp-median)/(2*dispersion)).clip(0, 1)

    # creative error-function method
    if method == 'normal':
        return 0.5*sc.erfc((temp-median)/(2**0.5*dispersion))

    # invalid method
    raise ValueError(f"invalid method {method}")


def plot():
    """Make plot and return figure."""

    # initialize figure
    fig, axes = plt.subplots(
        figsize=(160/25.4, 80/25.4), ncols=2, gridspec_kw={
            'left': 0.1, 'bottom': 0.15, 'right': 0.95, 'top': 0.9})

    # for variable dispersion value
    for sigma in range(6):

        # plot snow fraction
        temp = np.linspace(-4, 6, 101)
        color = plt.get_cmap('Blues', 7)(sigma+1)
        frac = snow_frac(temp, dispersion=sigma, method='normal')
        axes[0].plot(temp, frac, color=color)

        # plot effective temperature for melt
        temp = np.linspace(-5, 5, 101)
        color = plt.get_cmap('Reds', 7)(sigma+1)
        axes[1].plot(temp, melt_teff(temp, sigma), color=color)

    # set axes properties
    axes[0].set_title('Fraction of precipitation that falls as snow')
    axes[0].set_xlabel('Surface air temperature (°C)')
    axes[0].set_ylabel('Snow fraction')
    axes[1].set_title('Effective temperature for melt')
    axes[1].set_xlabel('Effective temperature (°C)')
    axes[1].set_ylabel('Surface air temperature (°C)')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    fig = plot()
    fig.savefig(__file__[:-3], dpi='figure')


if __name__ == '__main__':
    main()
