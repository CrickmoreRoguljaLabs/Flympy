"""
Functions for file I/O -- All code specific to .flim files

Operating under the presumption the format of .flim files will not change

-SCT June 2022
"""

from typing import Union, Iterable
import datetime

import numpy as np
import libtiff

from .tiffinfo import TIFFTAG
from .params import *
from .params import ParamClass

__all__ = [
    'FlimInfo',
    'FrameInfo',
    'read_params',
    'read_frame_info',
    'read_frame_intensity',
    'read_histogram',
    'read_frame_flim'
]

class FlimInfo():
    """ A class that stores imaging-session-wide info about the .flim file """
    def __init__(self, info_dict : dict):
        """ Expects a tifftools.read_tiff dictionary for info_dict """
        self.acquisition_parameters : AcquisitionParameters = read_params(info_dict['ifds'], AcquisitionParameters)
        self.spc_parameters : SPCParameters = read_params(info_dict['ifds'], SPCParameters)
        self.uncaging_parameters : UncagingParameters = read_params(info_dict['ifds'], UncagingParameters)
        self.motor_parameters : MotorParameters = read_params(info_dict['ifds'], MotorParameters)

    @property
    def volume(self)->int:
        """ Number of frames per volume """
        slices = self.acquisition_parameters.nSlices if self.acquisition_parameters.ZStack else 1
        n_channels = self.acquisition_parameters.nChannels
        return slices*n_channels

    @property
    def shape(self)->tuple[int]:
        return _array_shape(self)

    def __repr__(self)->str:
        retstr = "FlimInfo :"
        retstr += "\n\n" + self.acquisition_parameters.__repr__()
        retstr += "\n\n" + self.spc_parameters.__repr__()
        retstr += "\n\n" + self.uncaging_parameters.__repr__()
        retstr += "\n\n" + self.motor_parameters.__repr__()
        return retstr

class FrameInfo():
    """ A class that stores frame-by-frame info within a .flim file """

    def __init__(self, ifd : dict, frame_number : int = None):
        """ Expects the dictionary of IFD information output by tifftools for a single frame """
        
        if isinstance(frame_number, int):
            self.frame_number = frame_number
        
        tags = ifd['tags']
        
        for tag_type in TIFFTAG:
            if tag_type.value in tags:
                setattr(
                    self,
                    tag_type.name,
                    tags[tag_type.value]['data']    
                )

        # pulls all of the description string, splits ones that contain settable attributes
        description_string = tags[TIFFTAG.IMAGE_DESCRIPTION.value]['data'] # contains string representations of relevant info

        attributes = description_string.split("\r\n")
        if len(attributes) > 0:
            for attribute in attributes:
                if len(attribute.split(" = ")) == 2:
                    param, val = attribute.split(" = ")
                    setattr(
                        self,
                        param,
                        val.split(';')[0] # discard the semicolon
                    )

    @property
    def acquisition_time(self):
        if not hasattr(self, 'Acquired_Time'):
            raise AttributeError("No Acquired_Time found for this frame.")
        return datetime.datetime.strptime(self.Acquired_Time, '%Y-%m-%dT%H:%M:%S.%f')

    def __repr__(self)->str:
        retstr = "FrameInfo:\n\n"
        for attr_name, attr_value in self.__dict__.items():
            retstr+= "\t"
            retstr+= attr_name.lower().replace("_", " ") + " : "
            retstr += str(attr_value)
            retstr += "\n"
        return retstr


def read_params(ifd_list : list, paramclass : ParamClass) -> ParamClass:
    """
    A function which parses the first IFD of a .flim file
    and returns a populated ParamClass object
    containing the acquisition-wide parameters stored in
    the .flim file's initial header.

    Arguments
    ---------

    ifd_list : list

        Expects a list that is the output of tifftools.read_tiff()'s ifds key

    Returns
    -------

    ParamClass : AcquisitionParameters

        A set of collected acquisition parameters for easy access
    """
    first_IFD = ifd_list[0]

    # The IMAGE_DESCRIPTION tag contains a long string specifying many experimental details.
    description_string = first_IFD['tags'][TIFFTAG.IMAGE_DESCRIPTION.value]['data']
    return paramclass(description_string)

