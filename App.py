import Controller
import numpy as np
import time as stopwatch


# General models for any amount of species

# Model 1: A -> B -> C ... -> Z -> 0
# Model 2: A -> B -> C ... -> Z

# Specific models for a certain amount of species

# Model 3: A -> B -> C -> D; B -> D
# Model 4: A -> B -> C -> D -> E; B -> E
# Model 5: A -> B -> C -> D -> E; C -> E
# Model 6: A -> B -> C -> D -> E -> F; C -> F
# Model 7: A -> B; A -> C
# Model 8: A -> B ; B -> C ; B -> D

# Model "custom matrix"

"""General Settings"""

# for an interactive plot overlay type "%matplotlib qt5" into the console
# to revert this type "%matplotlib inline"

# The directory that contains the data files.
# Must be a folder with three files ending with "delays.txt" "lambda.txt" "spectra.txt".
path = "/home/hackerman/Documents/fsTA Daten/c_PDI_t"
# Choose model: 0 for GLA, 1-8 for GTA and "custom matrix" for a custom GTA model.
model = "custom matrix"
# Lower and upper limits for the wavelengths and delays.
# [None, None] to use all data.
w_bounds = [350, 750]
d_bounds = [0.2, 3400]
# Plotting the data: 0 doesn't show the plot of the original data,
# 3 shows the 3-in-1 plot or less subplots if wavelength_slices and delay_slices are empty.
# 4 shows a 3D contour plot
orig = 0
# Plotting the fitted data: 0 doesn't calculate a fit, 1 outputs the fitted
# parameters, 2 shows the fitted 3-in-1 plot and 3 shows both.
# 4 shows the fitted 3D contour plot and the fitted parameters
fit = 1
# Plotting the residuals: 0 doesn't show the residuals, 1 and 2 create a 1D or
# 2D image and 3 shows both. Only works if fit is not 0.
resi = 0
# Algorithm used for the minimization of the tau values
opt_method = 'Nelder-Mead'
# Options:
# 'least_squares' 'Nelder-Mead' 'Powell' 'CG' 'BFGS' 'L-BFGS-B' 'TNC' 'COBYLA'
# 'SLSQP' 'trust-constr' 'ampgo' 'basinhopping'

# !'Newton-CG' 'dogleg' 'trust-ncg' 'trust-exact' 'trust-krylov' DO NOT WORK!

"""Settings for Global Lifetime Analysis"""

# The guessed lifetimes which will be fitted.
GLA_tau_guess = [1,100]
# The lifetimes which won't be fitted.
GLA_tau_fix = [900000]


"""Settings for Global Target Analysis"""

# The guessed lifetimes which will be fitted.
GTA_tau = [1, 100, 9e5]
# Lower and upper limits for the fitting of the lifetimes.
GTA_tau_lb = [0, 0, 8e5] # No bounds: GTA_tau_lb = None
GTA_tau_ub = [3e2, 1e5, 10e5] # No bounds: GTA_tau_ub = None
# The inital concentrations. If empty all concentrations will be set to 0
# except the first one which will be 1. Def.: []
c0 = []
# A custom matrix for the GTA which only works if model=="custom matrix"
# and the dimension of the matrix is (n,n).
M = [[-4001, 300, 0],
 [1, -320,  0],
 [4000, 20, 0]]
# M = np.genfromtxt("path")
# Algorithm used for solving the ivp
ivp_method = "BDF"
# Options:
# 'RK45' 'RK23' 'DOP853' 'Radau' 'BDF' 'LSODA'

"""Settings for the 3-in-1 plots of the original and the fitted data"""

# The wavelenght slices whose plots (delays against absorption change) will be shown.
# If not of interest set to []. Corresponding plots won't be shown.
wavelength_slices = [360, 560, 700]
# The delay slices whose plots (absorption change against delays) will be shown.
# If not of interest set to []. Corresponding plots won't be shown.
delay_slices = [1.2, 106, 4000]
# The lower and upper boundaries for the colorbar in the 2D plot.
# None for automatic determination.
v_min = None
v_max = None
# Determines how much contour lines will be shown in the 2D plot.
# High values will show more lines.
cont = 25
# The value by which the absorption data should be multiplied depending on the
# unit of measurement. If not of interest set to 1.
# Do NOT set to values <=0.
mul = 1000


"""Program"""

Controller = Controller.Controller(path)
wavelength_slices.sort()
delay_slices.sort()
if model == "custom matrix":
    M = np.array(M)
    ones = np.full(M.shape, 1)
    GTA_tau = np.divide(ones, M, out=np.zeros_like(M), where=M!=0)
    

# Calculation and Plotting

Controller.createOrigData(d_bounds, w_bounds, opt_method, ivp_method)

tau_fit = None

if mul <= 0:
    mul = 1

if model == 0:
    start = stopwatch.time()
    if fit != 0:
        tau_fit, spec, res, D_fit, fit_report = Controller.calcDAS(
            [GLA_tau_fix, GLA_tau_guess], d_bounds, w_bounds, opt_method)
    print("runtime GLA:", stopwatch.time()-start)
    if fit == 1:
        print(fit_report)
    elif fit == 2:
        Controller.plot3FittedData(wavelength_slices, delay_slices, v_min, v_max, model, cont, mul)
    elif fit == 3:
        print(fit_report)
        Controller.plot3FittedData(wavelength_slices, delay_slices, v_min, v_max, model, cont, mul)
    elif fit == 4:
        print(fit_report)
        Controller.plot3DFittedData(v_min, v_max, model, mul)
    
else:
    start = stopwatch.time()
    if fit != 0:
        tau_fit, spec, res, D_fit,fit_report = Controller.calcSAS(GTA_tau, c0, d_bounds,
                                                       w_bounds, model,
                                                       GTA_tau_lb, GTA_tau_ub,
                                                       opt_method, ivp_method)
        print("runtime GTA:", stopwatch.time()-start)
    if fit == 1:
        if model != "custom matrix":
            print(fit_report)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit),
                              where=tau_fit!=0)
            print("Custom Matrix - GTA: ", k_fit)
    elif fit == 2:
        Controller.plot3FittedData(wavelength_slices, delay_slices, v_min, v_max, model, cont, mul)
    elif fit == 3:
        if model != "custom matrix":
            print(fit_report)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit),
                              where=tau_fit!=0)
            print("Custom Matrix - GTA: ", k_fit)
        Controller.plot3FittedData(wavelength_slices, delay_slices, v_min, v_max, model, cont, mul)
    elif fit == 4:
        if model != "custom matrix":
            print(fit_report)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit),
                              where=tau_fit!=0)
            print("Custom Matrix - GTA: ", k_fit)
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
    Controller.plot3OrigData(wavelength_slices, delay_slices, v_min, v_max, d_bounds, w_bounds, 
                             cont, mul, opt_method, ivp_method)
if orig ==4:
    Controller.plot3DOrigData(v_min, v_max, d_bounds, w_bounds, 
                             mul, opt_method, ivp_method)

"""Custom plots"""
# If you want to create custom plots you can write the code here below.
# Keep in mind that you still have to choose the right values for model,
# d_bounds, w_bounds and c0 for GTA in the settings at the beginning.
# The method you will want to use is Controller.plotCustom(...).

# custom describes which subplots will be plotted, read further in README
custom = "1+2"
# add is an addition to the title of the plot, the default is ""
add = "1+2"

# Controller.plotCustom(wavelength_slices, delay_slices, v_min, v_max, model, cont, custom, mul, add)

# if fit != 0:
#     if model != 0:
#         Controller.plotKinetics(model)
#     Controller.plotDAS(model, tau_fit, mul)
