"""
For ensuring FlimTraces carrying different types of data are not
accidentally combined on unequal terms
"""

from enum import Enum
from typing import Union

import numpy as np

MULTIHARP_BASE_RESOLUTION_IN_PICOSECONDS = 5
TIMEHARP_BASE_RESOLUTION_IN_PICOSECONDS = 200

## THIS IS BAD!
# TRYING TO COME UP WITH A BETTER WAY
# TO USE THE READ INFORMATION FROM THE
# FILE AND ALSO BE COMPATIBLE BETWEEN
# SIFFPY AND FLYMPY
#
# TODO!!!
try:
    import siffpy
    BASE_RESOLUTION_PICOSECONDS = 4*MULTIHARP_BASE_RESOLUTION_IN_PICOSECONDS
except ImportError:
    BASE_RESOLUTION_PICOSECONDS = TIMEHARP_BASE_RESOLUTION_IN_PICOSECONDS

class FlimUnits(Enum):
    PICOSECONDS = "picoseconds"
    NANOSECONDS = "nanoseconds"
    COUNTBINS = "countbins"
    UNKNOWN = "unknown"
    UNITLESS    = "unitless"

def convert_flimunits(in_array : Union[np.ndarray,float], from_units : FlimUnits, to_units : FlimUnits)->Union[np.ndarray,float]:
    """
    Converts an array or float `in_array` from one type of FLIMUnit to another.

    Ignores UNITLESS.
    """
    if not (isinstance(from_units, FlimUnits) and isinstance(to_units, FlimUnits)) :
        raise ValueError("Must provide valid FlimUnits to convert")

    if from_units == FlimUnits.UNITLESS:
        # unitless vals shouldn't be transformed
        return in_array

    if any( unit == FlimUnits.UNKNOWN for unit in [from_units, to_units]) and (not all( unit == FlimUnits.UNKNOWN for unit in [from_units, to_units] )):
        raise ValueError("Unable to convert FlimUnits of UNKNOWN type to any other.")
    
    if from_units is FlimUnits.COUNTBINS:
        if to_units is FlimUnits.PICOSECONDS:
            out = BASE_RESOLUTION_PICOSECONDS * in_array
        if to_units is FlimUnits.NANOSECONDS:
            out = (BASE_RESOLUTION_PICOSECONDS/1000.0) * in_array
    
    if from_units is FlimUnits.PICOSECONDS:
        if to_units is FlimUnits.COUNTBINS:
            out = in_array/BASE_RESOLUTION_PICOSECONDS
        if to_units is FlimUnits.NANOSECONDS:
            out = in_array/1000.0
    
    if from_units is FlimUnits.NANOSECONDS:
        if to_units is FlimUnits.PICOSECONDS:
            out = in_array*1000
        if to_units is FlimUnits.COUNTBINS:
            out = in_array*1000/BASE_RESOLUTION_PICOSECONDS
    return out