"""
Math related to exponentials
used for computing values in
FLIM analysis

Functions
---------

chi_sq = px_chi_sq_exp(photon_arrivals, params)
    Returns the chi-squared value of a data array with the given params.

LL = px_log_likelihood_exp(photon_arrivals, params)
    returns the log-likelihood value of the dataset photon_arrivals
    under the parameter dictionary params

p = monoexponential_probability(photon_arrivals, tau, tau_g)
    Computes the probability of a photon_arrivals vector under the
    assumption of an exponential distribution with time constant tau
    and IRF gaussian width tau_g


SCT March 27 2021
"""

import numpy as np
from scipy import special

from .flimparams import FLIMParams, Exp, Irf

def px_chi_sq_exp(photon_arrivals : np.ndarray, flimparams : FLIMParams)->float:
    """ Returns the chi-squared statistic
    of a photon arrival data set, given
    parameters in params

    INPUTS
    ----------
    photon_arrival : np.ndarray

        Histogrammed arrival time of each photon. Element n is the count of photons arriving in histogram bin n.

    flimparams : FLIMParams
        
        A FLIMParams file with fit parameters.
    
    RETURN VALUES
    ----------
    Chi-squared : float 
        
        Chi-squared statistic of the histogram data under the model of the FLIMParams object
    """
    arrival_p = np.zeros(photon_arrivals.shape) # default, will be overwritten
    # params needed for all exponential models
    t_o = flimparams.irf.t_offset 
    tau_g = flimparams.irf.sigma
    num_exps = flimparams.ncomponents

    # iterate through components, adding up likelihood values
    for component in flimparams.exps:
        # get params for this component of the distribution

        arrival_p += component.frac * monoexponential_prob(np.arange(arrival_p.shape[0])-t_o,component.tau, tau_g)

    total_photons = np.sum(photon_arrivals)

    chi_sq = ((photon_arrivals - total_photons*arrival_p)**2)/arrival_p

    chi_sq[np.isinf(chi_sq)]=0

    return np.nansum(chi_sq)


def px_log_likelihood_exp(photon_arrivals, params):
    """ Returns the log-likelihood of a single pixel's distribution of arrival times under the presumption of the input params

    INPUTS
    ----------
    photon_arrival (1-dim ndarray):
        Histogrammed arrival time of each photon. Element n is the count of photons arriving in histogram bin n.

    params(dict). A params file like the others. Perhaps I'll make this a class
    
    RETURN VALUES
    ----------
    LL (double) -- log-likelihood of the photon
    """
    arrival_p = np.zeros(photon_arrivals.shape) # default, will be overwritten
    # params needed for all models
    t_o = params['T_O']
    tau_g = params['IRF']['PARAMS']['SIGMA']
    num_exps = params['NCOMPONENTS']

    # iterate through components, adding up likelihood values
    for component in range(num_exps):
        # get params for this component of the distribution
        comp_dict = params['EXPPARAMS'][component]
        tau_c = comp_dict['TAU']
        f = comp_dict['FRAC']

        arrival_p += f * monoexponential_prob(np.arange(arrival_p.shape[0])-t_o,tau_c, tau_g)

    return np.nansum(np.log(arrival_p)*photon_arrivals)

def monoexponential_prob(x_range : np.ndarray, tau : float, tau_g : float, cut_negatives : bool = True)->float:
    """ Takes in parameters of an exponential distribution
    convolved with a Gaussian, and outputs the probability
    of each element of x_range
    TODO: Switch from pointwise estimate to bin-size integral
    
    
    INPUTS
    ----------

    x_range (ndarray) -- The range of values to compute the probability of.

    tau (double) -- The decay parameter of the exponential

    tau_g (double) -- Width of the Gaussian with which the exponential
    distribution has been convolved


    RETURN VALUES
    ----------

    p (ndarray) -- Probability of each corresponding element of x_range
    """
    gauss_coeff = (1/(2*tau)) * np.exp((tau_g**2)/(2*(tau**2)))
    normalization = special.erfc( -(tau * x_range - tau_g**2)/ (np.sqrt(2)*tau_g*tau) )
    exp_dist = np.exp(-x_range/tau)

    if cut_negatives:
        p_out = gauss_coeff * normalization * exp_dist * (x_range > 0) # for above tau_o
    else:
        p_out = gauss_coeff * normalization * exp_dist
    
    return p_out