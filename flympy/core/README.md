# CORE UTILITIES

This submodule contains all the standard sort of code you might need to run.
It's a little awkwardly implemented -- I wasn't able to get `libtiff` to work
on `Python 3.9` so I used `tifftools`, but eventually switched over to `pylibtiff`.
So some things are done with `tifftools` and work well enough that I didn't see a
reason to reimplement them in `pylibtiff`. 

TODO:
-   Document `FlimReader` here
-   Swap `tifftools` for `pylibtiff`