"""
Stores TIFF format specific information
that tifftools doesn't quite format in a
useful way

-SCT June 2022
"""

from enum import Enum

class TIFFTAG(Enum):
    IMAGE_WIDTH         =   256
    IMAGE_LENGTH        =   257
    BITS_PER_SAMPLE     =   258
    COMPRESSION         =   259
    PHOTOMETRIC         =   262
    FILLORDER           =   266
    IMAGE_DESCRIPTION   =   270
    STRIP_OFFSET        =   273
    ORIENTATION         =   274
    SAMPLES_PER_PIXEL   =   277
    ROWS_PER_STRIP      =   278
    STRIP_BYTE_COUNTS   =   279
    XRESOLUTION         =   282
    YRESOLUTION         =   283
    PLANAR_CONFIGURATION=   284
    RESOLUTION_UNIT     =   296