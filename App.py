import Controller
import numpy as np
import time as timee


# General models for any amount of species

# Model 1: A -> B -> C ... -> Z -> 0
# Model 2: A -> B -> C ... -> Z
# Model 3: A <=> B <=> C ... <=> Z -> 0
# Model 4: A <=> B <=> C ... <=> Z

# Specific models for a certain amount of species

# Model 5: A -> B -> C -> D; B -> D
# Model 6: A -> B -> C -> D -> E; B -> E
# Model 7: A -> B -> C -> D -> E; C -> E
# Model 8: A -> B -> C -> D -> E -> F; C -> F
# Model 9: A -> B; A -> D
# Model 10: A -> B ; B -> C ; B -> D

# Model "custom"


"""General Settings"""

# for an interactive plot overlay type "%matplotlib qt5" into the console
# to revert this type "%matplotlib inline"

# The path that contains the data files.
path = "/home/hackerman/Documents/fsTA Daten/c_PDI_t"
# Choose model: 0 for GLA, 1-10 for GTA and "custom" for a custom GTA model.
model = 0
# Lower and upper limits for the lambdas and delays.
# [None, None] to use all data.
l_limits = [350, 750]
d_limits = [0.2, 3400]
# Plotting the data: 0 doesn't show the plot of the original data,
# 3 shows the 3-in-1 plot or less subplots if wave and time are empty.
# 4 shows a 3D contour plot
orig = 0
# Plotting the fitted data: 0 doesn't calculate a fit, 1 outputs the fitted
# parameters, 2 shows the fitted 3-in-1 plot and 3 shows both.
# 4 shows the fitted 3D contour plot and the fitted parameters
fit = 2
# Plotting the residuals: 0 doesn't show the residuals, 1 and 2 create a 1D or
# 2D image and 3 shows both. Only works if fit is not 0.
resi = 0
# Algorithm used for the minimization of the tau values
opt_method = 'Nelder-Mead'
# Options:
# 'least_squares' 'Nelder-Mead' 'Powell' 'CG' 'BFGS' 'L-BFGS-B' 'TNC' 'COBYLA'
# 'SLSQP' 'trust-constr' 'ampgo' 'basinhopping'

# !'Newton-CG' 'dogleg' 'trust-ncg' 'trust-exact' 'trust-krylov' DO NOT WORK!

"""Settings for the Decay Associated Spectra"""

# The guessed decay constants which will be fitted.
tau_guess = [1,100]
# The decay constants which won't be fitted.
tau_fix = [900000]


"""Settings for the Species Associated Spectra"""

# The guessed decay constants which will be fitted.
tau_forwards = [1, 100, 9e5]
tau_backwards = []
# Lower and upper limits for the fitting of the decay constants.
tau_low_f = [0, 0, 8e5] # No bounds: tau_low = None
tau_low_b = []
tau_high_f = [3e2, 1e5, 10e5] # No bounds: tau_high = None
tau_high_b = []
# The inital concentrations. If empty all concentrations will be set to 0
# except the first one which will be 1. Def.: []
C_0 = []
# A custom matrix for the GTA which only works if model=="custom"
# and the dimension of the matrix is (n,n).
M = [[-0.5,  0  ,  0  , 0],
      [ 0.5 , -11,  0.   , 0],
      [ 0.0,  11, -9e5, 0],
      [0,    0,  9e5, 0]]
# M = np.genfromtxt("path")
# Algorithm used for solving the ivp
ivp_method = "BDF"
# Options:
# 'RK45' 'RK23' 'DOP853' 'Radau' 'BDF' 'LSODA'

"""Settings for the 3-in-1 plots of the original and the fitted data"""

# The wavelenghts whose plots (delays against absorption change) will be shown.
wave = [360, 560, 700]
# The delays whose plots (absorption change against delays) will be shown.
time = [1.2, 106, 4000]
# The lower and upper boundaries for the colorbar in the 2D plot.
# None for automatic determination.
v_min = None
v_max = None
# Determines how much contour lines will be shown in the 2D plot.
# High values will show more lines.
cont = 25
# The value by which the absorption data should be multiplied depending on the
# unit of measurement.
mul = 1000


