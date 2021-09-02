# -*- coding: utf-8 -*-
import os
import re
from setuptools import setup, find_namespace_packages

# Get README and remove badges.
README = open('README.md').read()
README = re.sub('----.*marker', '----', README, flags=re.DOTALL)

DESCRIPTION = (
    """
    A convenient package to read GMT style cpt-files to matplotlib cmaps
    and mimic the dynamic scaling around a hinge point.
    """
)

KEYWORDS = [
    'cmap', 'colormap', 'matplotlib', 'pyplot',
    'GMT', 'generic mapping tools', 'makecpt', 'color pallet table'
]

setup(
    name='cmaptools',
    python_requires='>3.7.0',
    description=DESCRIPTION,
    long_description=README,
    author=[
        'Shahar Shani-Kadmiel'
    ],
    author_email='s.shanikadmiel@tudelft.nl',
    url='https://github.com/shaharkadmiel/cmaptools',
    download_url='https://github.com/shaharkadmiel/cmaptools.git',
    license='GNU General Public License v3 (GPLv3)',
    packages=find_namespace_packages(include=['cmaptools.*']),
    keywords=KEYWORDS,
    entry_points={},
    scripts=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'numpy',
        'matplotlib>=3.1.0'
    ],
    use_scm_version={
        'root': '.',
        'relative_to': __file__,
        'write_to': os.path.join('cmaptools', 'version.py'),
    },
    setup_requires=['setuptools_scm'],
)
