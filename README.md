# FLYMPY

Python code for basic .flim file functionality. Written to help Crickmore
lab members get started on basic analysis.

TODO: WRITE THIS! And implement:

-   Faster arbitrary frame access
-   Viewing frames functionality
-   ROIs
-   Registration

## Installing Flympy

First you'll need to clone this git repository into a location of your choice:

Open up a terminal (if you're on Windows, use `git bash`. If you're on
Linux or macOS, you can just use your standard `bash` or `zsh` terminal),
then navigate to wherever you want to copy the repository. For example:
(syntax is for `bash` shells)
```
cd ~/Documents/
mkdir FlimCode
cd FlimCode
```

then copy the repository with `git clone` and enter the folder:

```
git clone https://github.com/CrickmoreRoguljaLabs/Flympy
cd Flympy
```

Now if you're using something like `conda` to manage your environment,
make sure you're in the environment you want. For example, let's make a fresh environment:

```
conda create -n flym python=3.9 ipykernel numpy scipy libtiff
```

This will create an environment named `flym` that uses the `Python 3.9` interpreter.
The lines at the end tell it to allow it to work with `Jupyter` and to
install `numpy`, `scipy`, `tifftools`, and `pylibtiff`.

Now activate the environment so that you install stuff into it:

```
conda activate flym
```
or, if you're using a version of `conda` before version 4.6, you might need
to type

```
source activate flym
```

### Dependencies 

## Using FlymPy

