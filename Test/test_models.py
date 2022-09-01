import pytest as pt
from models import Models
import numpy as np


class Test_getK:
    def setup(self):
        ks = [0.83, 0.025, 0.0000011]
        self.mod = Models(ks)
        model = 1
        self.K, self.n = self.mod.getK(model)

    def test_values_K(self):
        test_values = np.array([[-8.3e-01,  0.0e+00,  0.0e+00],
                                [8.3e-01, -2.5e-02,  0.0e+00],
                                [0.0e+00,  2.5e-02, -1.1e-06]])
        assert self.K == pt.approx(test_values)

    def test_values_n(self):
        assert self.n == 3

    def test_type(self):
        types = [type(self.K), type(self.n)]
        test_types = [np.ndarray, int]
        assert types == test_types

    def test_shape_K(self):
        shapes = self.K.shape
        test_shapes = (3, 3)
        assert shapes == test_shapes
        
class Test_model1:
    def setup(self):
        ks = [1, 2, 5]
        self.mod = Models(ks)
        model = 1
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (3,3)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1,  0.0e+00,  0.0e+00], [1, -2,  0.0e+00],
                                [0.0e+00,  2, -5]])
        assert self.K == pt.approx(test_values)

class Test_model2:
    def setup(self):
        ks = [1, 2, 5]
        self.mod = Models(ks)
        model = 2
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (4,4)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 0.0, 0.0, 0.0],
                                [1, -2, 0.0, 0.0],
                                [0.0, 2, -5, 0.0],
                                [0.0, 0.0, 5, 0.0]])
        assert self.K == pt.approx(test_values)
        
class Test_model3:
    def setup(self):
        ks = [1, 2, 5, 9, 13]
        self.mod = Models(ks)
        model = 3
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (3,3)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 9, 0.0], [1, -11, 13],
                                [0.0, 2, -18]])
        assert self.K == pt.approx(test_values)
        
class Test_model4:
    def setup(self):
        ks = [1, 2, 5, 9, 13, 18]
        self.mod = Models(ks)
        model = 4
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (4,4)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 9, 0.0, 0.0],
                                [1, -11, 13, 0.0],
                                [0.0, 2, -18, 18],
                                [0.0, 0.0, 5, -18]])
        assert self.K == pt.approx(test_values)
        
class Test_model5:
    def setup(self):
        ks = [1, 2, 5, 9]
        self.mod = Models(ks)
        model = 5
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (4,4)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 0.0, 0.0, 0.0],
                                [1, -11, 0.0, 0.0],
                                [0.0, 2, -5, 0.0],
                                [0.0, 9, 5, 0.0]])
        assert self.K == pt.approx(test_values)

class Test_model6:
    def setup(self):
        ks = [1, 2, 5, 9, 13]
        self.mod = Models(ks)
        model = 6
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (5,5)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 0.0, 0.0, 0.0, 0.0],
                                [1, -15, 0.0, 0.0, 0.0],
                                [0.0, 2, -5, 0.0, 0.0],
                                [0.0, 0.0, 5, -9, 0.0],
                                [0.0, 13, 0.0, 9, 0.0]])
        assert self.K == pt.approx(test_values)
        
class Test_model7:
    def setup(self):
        ks = [1, 2, 5, 9, 13]
        self.mod = Models(ks)
        model = 7
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (5,5)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 0.0, 0.0, 0.0, 0.0],
                                [1, -2, 0.0, 0.0, 0.0],
                                [0.0, 2, -18, 0.0, 0.0],
                                [0.0, 0.0, 5, -9, 0.0],
                                [0.0, 0.0, 13, 9, 0.0]])
        print([list(item) for item in self.K])
        assert self.K == pt.approx(test_values)
        
class Test_model8:
    def setup(self):
        ks = [1, 2, 5, 9, 13, 18]
        self.mod = Models(ks)
        model = 8
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (6,6)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 0.0, 0.0, 0.0, 0.0, 0.0],
                                [1, -2, 0.0, 0.0, 0.0, 0.0],
                                [0.0, 2, -23, 0.0, 0.0, 0.0],
                                [0.0, 0.0, 5, -9, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 9, -13, 0.0],
                                [0.0, 0.0, 18, 0.0, 13, 0.0]])
        print([list(item) for item in self.K])
        assert self.K == pt.approx(test_values)
        
class Test_model9:
    def setup(self):
        ks = [1, 2]
        self.mod = Models(ks)
        model = 9
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (3,3)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-3, 0.0, 0.0], [1, 0.0, 0.0],
                                [2, 0.0, 0.0]])
        assert self.K == pt.approx(test_values)
        
class Test_model10:
    def setup(self):
        ks = [1, 2, 5]
        self.mod = Models(ks)
        model = 10
        self.K, self.n = self.mod.getK(model)
        
    def test_shape(self):
        assert self.K.shape == (4,4)
        
    def test_type(self):
        assert type(self.K) == np.ndarray
        
    def test_values(self):
        test_values = np.array([[-1, 0.0, 0.0, 0.0], [1, -7, 0.0, 0.0],
                                [0.0, 2, 0.0, 0.0], [0.0, 5, 0.0, 0.0]])
        assert self.K == pt.approx(test_values)