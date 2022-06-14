import numpy as np

from .flimunits import FlimUnits

class FLIMParams():
    """
    A class for storing parameters related
    to fitting distributions of fluorescence
    lifetime or photon arrival data.

    Currently only implements mono and diexponentials.
    """
    
    def __init__(self, *args, color_channel : int = 0, units = FlimUnits.ARRIVAL_BINS, **params):
        
        self.exps = [arg for arg in args if isinstance(arg, Exp)]
        self.irf = next(isinstance(x, Irf) for x in args, None)
        self.color_channel = color_channel
        self.units = units

    @property
    def param_tuple(self)->tuple:
        """
        Returns a tuple for all of the parameters together so they can be
        passed into numerical solvers.
        """
        retlist = []
        for exp in self.exps:
            retlist += exp.param_list

        retlist += self.irf.param_list
        return tuple(retlist)    

    def convert_units(self, to_units : FlimUnits, flim_info = None):
        """
        Converts the units of all the parameters of this FLIMParams to
        the requested unit type of to_units.

        Arguments
        ---------

        to_units : FlimUnits

            A FlimUnits object specifying the units
            into which the FLIMParams will be transformed.

        flim_info : FlimInfo

            A FlimInfo object that is necessary to determine how
            to interchange between arrival_bins and real time units
            like picoseconds and nanoseconds. If converting between
            real time units, this parameter can be ignored

        Returns
        -------
        None
        """
        pass

    @property
    def ncomponents(self):
        if hasattr(self, 'exps'):
            return len(self.exps)
        return 0

class FLIMParameter():
    """
    Base class for the various types of parameters.

    Doesn't do anything special, just a useful organizer
    for shared behavior.
    """
    class_params = []

    def __init__(self, **params):
        # map and filter is cuter but this is more readable.
        for key, val in params.items():
            if key in self.__class__.class_params:
                setattr(self, key, val)
        for param in self.__class__.class_params:
            if not hasattr(self, param):
                setattr(self, param, None)
    
    @property
    def param_list(self)->list:
        return [getattr(self, attr) for attr in self.__class__.class_params]

    @property
    def param_tuple(self)->tuple:
        return tuple(self.param_list)

class Exp(FLIMParameter):
    """ Monoexponential parameter fits """
    class_params = ['tau', 'frac']

class Irf(FLIMParameter):
    """ Instrument response function """
    class_params = ['tau_g', 'tau_offset']

