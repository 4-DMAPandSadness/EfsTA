import pytest as pt
from Model import Model
import numpy as np
from models import Models
import matplotlib.pyplot as plt
import DAS_natalia as das

class TestClassModel:

    delays_filename = "/home/schmidbauer/Downloads/data/PDI4sg/01_Toluenez20_c_PDI_c_530_tol_delays.txt"
    spectra_filename = "/home/schmidbauer/Downloads/data/PDI4sg/01_Toluenez20_c_PDI_c_530_tol_spectra.txt"
    lambdas_filename = "/home/schmidbauer/Downloads/data/PDI4sg/01_Toluenez20_c_PDI_c_530_tol_lambda.txt"
    d_limits = [0.3, None]
    l_limits = [None, None]


class Test_init(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )

    def test_type(self):
        types = [
            type(self.mod.delays),
            type(self.mod.spectra),
            type(self.mod.lambdas),
            type(self.mod.d_borders),
            type(self.mod.l_borders),
            type(self.mod.name),
        ]
        test_types = [np.ndarray, np.ndarray, np.ndarray, list, list, str]
        assert types == test_types

    def test_shape(self):
        shapes = [
            self.mod.delays.shape,
            self.mod.spectra.shape,
            self.mod.lambdas.shape,
            len(self.mod.d_borders),
            len(self.mod.l_borders),
            len(self.mod.name),
        ]
        test_shapes = [(107,), (367, 107), (367,), 2, 2, 33]
        assert shapes == test_shapes

    def test_values(self):
        values = [
            self.mod.delays[56],
            self.mod.spectra[45, 30],
            self.mod.lambdas[349],
            self.mod.d_borders[1],
            self.mod.l_borders[0],
            self.mod.name[10],
        ]
        test_values = [32.45, 0.04855014, 731.20184, 132, 0, 'z']
        assert values == pt.approx(test_values)


