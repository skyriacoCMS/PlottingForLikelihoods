#!/usr/bin/env python                                                           

def fa3_new(fa3,fa2,fL1):


    cosW = 0.87681811112
    sinW = 0.48082221247
    mZ   = 91.2
    L1   = 1e4


    sigma_2 = (1.65684)^-2
    sigma_L1 = (-12100.42) ^-2
    sigma_4 = (2.55052) ^-2
    sigmaLZg = (-7613.351302119843)^-2


    #values taken from https://github.com/hroskes/HiggsAnalysis-CombinedLimit/blob/2236fdf2515b9de2fdae59fa408e8ce8c9faa288/python/SpinZeroStructure.py#L604-L609

    
    g_2 = sqrt(fa2/sigma_2)
    g_L1 = sqrt(fL1/sigma_L1)
    g_4 = sqrt(fa3/sigma_4)
    g_L1ZG = 2*cosW*sinW*(L1**2)/(cosW**2 - sinW**2)*( g_L1/(L1**2) - g_2/mZ**2)
    fa3_new = ( fa3**-1  + (g_L1Zg**2)*sigmaLZg/(sigma_4*g_4**2) )**(-1) 


    return fa3_new


