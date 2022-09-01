import pytest as pt
from Controller import Controller
import numpy as np

class TestClassModel:

    con = Controller("/home/schmidbauer/Downloads/data/PDI4sg")
    
class Test_init(TestClassModel):
    def setup(self):
        self.delays_filename = "/home/schmidbauer/Downloads/data/PDI4sg/01_Toluenez20_c_PDI_c_530_tol_delays.txt"
        self.spectra_filename = "/home/schmidbauer/Downloads/data/PDI4sg/01_Toluenez20_c_PDI_c_530_tol_spectra.txt"
        self.lambdas_filename = "/home/schmidbauer/Downloads/data/PDI4sg/01_Toluenez20_c_PDI_c_530_tol_lambda.txt"
    
    def test_type(self):
        assert [type(self.con.delays_filename),
                type(self.con.spectra_filename),
                type(self.con.lambdas_filename)] == [str, str, str]
        
    def test_values_delays(self):
        assert self.con.delays_filename == self.delays_filename
        
    def test_values_spectra(self):
        assert self.con.spectra_filename == self.spectra_filename
        
    def test_values_lambdas(self):
        assert self.con.lambdas_filename == self.lambdas_filename
        
class Test_calcDAS(TestClassModel):
    def setup(self):
        tau = [[900000], [1.2, 160]]
        d_limits = [0.3, None]
        l_limits = [None, None]
        self.tau_fit, self.spec, self.res, D_fit = self.con.calcDAS(tau, d_limits,
                                                        l_limits)
        
    def test_type(self):
        assert [type(self.tau_fit), type(self.spec),
                type(self.res)] == [np.ndarray, np.ndarray, np.ndarray]
        
    def test_shape(self):
        assert [len(self.tau_fit), self.spec.shape,
                self.res.shape] == [3, (367, 107), (367, 107)]
        
# class Test_calcSAS(TestClassModel):
#     def setup(self):
#         k = [0.83, 0.025, 0.0000011]
#         C_0 = []
#         d_limits = [0.3, None]
#         l_limits = [None, None]
#         model = 1
#         self.k_fit, self.spec, self.res = self.con.calcSAS(k, C_0, d_limits,
#                                                            l_limits, model)
        
#     def test_shape(self):
#         assert [len(self.k_fit), self.spec.shape,
#                 self.res.shape] == [3, (366, 107), (366, 107)]
        
#     def test_type(self):
#         assert [type(self.k_fit), type(self.spec),
#                 type(self.res)] == [np.ndarray, np.ndarray, np.ndarray]
        
# plot data   