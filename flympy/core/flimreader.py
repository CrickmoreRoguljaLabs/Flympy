"""
Modified version of Ryohei's original FlimReader.py object.

SCT
"""

import os
from typing import Iterable, Union
from datetime import datetime

import tifftools
import libtiff
import numpy as np

from .params import *
from .readfunctions import *
from ..math.flim import FLIMParams, FlimUnits

class FlimReader():
    """
    Wrap functions related to reading from a .flim file, a
    (irritatingly inefficient) format for storing FLIM data.

    It uses, more or less, the .tiff specification, creating large
    arrays of mostly zeros, effectively increasing image size by
    a factor of the number of arrival time bins. But it has the plus
    side of being supported by an extant file reader, so you don't
    have to write your own.
    """

    def __init__(self, filename : str = None):
        self.filename = filename

        # Parameters that should be read from the file
        # when opened
        self.tifffile = None
        self.tiff_info = None
        self.flim_info = None

        # if a file is provided, go ahead and open it
        if not (self.filename is None):
            self.open(self.filename)

    def open(self, filename : str = None):
        """
        Open the file at path filename. If a filename was provided
        at initialization, you can use that without passing an
        additional argument.

        Arguments
        ---------

        filename : string (optional)

            A valid path to a .flim file to open. If None is passed,
            or if this argument isn't provided, will use the filename
            provided upon initialization of the FlimReader.
        
        """
        if filename is None:
            if self.filename is None:
                raise ValueError("Must pass a valid file to `open`.")
            filename = self.filename

        if not os.path.splitext(filename)[-1] == ".flim":
            raise ValueError(f"Path provided must be to a .flim file. " + 
                f"Provided file was of extension {os.path.splitext(filename)[-1]}."
            )

        self.filename = filename # updates the filename to this file.
        self.tifffile = libtiff.TIFFfile(self.filename) # File I/O
        self.tiffarray = self.tifffile.get_tiff_array()
        self.tiff_info : dict = tifftools.read_tiff(filename) # Returns a dict that parses the file as a generic .tiff
        self.flim_info = FlimInfo(self.tiff_info) # Gets the .flim specific data

    ##### FILE I/O

    def get_intensity(self, frames : Union[int, Iterable] = None)->np.ndarray:
        """
        Returns an array whose values correspond to the pixelwise photon counts
        in the frames requested

        Arguments
        --------

        frames : int or iterable of ints

            The indices (STARTING FROM 0!) of the frames whose intensity you want.

        Returns
        -------

        intensity_array : np.ndarray

            An array of dimensions = (timepoints, slices, colors, y_size, x_size)        
        """
        if frames is None:
            frames = list(range(len(self.tiff_info['ifds'])-1))
        return read_frame_intensity(self.tiffarray, self.flim_info, frames) 

    def histogram_time_axis(self, units : FlimUnits = FlimUnits.PICOSECONDS, color : int = 0)->np.ndarray:
        """
        TODO PROPER DOCSTRING
        """
        if isinstance(units, str):
            units = FlimUnits(units.upper()) # lets you use a string instead

        resolution = self.flim_info.spc_parameters.resolution[color] # in picoseconds by default
        n_bins = self.flim_info.spc_parameters.nbins

        if units == FlimUnits.PICOSECONDS:
            return np.array([resolution * x for x in range(n_bins)])
        if units == FlimUnits.NANOSECONDS:
            return np.array([resolution * x / 1000 for x in range(n_bins)])
        else:
            raise ValueError("Unknown unit request provided")

    def get_histogram(self, color : int = 0, frames = None):
        """
        Returns a 1-d histogram of arrival times for the specified color channel.
        Defaults to using the first channel (green).

        TODO PROPER DOCSTRING
        """
        if frames is None:
            frames = list(range(len(self.tiff_info['ifds'])-1))
        return read_histogram(self.tiffarray, self.flim_info, frames, color) 

    def get_flim_array(self, frames = None):
        """
        Returns a timepoints by slices by color by ydim by xdim by tau
        numpy array. This is a large object to store in RAM (64 fold bigger
        than standard imaging data) and is an extremely inefficient tool to use.
        But it's here so you can do more custom analyses and because it's
        easy to implement. 

        I advise using the histogram, fitting, and lifetime methods instead,
        since they read single full frames at a time and then transform them
        rather than taking in the whole array at once. But because of the way
        .flim files store the data, it's tricky to rapidly compute statistics
        on photon arrival times in direct file I/O, so nothing will be super
        fast.

        Arguments
        ---------

        frames : int or iterable of ints

            The indices (STARTING FROM 0!) of the frames whose intensity you want.

        Returns
        -------

        flim_array : np.ndarray

            An array of dimensions = (timepoints, slices, colors, y_size, x_size, tau_depth)        
        """
        if frames is None:
            frames = list(range(len(self.tiff_info['ifds'])-1))
        return read_frame_flim(self.tiffarray, self.flim_info, frames) 

    def get_lifetime(self, FLIMParams : FLIMParams, frames = None):
        raise NotImplementedError()

    def get_metadata(self, frames : Union[int, Iterable] = None):
        """
        Takes either an index for the frame whose info is requested
        or an iterable of indices (or iterable of iterables...)
    
        Preserves the shape of the input, so if you pass a list
        of lists it will return a list of lists of FrameInfo objects.

        If no frames argument is provided, will return a flat list for
        all frames.

        Arguments
        ---------
        frames : int or iterable that contains ints at its lowest elements

            The indices (STARTING FROM 0!) of the frames whose metadata you
            want.

        Returns
        -------

        frame_infos : FrameInfo or iterable containing FrameInfos at its lowest elements

            FrameInfos contain per-frame     
        """
        if frames is None:
            frames = list(range(len(self.tiff_info['ifds'])-1))
        return read_frame_info(self.tiff_info['ifds'], frames)

    def get_datetime(self, frames : Union[int,Iterable] = None)->Union[datetime, list[datetime]]:
        """
        Returns the precise timestamps of each frame as a datetime object.
        For more information on using datetime objects, look up Python's
        datetime library.

        Arguments
        ---------

        frames : int or iterable whose lowest element is ints

            The indices of the frames whose timepoints you want. If
            None is provided (or if this argument is ignored), it will
            return the timepoints of ALL frames. Keep in mind that this
            might behave differently for multiple color channels!

        Returns
        -------

        times : datetime.datetime or a list containing datetimes

            A list of datetime objects corresponding to each requested
            frame's timestamps.
        """
        if frames is None:
            frames = list(range(len(self.tiff_info['ifds'])-1))
        
        frame_infos = read_frame_info(self.tiff_info['ifds'], frames)
        
        if not hasattr(frame_infos, '__iter__'):
            return frame_infos.acquisition_time
        
        return [this_frame.acquisition_time for this_frame in frame_infos]

    def get_time(self,
            frames : Union[int,Iterable] = None,
            zero_timepoint : datetime = None
        )->Union[np.ndarray,datetime]:
        """
        Returns a datetime if only one frame is requested. Otherwise returns
        an array of floats corresponding to the number of seconds since the
        provided argument `zero_timepoint`. If None is provided for zero_timepoint,
        defaults to using the first returned frame.

        Arguments
        ---------

        frames : int or iterable whose lowest element is ints

            The indices of the frames whose timepoints you want. If
            None is provided (or if this argument is ignored), it will
            return the timepoints of ALL frames. Keep in mind that this
            might behave differently for multiple color channels!

        zero_timepoint : datetime.datetime

            What time to consider "0". If no value is provided, defaults to
            using the first frame requested.

        Returns
        -------

        times : np.ndarray

            A 1-dimesional array containing the number of seconds since the zero timepoint
            of each frame requested.
        """
        if frames is None:
            frames = list(range(len(self.tiff_info['ifds'])-1))
        
        frame_infos = read_frame_info(self.tiff_info['ifds'], frames)
        
        if not hasattr(frame_infos, '__iter__'):
            return frame_infos.acquisition_time

        if zero_timepoint is None:
            zero_timepoint = frame_infos[0].acquisition_time
        
        return np.asarray(
            [
                (this_frame.acquisition_time - zero_timepoint).total_seconds()
                for this_frame in frame_infos
            ],
            dtype=float,
        )

    def __repr__(self)->str:
        retstr = "FlimReader object :\n\n"
        if not (self.filename is None):
            retstr += f"\tFilename : {self.filename}\n\n"
        
        if not (self.flim_info is None):
            retstr += f"\tInfo : {self.flim_info.__repr__()}\n\n"
        return retstr
