#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
cmaptools - A convenient package to read GMT style cpt-files to
matplotlib cmaps and mimic the dynamic scaling around a hinge point.

:copyright:
    Shahar Shani-Kadmiel (s.shanikadmiel@tudelft.nl)

:license:
    This code is distributed under the terms of the
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

import os
import sys
from glob import glob
from setuptools import find_namespace_packages

try:
    from numpy.distutils.core import setup
except ImportError:
    msg = ('No module named numpy. Please install numpy first, it is '
           'needed before installing cmaptools.')
    raise ImportError(msg)


SETUP_DIRECTORY = os.path.abspath('./')
name = 'cmaptools'

KEYWORDS = [
    'cmap', 'colormap', 'matplotlib', 'pyplot',
    'GMT', 'generic mapping tools', 'makecpt', 'color pallet table'
]

INSTALL_REQUIRES = [
    'numpy',
    'matplotlib',
]

ENTRY_POINTS = {
    'console_scripts': []
}

# get the package version from from the main __init__ file.
for line in open(os.path.join(SETUP_DIRECTORY, name, '__init__.py')):
    if '__version__' in line:
        package_version = line.strip().split('=')[-1]
        break


def setup_package():
    # setup package
    setup(
        name=name,
        version=package_version,
        description='cmaptools',
        long_description=('A convenient package to read GMT style cpt-files '
                          'to matplotlib cmaps and mimic the dynamic scaling '
                          'around a hinge point.'),
        author=['Shahar Shani-Kadmiel'],
        author_email='s.shanikadmiel@tudelft.nl',
        url='https://gitlab.com/shaharkadmiel/cmaptools',
        download_url='https://gitlab.com/shaharkadmiel/cmaptools.git',
        install_requires=INSTALL_REQUIRES,
        keywords=KEYWORDS,
        packages=find_namespace_packages(include=['cmaptools.*']),
        entry_points=ENTRY_POINTS,
        zip_safe=False,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: ' +
                'GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Visualization',
            'Operating System :: OS Independent'
        ],
    )


if __name__ == '__main__':
        setup_package()
