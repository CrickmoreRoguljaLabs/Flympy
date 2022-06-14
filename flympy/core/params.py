VERIFICATION_STR = "FLIMimage parameters" # Yes, I know it's a typo, there are tons in Ryohei's code..

import os
from re import I

HERE = os.path.abspath(os.path.dirname(__file__))

__all__ = [
    'AcquisitionParameters',
    'SPCParameters',
    'UncagingParameters',
    'MotorParameters',
]

class ParamClass():
    """
    Generic class with all functionality for types of parameters
    that can be extracted from .flim files.
    """

    PARAM_TYPE = None

    def __init__(self, description_string : str):
        if not isinstance(self.__class__.PARAM_TYPE, str):
            raise ValueError(
                "Must provide a string for the parameter class's definition "
                "to identify appropriate info in the flim file"
            )
        if not isinstance(description_string, str):
            raise ValueError(
                f"{self.__class__.__name__} class can only be initialized "
                "by a description string read out of a .tiff file or "
                "tiff-like file."
            )
        
        split = description_string.split("\r\n")
        # Check that this is the right data format.
        if not (split[0] == VERIFICATION_STR):
            raise ValueError(
                "FLIMage save format seems to have changed. "
                "Contact Ryohei and ask why the saved info no longer "
                f"begins with {VERIFICATION_STR}. If the only change is "
                f"in the value of this string, then go to {HERE} and "
                "change the string at the beginning of the file under "
                "the value VERIFICATION_STR."
            )

        # Looks for things that might store this type of PARAM's data
        viableVals = [
            substr
            for substr in split
            if (
                (len(substr.split(" = ")) == 2) # contains exactly one equality in the line
                and
                self.__class__.PARAM_TYPE in substr.split(" = ")[0] # it contains a PARAM_TYPE assignment
            )
        ]

        # Expects these parameters to be evaluatable Python expressions
        for assigned_val in viableVals:
            param, val = assigned_val.split(" = ")
            setattr(
                self,
                param.split(self.__class__.PARAM_TYPE)[-1],
                eval(val.split(';')[0])
            )

    def __repr__(self)->str:
        retstr = f"{self.__class__.__name__} : \n"
        for param, param_val in self.__dict__.items():
            retstr += f"\t{param} : {param_val}\n"
        return retstr


class AcquisitionParameters(ParamClass):
    """
    A class for storing information related to the acquisition
    of data -- e.g. microscope settings, what type of stimulation
    was used, etc.
    """
    PARAM_TYPE = 'State.Acq.'

class SPCParameters(ParamClass):
    """
    A class for storing information related to the photo counting
    data -- e.g. number of timing bins, what their precision is.
    """
    PARAM_TYPE = "State.Spc."

    @property
    def resolution(self):
        return getattr(self, "spcData.resolution")

    @property
    def nbins(self):
        return getattr(self, "spcData.n_dataPoint")
    

class UncagingParameters(ParamClass):

    PARAM_TYPE = "State.Uncaging."

class MotorParameters(ParamClass):

    PARAM_TYPE = "State.Motor."


        
