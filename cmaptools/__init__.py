# -*- coding: utf-8 -*-
"""
cmaptools
=========
A convenient package to read GMT style cpt-files to matplotlib cmaps and
mimic the dynamic scaling around a hinge point.

:author:
    Shahar Shani-Kadmiel (s.shanikadmiel@tudelft.nl)

:copyright:
    Shahar Shani-Kadmiel (s.shanikadmiel@tudelft.nl)

:license:
    This code is distributed under the terms of the
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from __future__ import absolute_import, print_function, division

import os
import numpy as np
from matplotlib.colors import (
    Colormap, LinearSegmentedColormap, ListedColormap, hsv_to_rgb,
    Normalize, DivergingNorm
)
from matplotlib.colorbar import ColorbarBase
import matplotlib.pyplot as plt

import re

from .gmtcolors import GMT_COLOR_NAMES


class DynamicColormap(Colormap):
    """
    Colormap object with a dynamic hinge point.
    """
    def __init__(self, cmap):
        """
        Make a colormap dynamic with respect to a hinge point.

        Dynamic colormaps are stretched to the ``[vmin, vmax]`` range,
        by separately scaling the lower part of the colormap
        (v < ``hinge``) and the upper part (v > ``hinge``).

        For instance, a colormap with v range `[-1, 1]` and hinge at
        `0` with `min_color` at `-1`, `hinge_color` and the ``hinge``,
        and `max_color` at `1`, can be dynamically scaled to
        ``[-10, 5]`` with `min_color` at `-10`, `hinge_color` and the
        ``hinge``, and `max_color` at `5`::

            <|min_color-----------hinge_color-----------max_color|>
            -1                         0                         1
                                        \
                                         \
                                          \
                                           \
            <|min_color-----------------hinge_color-----max_color|>
            -10                              0                   5

        See Also
        --------
        DynamicColormap.set_range
            Scale the colormap to a new range, keeping, or overriding
            the hinge point.
        """
        self.monochrome = False
        Colormap.__init__(self, cmap.name, cmap.N)
        try:
            self.values = cmap.values
        except AttributeError:
            self.values = np.linspace(-1, 1, self.N)
        self._vmin = self.values[0]
        try:
            self._hinge = cmap.hinge
        except AttributeError:
            self._hinge = 0
        self._vmax = self.values[-1]
        try:
            self.colors = cmap.colors
        except AttributeError:
            self.colors = cmap(self.values)

        self.set_range(self.vmin, self.vmax, self.hinge)

        self._lut = cmap._lut
        self._isinit = True
        self._set_extremes()

    @property
    def vmin(self):
        return self._vmin

    @property
    def hinge(self):
        return self._hinge

    @property
    def vmax(self):
        return self._vmax

    @property
    def norm(self):
        return DivergingNorm(
            vmin=self.vmin, vcenter=self.hinge, vmax=self.vmax
        )

    def set_range(self, vmin=None, vmax=None, hinge=None):
        """
        Set the range of the colormap to ``[vmin, vmax]`` around a hinge
        point. This range and hinge are used by the DynamicColormap.norm
        property.
        """
        self._vmin = vmin if vmin is not None else self.vmin
        self._hinge = hinge if hinge is not None else self.hinge
        self._vmax = vmax if vmax is not None else self.vmax

    def _resample(self, lutsize):
        """
        Return a new color map with ``lutsize`` entries.
        """
        colors = self(np.linspace(0, 1, lutsize))
        return ListedColormap(colors, name=self.name)

    def reversed(self, name=None):
        """
        Make a reversed instance of the Colormap.

        Parameters
        ----------
        name : str, optional
            The name for the reversed colormap. If it's None the
            name will be the name of the parent colormap + '_r'.

        Returns
        -------
        ListedColormap
            A reversed instance of the colormap.
        """
        if name is None:
            name = self.name + "_r"

        colors_r = list(reversed(self.colors))
        return ListedColormap(colors_r, name=name, N=self.N)

    def preview(self, vmin=None, vmax=None, hinge=None):
        """
        Preview a colorbar representation of the colormap setting the
        range to ``[vmin, vmax]`` around a ``hinge`` value.
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(4, 1.5))
        fig.subplots_adjust(0, 0, 1, 1, hspace=3)
        fig.suptitle(self.name, y=1.2)

        ColorbarBase(ax1, self, orientation='horizontal')
        ax1.set_xlabel('no norm')

        ColorbarBase(ax2, self, orientation='horizontal', norm=self.norm)
        ax2.set_xlabel('original norm')

        self.set_range(vmin, vmax, hinge)
        ColorbarBase(ax3, self, orientation='horizontal', norm=self.norm)
        ax3.set_xlabel('new norm')


