# -*- coding: utf-8 -*-
"""
Created on Tuesday, Sep 13, 2016
Author: Bjorn Stevens (bjorn.stevens@mpimet.mpg.de)
"""
#

Rd      = 287.05
Rv      = 461.50
cpd     = 1004.
cpv     = 1864.
cpl     = 4184.
cpi     = 2108.
lv0     = 2500.8e3
lf0     = 333.7e3
gravity = 9.8076
eps     = Rv/Rd -1.

import numpy as np

def eslf(T, formula="goff-gratch", ice_phase=False):
    """ Returns the saturation vapour pressure [hPa] over liquid given 
	the temperature.  Temperatures can be in Celsius or Kelvin.
	Formulas supported are
	  - Goff-Gratch (1994 Smithsonian Tables) is the default
	  - Sonntag (1994) 
	  - Flatau
	  - Magnus Tetens (MT)
	>>> eslf(273.15)
	6.112
    """
    x = np.asarray(T)
    if formula == "flatau":
        if np.min(x) > 100:
          x = x-273.16
        x[x < -80.] = -80.
        c_es= np.asarray([0.6105851e+03, 0.4440316e+02, 0.1430341e+01, 0.2641412e-01,
                           0.2995057e-03,0.2031998e-05,0.6936113e-08,0.2564861e-11,-0.3704404e-13])
        es = np.polyval(c_es[::-1],x)/100.
    elif formula == "magnus":
        if np.min(x) > 100:
          x = x-273.15
        es = 6.112*np.exp((17.62*x)/(243.12+x))
    elif formula == "sonntag":
        if np.max(x) < 100:
            x = x+273.15
        xx = -6096.9385/x + 16.635794 - 2.711193e-2*x + 1.673952e-5*x*x + 2.433502 * np.log(x)
        es = np.exp(xx)

    elif formula =='goff-gratch':
        if np.max(x) < 100:
            x = x+273.15
        x1 = 273.16/x
        x2 = 373.16/x
        xi = np.log10(   6.1071) - 9.09718*(x1 - 1) - 3.56654*np.log10(x1) + 0.876793*(1 - 1./x1) 
        xl = np.log10(1013.246 ) - 7.90298*(x2 - 1) + 5.02808*np.log10(x2) - 1.3816e-7*(10**(11.344*(1.-1./x2)) - 1.0) 
        + 8.1328e-3 * (10**(-3.49149*(x2-1)) - 1.0)

        el =10**xl
        if ice_phase:
            ei =10**xi
            es = np.where(x>=273.15,el,ei)
        else:
            es = el
    return(es)
   
def latent_enthalpy(Tx, ice_phase=False):
#   """ Returns the formation enthlapy [J/g] incorporating the fusion enthalphy
#   whenever the temperature is below freezing.  Input temperature can be in 
#   deg Celcius or Kelvin
#   >>> latent_enthalpy(273.15)
#   2500.8e3
#   """
    import numpy as np

    x = np.asarray(Tx)
    if np.max(x) < 100:
        x = x+273.15
    Lvap = lv0 + (cpv-cpl)*(x-273.15)
    Lsub = lf0 + (cpl-cpi)*(x-273.15) + Lvap
    if ice_phase:
        L = np.where(x>=273.15,Lvap,Lsub)
    else:
        L = Lvap
    return (L)
    
def calc_mr_from_pp(e,p):
#   """ Calculates mixing ratio from the partial and total pressure
#   assuming both have same units and returns value in units of kg/kg.
#   """
	return (Rd/Rv)*e/(p-e)

def calc_sm_from_pp(e,p):                 
#   """ Calculates specific mass from the partial and total pressure
#   assuming both have same units and returns value in units of kg/kg.
#   """
    mr = calc_mr_from_pp(e,p)
    return (mr/(1 + mr))

def calc_pp_from_mr(p,mr):
#   """ Calculates partial pressure from mixing ratio and pressure, if mixing ratio
#   units are greater than 1 they are normalized by 1000.
#   """
    x = np.asarray(mr)
    if np.max(x) >= 1:
        x = x/1000.
    return(x*p/(x+Rd/Rv))

def calc_mse(T,Q,Z):                  # moist static energy from temperature, mixing ratio and altitude

    import numpy as np
    lv  = latent_enthalpy(T)
    cp  = cpd + (cpv-cpd)*Q
    mse = cp*T + lv*Q + gravity*np.array(Z)
    return(mse)

def calc_dse(T,Q,Z):                  # dry static energy from temperature, mixing ratio and altitude

    import numpy as np
    cp  = cpd + (cpv-cpd)*Q
    dse = cp*T + gravity*np.array(Z)
    return(dse)

def q_sat(T,p) :
    return eps * (eslf(T,ice_phase=True)*100) / p


cpd = 1004 # J kg-1 K-1

def cp(q) :
    return cpd + (cpv-cpd)*q