def read_frame_info(ifd_list : dict, frame_num : Union[int, Iterable])->FrameInfo:
    """ 
    Takes either an index for the frame whose info is requested
    or an iterable of indices (or iterable of iterables...)
    
    Preserves the shape of the input
    """
    if hasattr(frame_num, '__iter__'):
        return [read_frame_info(ifd_list, frame) for frame in frame_num]
    
    return FrameInfo(ifd_list[frame_num + 1], frame_number = frame_num)

def _array_shape(flim_info : FlimInfo)->tuple:
    """ Returns a tuple specifying the shape of each acquired image """
    slices = flim_info.acquisition_parameters.nSlices if flim_info.acquisition_parameters.ZStack else 1
    n_channels = flim_info.acquisition_parameters.nChannels
    xdim, ydim = flim_info.acquisition_parameters.pixelsPerLine, flim_info.acquisition_parameters.linesPerFrame
    histo_depth = getattr(flim_info.spc_parameters,"spcData.n_dataPoint")
    return (slices, n_channels, ydim, xdim, histo_depth)


def read_frame_intensity(tiff_arr : libtiff.TiffArray, flim_info : FlimInfo, frames : Union[int, Iterable])->np.ndarray:
    """
    Takes a TiffArray, the FlimInfo object that specifies acquisition info, and the indices of the frames
    desired and returns an array of the intensity values within each frame.
    """
    frame_shape = _array_shape(flim_info)

    # Messiness has to do with the fact that colors and slices are each stored as a separate frame
    # so "frame", as passed, is really a VOLUME.
    if not hasattr(frames, "__iter__"):
        #true_frames = list(range(frames*flim_info.volume,(frames+1)*flim_info.volume))
        #return np.array([tiff_arr[each_frame] for each_frame in true_frames]).reshape(frame_shape).sum(axis=-1)
        return tiff_arr[frames].reshape(frame_shape).sum(axis=-1)

    return np.array(
        [
            tiff_arr[frame].reshape(frame_shape).sum(axis=-1)
            for frame in frames
        ]
    )

    # return np.array(
    #     [
    #         np.array(
    #             [
    #                 tiff_arr[each_frame]
    #                 for each_frame in list(range(frame*flim_info.volume, (frame+1)*flim_info.volume))
    #             ]
    #         ).reshape(frame_shape).sum(axis=-1) for frame in frames
    #     ]
    # )

def read_histogram(tiff_arr : libtiff.TiffArray, flim_info : FlimInfo, frames : Union[int, Iterable], color : int)->np.ndarray:
    """
    Takes a TiffArray, the FlimInfo object that specifies acquisition info, and the indices of the frames
    desired and returns a 1d array corresponding to the number of photons in the requested frames in each
    arrival time bin.
    """
    frame_shape = _array_shape(flim_info)
    
    if not hasattr(frames, "__iter__"):
        return np.sum(tiff_arr[frames].reshape(frame_shape),axis=tuple([0,2,3]))[color,:]

    return np.array(
        [
            np.sum(
                tiff_arr[frame].reshape(frame_shape),
                axis=tuple([0,2,3]) # excludes color axis
            )[color,:]
        for frame in frames
        ]
    ).sum(axis=0)

def read_frame_flim(tiff_arr : libtiff.TiffArray, flim_info : FlimInfo, frames : Union[int, Iterable])->np.ndarray:
    """
    Simply returns the timepoints x slices x colors x ydim x xdim x tau numpy array reading the .tiff directly.

    Extremely large array in RAM. I advise against using this method for analyses and instead performing estimates
    using the histograms, parameter fits, and then computing a statistic of interest like fluorescence lifetime.
    """
    frame_shape = _array_shape(flim_info)
    if not hasattr(frames, "__iter__"):
        return tiff_arr[frames].reshape(frame_shape)

    return np.array([tiff_arr[frame].reshape(frame_shape)for frame in frames])