class Test_genE_tau(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        tau = [1.2, 150, 900000]
        self.E_tau = self.mod.genE_tau(tau)

    def test_shape(self):
        assert self.E_tau.shape == (3, 107)

    def test_type(self):
        assert type(self.E_tau) == np.ndarray

    def test_values(self):
        assert self.E_tau[1, 45:50] == pt.approx(
            [0.93127562, 0.92416314, 0.91637159, 0.90785858, 0.89852567])


class Test_setInitialConcentrations(TestClassModel):
    def setup(self):
        model = 1
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        self.mod.n = 3
        C_0 = []
        self.C = self.mod.setInitialConcentrations(C_0)

    def test_shape(self):
        assert len(self.C) == 3

    def test_type(self):
        assert type(self.C) == np.ndarray

    def test_values(self):
        assert self.C == pt.approx([1, 0, 0])


class Test_calcdCdt(TestClassModel):
    def setup(self):
        model = 1
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        self.mod.K = np.array([[-8.3e-01,  0.0e+00,  0.0e+00],
                               [8.3e-01, -2.5e-02,  0.0e+00],
                               [0.0e+00,  2.5e-02, -1.1e-06]])
        self.C_0 = np.array([1, 0, 0])
        self.dCdt = self.mod.calcdCdt(self.mod.delays, self.C_0)

    def test_shape(self):
        shape = self.dCdt.shape
        assert shape == (3,)

    def test_type(self):
        assert type(self.dCdt) == np.ndarray

    def test_values(self):
        assert self.dCdt == pt.approx(np.array([-0.83, 0.83, 0]))


class Test_solveDiff(TestClassModel):
    def setup(self):
        model = 1
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        K = np.array([[-8.3e-01,  0.0e+00,  0.0e+00],
                      [8.3e-01, -2.5e-02,  0.0e+00],
                      [0.0e+00,  2.5e-02, -1.1e-06]])
        self.mod.C_0 = np.array([1, 0, 0])
        self.C_t = self.mod.solveDiff(K)

    def test_shape(self):
        assert self.C_t.shape == (3,107)

    def test_type(self):
        assert type(self.C_t) == np.ndarray
        
    def test_values(self):
        assert self.C_t[1,40:43] == pt.approx(np.array([0.87884498, 0.86658069,
                                                        0.85193718]))
        
class Test_getK(TestClassModel):
    def setup(self):
        model = 1
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        ks = [0.83, 0.025, 0.0000011]
        self.mod.mod = Models(ks)
        self.K, self.n = self.mod.getK(ks)
        
    def test_shape_K(self):
        assert self.K.shape == (3, 3)
        
    def test_type(self):
        assert [type(self.K), type(self.n)] == [np.ndarray, int]
        
    def test_values_K(self):
        test_values = np.array([[-0.83,  0.  ,  0.  ],
                               [ 0.83 , -0.025,  0.   ],
                               [ 0.0e+00,  2.5e-02, -1.1e-06]])
        assert self.K == pt.approx(test_values)
        
    def test_values_n(self):
        assert self.n == 3
        
class Test_getM(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        tau = [1.2, 150, 900000]
        self.M = self.mod.getM(tau)
    
    def test_shape(self):
        assert self.M.shape == (3,107)
        
    def test_type(self):
        assert type(self.M) == np.ndarray

    def test_values(self):
        assert self.M[1,78:80] == pt.approx(np.array([0.16679329, 0.1400905]))
        
class Test_getMlin(TestClassModel):
    def setup(self):
        model = "custom"
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        M = np.array([[-0.83,  0.  ,  0.  ],[ 0.83 , -0.025,  0.   ],
                      [ 0.0e+00,  2.5e-02, -1.1e-06]])
        self.M_lin = self.mod.getM_lin(M)
    
    def test_shape(self):
        assert len(self.M_lin) == 3
        
    def test_type(self):
        assert type(self.M_lin) == list
        
    def test_values(self):
        test_values = [0.83, 0.025, -0.0000011]
        assert self.M_lin == pt.approx(test_values)
        
class Test_regenM(TestClassModel):
    def setup(self):
        model = "custom"
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        ks = [0.83, 0.025, -0.0000011]
        self.mod.M_ones = np.array([[0, 0, 0],[1, 0, 0],[0, 1, 1]])
        self.M = self.mod.regenM(ks)
        
    def test_shape(self):
        assert self.M.shape == (3,3)
        
    def test_type(self):
        assert type(self.M) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-0.83,  0.  ,  0.  ],[ 0.83 , -0.025,  0.   ],
                      [ 0.0e+00,  2.5e-02, -1.1e-06]])
        assert self.M == pt.approx(test_values)
        
