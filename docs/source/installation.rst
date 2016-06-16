.. PyRate documentation master file, created by
   sphinx-quickstart on Thu Jun 16 18:45:46 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



Installation
============

Download the PyRate Python scripts:

- `$ git clone https://github.com/GeoscienceAustralia/PyRate.git`

Add the following lines to your ~/.bashrc file:

::

export PYRATEPATH="path_to_pyrate_here"
export PYTHONPATH="$PYRATEPATH:$PYTHONPATH"
 

Create the run environment with Anaconda
----------------------------------------
Anaconda is a Python distribution which easily installs and manages Python modules.

- Download the latest Linux 64-bit Python 2.7 installer from [here](https://www.continuum.io/downloads) to your home directory
- `$ bash Anaconda2-2.4.1-Linux-x86_64.sh` in your home directory
- Please accept all defaults. This will install anaconda in the `~/anaconda2` directory
- Select yes when asked about "adding to path"
- `$ source ~/.bashrc`
- `$ source activate anaconda2/`
- `$ conda install -c conda conda-env` (update the base Anaconda modules)
- `$ conda env create -f ~/PyRate/environment_simple.yml` (downloads the module set required by Pyrate)
- `$ source activate pyrate` (activates the above module set, consider adding the line to your .bashrc if it's the only environment you use)

Additional dependancies
-----------------------
<do we need openmpi-bin and mpich>




