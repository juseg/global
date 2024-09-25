#!/usr/bin/python
# Copyright (c) 2024, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot global PDD snow fraction methods."""

import numpy as np
import scipy.special as sc
import matplotlib.pyplot as plt


def snow_frac(temp, median=1, dispersion=1, method='linear'):
    """Compute fraction of precipitation that falls as snow."""

    # classic piecewise-linear method
    if method == 'linear':
        return (0.5-(temp-median)/(2*dispersion)).clip(0, 1)

    # creative error-function method
    if method == 'normal':
        return 0.5*sc.erfc((temp-median)/(2**0.5*dispersion))


def plot():
    """Make plot and return figure."""

    # initialize figure
    fig = plt.figure(figsize=(160/25.4, 80/25.4))
    ax = fig.add_axes([0.1, 0.15, 0.85, 0.75])

    # plot snow fraction
    temp = np.linspace(-4, 6, 101)
    for method, color in zip(['linear', 'normal'], ['tab:blue', 'tab:red']):
        frac = snow_frac(temp, method=method)
        half = snow_frac(temp, dispersion=0.5, method=method)
        double = snow_frac(temp, dispersion=2, method=method)
        ax.fill_between(temp, half, double, alpha=0.1, color=color)
        ax.plot(temp, frac, color=color, label=method)

    # set axes properties
    ax.set_title('Fraction of precipitation that falls as snow')
    ax.set_xlabel('Surface air temperature (°C)')
    ax.set_ylabel('Snow fraction')
    ax.legend()

    # return figure
    return fig


def main():
    """Main program called during execution."""
    fig = plot()
    fig.savefig(__file__[:-3], dpi='figure')


if __name__ == '__main__':
    main()