"""Program"""

# Preamble
Controller = Controller.Controller(path)
wave.sort()
time.sort()
tau = list(np.concatenate([tau_forwards, tau_backwards]))
tau_low = list(np.concatenate([tau_low_f, tau_low_b]))
tau_high = list(np.concatenate([tau_high_f, tau_high_b]))
if model == "custom":
    M = np.array(M)
    ones = np.full(M.shape, 1)
    tau = np.divide(ones, M, out=np.zeros_like(M), where=M!=0)
    # tau = np.array(M)
    

# Calculation and Plotting

Controller.createOrigData(d_limits, l_limits, opt_method, ivp_method)

tau_fit = None

if model == 0:
    start = timee.time()
    if fit != 0:
        tau_fit, spec, res, D_fit, fit_report = Controller.calcDAS(
            [tau_fix, tau_guess], d_limits, l_limits, opt_method)
    print("runtime GLA:", timee.time()-start)
    if fit == 1:
        print(fit_report)
    elif fit == 2:
        Controller.plot3FittedData(wave, time, v_min, v_max, model, cont, mul)
    elif fit == 3:
        print(fit_report)
        Controller.plot3FittedData(wave, time, v_min, v_max, model, cont, mul)
    elif fit == 4:
        print(fit_report)
        Controller.plot3DFittedData(v_min, v_max, model, mul)
    
else:
    start = timee.time()
    if fit != 0:
        tau_fit, spec, res, D_fit,fit_report = Controller.calcSAS(tau, C_0, d_limits,
                                                       l_limits, model,
                                                       tau_low, tau_high,
                                                       opt_method, ivp_method)
        print("runtime GTA:", timee.time()-start)
    if fit == 1:
        if model != "custom":
            print(fit_report)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit),
                              where=tau_fit!=0)
            print("Custom Matrix - SAS: ", k_fit)
    elif fit == 2:
        Controller.plot3FittedData(wave, time, v_min, v_max, model, cont, mul)
    elif fit == 3:
        if model != "custom":
            print(fit_report)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit),
                              where=tau_fit!=0)
            print("Custom Matrix - SAS: ", k_fit)
        Controller.plot3FittedData(wave, time, v_min, v_max, model, cont, mul)
    elif fit == 4:
        if model != "custom":
            print(fit_report)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit),
                              where=tau_fit!=0)
            print("Custom Matrix - SAS: ", k_fit)
        Controller.plot3DFittedData(v_min, v_max, model, mul)
        
if fit != 0:
    if resi == 1:
        Controller.plot1Dresiduals(model)
    elif resi == 2:
        Controller.plot2Dresiduals(v_min, v_max, model, cont, mul)
    elif resi == 3:
        Controller.plot1Dresiduals(model)
        Controller.plot2Dresiduals(v_min, v_max, model, cont, mul)
        
if orig == 3:
    Controller.plot3OrigData(wave, time, v_min, v_max, d_limits, l_limits, 
                             cont, mul, opt_method, ivp_method)
if orig ==4:
    Controller.plot3DOrigData(v_min, v_max, d_limits, l_limits, 
                             mul, opt_method, ivp_method)

"""Custom plots"""
# If you want to create custom plots you can write the code here below.
# Keep in mind that you still have to choose the right values for model,
# d_limits, l_limits and C_0 for GTA in the settings at the beginning.
# The method you will want to use is Controller.plotCustom(...).

# custom describes which subplots will be plotted, read further in README
custom = "1+2"
# add is an addition to the title of the plot, the default is ""
add = "1+2"

# Controller.plotCustom(wave, time, v_min, v_max, model, cont, custom, mul, add)

# if fit != 0:
#     if model != 0:
#         Controller.plotKinetics(model)
#     Controller.plotDAS(model, tau_fit, mul)