def _parse_color_segments(segments, name, hinge=0, colormodel='RGB', N=256):
    """
    A private function to parse color segments.

    Parameters
    ----------
    segments : list
        A list of segments following the GMT structure:

        `z0 color0  z1 color1`

        Where color is either a named color from the GMT color list like
        `black` or `r g b` or `r/g/b`.

    name : str, optional
        name of the returned cmap.

    hinge : float, optional
        Zero by default.

    colormodel : str, optional
        Assumed to be ``'RGB'`` by default.

    N : int, optional
        Number of entries in the look-up-table of the colormap.

    Returns
    -------
    cmap : Colormap
        Either a LinearSegmentedColormap if sequential or
        DynamicColormap if diverging around a ``hinge`` value.
    """
    x = []
    r = []
    g = []
    b = []
    for segment in segments:
        # parse the left side of each segment
        fields = re.split(r'\s+|[/]', segment)
        x.append(float(fields[0]))
        try:
            r.append(float(fields[1]))
            g.append(float(fields[2]))
            b.append(float(fields[3]))
            xi = 4
        except ValueError:
            r_, g_, b_ = GMT_COLOR_NAMES[fields[1]]
            r.append(float(r_))
            g.append(float(g_))
            b.append(float(b_))
            xi = 2

    # parse the right side of the last segment
    x.append(float(fields[xi]))

    try:
        r.append(float(fields[xi + 1]))
        g.append(float(fields[xi + 2]))
        b.append(float(fields[xi + 3]))
    except ValueError:
        r_, g_, b_ = GMT_COLOR_NAMES[fields[-1]]
        r.append(float(r_))
        g.append(float(g_))
        b.append(float(b_))

    x = np.array(x)
    r = np.array(r)
    g = np.array(g)
    b = np.array(b)

    if colormodel == "HSV":
        for i in range(r.shape[0]):
            # convert HSV to RGB
            rr, gg, bb = hsv_to_rgb(r[i] / 360., g[i], b[i])
            r[i] = rr
            g[i] = gg
            b[i] = bb
    elif colormodel == "RGB":
        r /= 255.
        g /= 255.
        b /= 255.
    else:
        raise ValueError('Color model `{}` not understood'.format(colormodel))

    if hinge is not None and x[0] < hinge < x[-1]:
        cmap_type = 'dynamic'
        norm = DivergingNorm(vmin=x[0], vcenter=hinge, vmax=x[-1])
        hinge_index = np.abs(x - hinge).argmin()
    else:
        cmap_type = 'normal'
        hinge = None
        norm = Normalize(vmin=x[0], vmax=x[-1])

    xNorm = norm(x)
    red = []
    blue = []
    green = []
    for i in range(xNorm.size):
        # avoid interpolation across the hinge
        try:
            if i == (hinge_index):
                red.append([xNorm[i], r[i - 1], r[i]])
                green.append([xNorm[i], g[i - 1], g[i]])
                blue.append([xNorm[i], b[i - 1], b[i]])
        except UnboundLocalError:
            pass

        red.append([xNorm[i], r[i], r[i]])
        green.append([xNorm[i], g[i], g[i]])
        blue.append([xNorm[i], b[i], b[i]])

    # return colormap
    cdict = dict(red=red, green=green, blue=blue)
    cmap = LinearSegmentedColormap(name=name, segmentdata=cdict, N=N)
    cmap.values = x
    cmap.colors = list(zip(r, g, b))
    cmap.hinge = hinge
    cmap._init()

    if cmap_type == 'dynamic':
        return DynamicColormap(cmap)
    else:
        return cmap


def readcpt(cptfile, name=None, hinge=0, override_hinge=False, N=256):
    """
    Read a GMT color map from a cpt file

    Parameters
    ----------
    cptfile : str or open file-like object
        Path (relative or absolute) to .cpt file

    name : str, optional
        name for color map. If not provided, the file name will be used.

    hinge, float, optional
         If a ``hinge`` attribute is found in the header it is used.
         Otherwise, it is assumed to be ``0``. To override the specified
         hinge attribute in the header, set ``override_hinge=True``.
    """
    # generate cmap name
    if name is None:
        name = os.path.basename(cptfile).split('.')[0]

    with open(cptfile, 'r') as cptfile:
        # assume RGB color model
        colormodel = "RGB"

        # read the lines into memory
        segments = []
        for line in cptfile:
            line = line.strip()

            # skip empty lines
            if not line:
                continue

            # update color model assumption to HSV if needed
            if "HSV" in line:
                colormodel = "HSV"
                continue

            # if not None look for hinge
            if not override_hinge and "HINGE" in line:
                hinge = float(line.split("=")[-1])
                continue

            # skip other comments
            if line.startswith('#'):
                continue

            # skip BFN info
            if line.startswith(("B", "F", "N")):
                continue

            segments.append(line)

    return _parse_color_segments(segments, name, hinge, colormodel, N)


def joincmap(cmap1, cmap2, N=256):
    """
    Join two colormaps and return one dynamic colormap.
    """
    if isinstance(cmap1, str):
        cmap1 = plt.get_cmap(cmap1)

    if isinstance(cmap2, str):
        cmap2 = plt.get_cmap(cmap2)

    cmap = ListedColormap(
        np.vstack(
            (cmap1(np.linspace(0, 1, N // 2)),
             cmap2(np.linspace(0, 1, N // 2)))
        ), '->'.join((cmap1.name, cmap2.name)), N
    )

    cmap._init()

    cmap.values = np.linspace(-1, 1, N)
    cmap.hinge = 0
    return DynamicColormap(cmap)


__version__ = '1'