class Test_calcD_x(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        tau = [1.2, 150, 900000]
        self.mod.M = self.mod.getM(tau)
        self.D = self.mod.calcD_x(tau)
        
    def test_shape(self):
        assert self.D.shape == (367, 3)
        
    def test_type(self):
        assert type(self.D) == np.ndarray

    def test_values(self):
        assert self.D[2] == pt.approx(np.array([-0.01543421,  0.02202565,
                                                0.04493234]))
    
class Test_calcA_x(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        tau = [1.2, 150, 900000]
        self.mod.M = self.mod.getM(tau)
        self.A = self.mod.calcA_x(tau)
        
    def test_shape(self):
        assert self.A.shape == (367,107)
        
    def test_type(self):
       assert type(self.A) == np.ndarray
       
    def test_values(self):
        print(self.A[289,76:79])
        test_A = np.array([-0.00348274, -0.00323534, -0.00300282])
        assert self.A[289,76:79] == pt.approx(test_A)
        
class Test_getChiSquare(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        self.mod.x_fix = [900000]
        x_guess = [1.2, 106]
        self.Chi = self.mod.getChiSquare(x_guess)

    def test_type(self):
        assert type(self.Chi) == np.float64
        
    def test_values(self):
        print(self.Chi)
        assert self.Chi == 1.4805668823781104
        
class Test_findx_fit(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        x_fix = [900000]
        x_guess = [1.2, 106]
        self.x_fit = self.mod.findx_fit(x_fix, x_guess)
    
    def test_type(self):
        assert type(self.x_fit) == np.ndarray

    def test_shape(self):
        assert len(self.x_fit) == 3
        
    def test_values(self):
        assert self.x_fit == pt.approx([13, 588, 900000])
        
class Test_calcD_fit(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        self.mod.x_fit = [9.66481077e+00, 5.30173314e+02]
        self.mod.x_fix = [ 9.00000000e+05]
        self.D = self.mod.calcD_fit()
        
    def test_shape(self):
        assert self.D.shape == (367, 3)
        
    def test_type(self):
        assert type(self.D) == np.ndarray
        
    def test_values(self):
        test_values = [-0.004625308457487476, 0.026698520097349212,
                       0.038209502307311474]
        print(list(self.D[2]))
        assert self.D[2] == pt.approx(test_values)
        
class Test_calcA_fit(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        self.mod.x_fit = [9.66481077e+00, 5.30173314e+02]
        self.mod.x_fix = [ 9.00000000e+05]
        self.mod.D_fit = self.mod.calcD_fit()
        self.A = self.mod.calcA_fit()
    
    def test_shape(self):
        assert self.A.shape == (367, 107)
        
    def test_type(self):
        assert type(self.A) == np.ndarray
        
    def test_values(self):
        print(self.A[54, 98:101])
        test_values = [0.0170999, 0.01685909, 0.01666449]
        assert self.A[54, 98:101] == pt.approx(test_values)
        
class Test_calcResiduals(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        self.mod.x_fit = [9.66481077e+00, 5.30173314e+02]
        self.mod.x_fix = [ 9.00000000e+05]
        self.mod.D_fit = self.mod.calcD_fit()
        self.mod.calcA_fit()
        self.res = self.mod.calcResiduals()
        
    def test_shape(self):
        assert self.res.shape == (367, 107)
        
    def test_type(self):
        assert type(self.res) == np.ndarray
        
    def test_values(self):
        test_values = [-0.0010147558711799086, -0.0005034108805062922,
                       3.762536012926962e-05]
        print(list(self.res[54, 98:101]))
        assert self.res[54, 98:101] == pt.approx(test_values)
        
class Test_setv_min(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        data = np.array([[1.0,0.0002],[0.0,0.61900]])
        self.v_min = self.mod.setv_min(data, 1)
        
    def test_type(self):
        assert type(self.v_min) == np.float64
        
    def test_values(self):
        assert self.v_min == 0.0

class Test_setv_max(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        data = np.array([[1.0,0.0002],[0.0,0.61900]])
        self.v_max = self.mod.setv_max(data, 1)
        
    def test_type(self):
        assert type(self.v_max) == np.float64
        
    def test_values(self):
        assert self.v_max == 1.0
        
class Test_FindNearestIndex(TestClassModel):
    def setup(self):
        model = 0
        self.mod = Model(
            self.delays_filename,
            self.spectra_filename,
            self.lambdas_filename,
            self.d_limits,
            self.l_limits,
            model,
        )
        data = np.array([1.0 ,0.0002, 0.0, 0.61900])
        x = [0.00019]
        self.index = self.mod.findNearestIndex(x, data)
        
    def test_type(self):
        assert type(self.index) == list
        
    def test_values(self):
        assert self.index == [1]
        
# class Test_plot1(TestClassModel):
#     def setup(self):
#         model = 0
#         self.mod = Model(
#             self.delays_filename,
#             self.spectra_filename,
#             self.lambdas_filename,
#             self.d_limits,
#             self.l_limits,
#             model,
#         )
#         wave = [360, 560, 700] 
#         wave_index = self.mod.findNearestIndex(wave, self.mod.lambdas)
#         fig = plt.figure(
#             figsize=(2.5, 3), constrained_layout=False, dpi=100, frameon=True
#         )
#         self.grid = plt.GridSpec(1, 3, wspace=0, width_ratios=[1.0, 0, 0])
#         self.mod.plot1(self.grid, wave, wave_index, self.mod.spectra)
#         plt.suptitle(self.mod.name + "_test")
#         plt.close(fig)
        
#     def test_values(self):
#         ax1 = plt.subplot(self.grid[0, 0])
#         x_plot = ax1.get_xdata() # funkt nicht
#         assert x_plot in self.mod.spectra
    
# """ FÜR WEITERE PLOT FUNKTIONEN??? plot2 plot3 customplot plotdata"""