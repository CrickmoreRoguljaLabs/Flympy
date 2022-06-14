from setuptools import setup, Extension
import setuptools
import logging
import os, re

try:
    import numpy
    import scipy # kind of silly to import scipy for just erfc but... whatever.
except ImportError as error:
    raise Exception("Numpy and scipy are not yet installed on this distribution. Set up numpy using command 'pip install <directory_containing_this_setup.py>' instead.")

HERE = os.path.abspath(os.path.dirname(__file__))

def _version() -> str:
    """ Parses _version.py to return a version string without executing the code """
    with open(os.path.join(HERE, "flympy", "core", "_version.py")) as f:
        match = re.search(r'version\s?=\s?\'([^\']+)', f.read())
        if match:
            return match.groups()[0].split('+')[0]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

setup (name = 'flympy',
       version = _version(),
       install_requires = [
           'numpy',
           'scipy',
       ],
       setup_requires = [
           'numpy',
           'scipy',
           'tifftools',
           'pylibtiff',
       ],
       extras_require = {
           'viz' : ['matplotlib','napari']
       },
       description = 'Python package for reading FLIMage! .flim files',
       # ext_modules = [flimreadermodule], PERHAPS TO BE IMPLEMENTED
       packages = setuptools.find_packages(),
       license='GPL-3',
       classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        ],
        author_email='thornquist@rockefeller.edu',
        author='Stephen Thornquist'
       )
    
try:
    import matplotlib.pyplot
except ImportError as error:
    logging.warning(f"{bcolors.WARNING}\nWARNING:\n\tInstalled without matplotlib. Plotting functionality may fail until those are installed.{bcolors.ENDC}")

try:
    import napari
except ImportError as error:
    logging.warning(f"{bcolors.WARNING}\nWARNING:\n\tInstalled without napari." +
    " All functionality should be present, but napari can provide a more pleasant" + 
    "experience for interacting with image data. Try to install it (ideally with pip)"+
    f" using the command 'pip install napari'. Has a tendency to break with conda.{bcolors.ENDC}")

try:
    import dask
except ImportError as error:
    logging.warning(f"{bcolors.WARNING}\nWARNING:\n\tInstalled without dask." +
    " Some napari plotting functionality will fail (anything relying on delayed " +
    f"evaluation. Install with conda or pip.){bcolors.ENDC}")