import numpy as np
from lmfit import minimize, Parameters, fit_report
import scipy.integrate as scint
from models import Models


class Model:
    """
    The calculations follow a matrix reconstruction algorithm described by
    for example: The Journal of Chemical Physics 125.18 (2006), S. 184508
    """
    def __init__(self, data, model, opt_method, ivp_method):
        self.lambdas, self.delays, self.spectra = data
        self.model = model

    def gen_logic_vector(self, values, limits):
        lv = np.ones_like(values, dtype=bool)
        if limits[0] is not None:
            lv &= (values >= limits[0])
        if limits[1] is not None:
            lv &= (values <= limits[1])
        return lv

    def read_data(self, filename):
        values = np.genfromtxt(filename)
        if "eprspectra.txt" in filename:
            values = values.T
        data = values[self.l_borders[0]: self.l_borders[1],
                         self.d_borders[0]: self.d_borders[1]]
        return data

    def gen_e_tau(self, tau):
        E_tau = np.zeros(shape=(len(tau), len(self.delays)))
        for i in range(len(tau)):
            for j in range(len(self.delays)):
                E_tau[i][j] = -self.delays[j] / tau[i]
        E_tau = np.exp(E_tau)
        return E_tau

    def set_concentrations(self, C_0):
        if C_0 == []:
            C_0 = np.zeros(self.n)
            C_0[0] = 1
        self.C_0 = C_0
        return C_0

    def calc_dcdt(self, delays, C_0):
        return self.K @ C_0

    def solve_differential_equation(self, ivp_method):
        Z = scint.solve_ivp(self.calc_dcdt, [min(self.delays), max(self.delays)],
                            self.C_0, t_eval=self.delays, method=ivp_method)
        C_t = Z.get("y")
        return C_t

    def get_kinetic_matrix(self, tau):
        if (self.model == "custom model" or self.model == "custom matrix"):
            Tau = self.regenerate_m(tau)
            n = Tau.shape[0]
            ones = np.full(Tau.shape, 1)
            K = np.divide(ones, Tau, out=np.zeros_like(Tau), where=Tau != 0)
        else:
            ones = np.full(np.array(tau).shape, 1)
            k = np.divide(ones, tau, out=np.zeros_like(tau, dtype='float64'),
                          where=tau != 0)
            mod = Models(k)
            K, n = mod.get_k(self.model)
        self.K , self.n = K, n
        return K, n

    def get_m_linear(self, tau_guess):
        """
        Transforms the custom matrix for the SAS in a linear list and a matrix
        with 1 as placeholders for the corresponding values.
        Saves the matrix M_ones as an attribute.

        Parameters
        ----------
        tau_guess : list, np.array
            The custom matrix for the SAS with the decay constants tau.

        Returns
        -------
        tau : np.array
            An array with the decay constants tau of the custom matrix.

        """
        ones = np.full(tau_guess.shape, 1)
        k_guess = np.divide(ones, tau_guess, out=np.zeros_like(tau_guess),
                            where=tau_guess != 0)
        M_lin = []
        M_ones = np.zeros(k_guess.shape)
        for i in range(k_guess.shape[0]):
            for j in range(k_guess.shape[1]):
                if i == j and i != k_guess.shape[0] - 1:
                    k_guess[i][j] = 0
                if k_guess[i][j] != 0:
                    M_ones[i][j] = 1
                    M_lin.append(abs(k_guess[i][j]))
        tau = 1 / np.array(M_lin)
        self.M_ones = M_ones
        return tau

    def regenerate_m(self, tau_guess):
        """
        Regenerates the custom matrix with the fitted values found in x_guess.
        Replaces the 1 in the M_ones matrix with the corresponding values.

        Parameters
        ----------
        tau_guess : list, np.array
            The fitted decay constants for the SAS.

        Returns
        -------
        M : np.array
            The custom matrix for the SAS with the decay constants tau.

        """
        a = 0
        M = np.zeros(self.M_ones.shape)
        for i in range(self.M_ones.shape[0]):
            for j in range(self.M_ones.shape[1]):
                if self.M_ones[i][j] == 1:
                    M[i][j] = tau_guess[a]
                    if j != self.M_ones.shape[0] - 1:
                        M[j][j] -= tau_guess[a]
                    a += 1
        M[-1][-1] *= -1
        return M

    def set_tau_bounds(self, tau_low, tau_high, tau):
        """
        Responsible for the setting of the bounds to be used in the optimizing
        of the tau values.

        Parameters
        ----------
        tau_low : list
            A list which contains the lower bounds for the respective tau
            values.
        tau_high : list
            A list which contains the upper bounds for the respective tau
            values.
        tau : list, np.array
            An array containing the decay constants tau.

        Returns
        -------
        None.

        """
        if tau_low == []:
            tau_low = [None for i in tau]
        if tau_high == []:
            tau_high = [None for i in tau]
        for i in range(len(tau_low)):
            if tau_low[i] == 0 or tau_low[i] is None:
                tau_low[i] = 0.01
        self.tau_low = tau_low
        self.tau_high = tau_high

    def get_tau_bounds(self, tau):
        """
        This method outputs the bounds of the tau values for their optimizing.

        Parameters
        ----------
        tau : list, np.array
            An array containing the decay constants tau.

        Returns
        -------
        bounds : list
            A list of the bounds for each tau value.

        """
        if self.model == 0:
            bounds = [(0.01, None) for i in tau]
        else:
            bounds = list(zip(self.tau_low, self.tau_high))
        return bounds

    def get_m(self, tau, ivp_method):
        """
        Outputs the matrix which will be used in the matrix reconstruction
        algorithm to obtain the fitted spectra A_fit. For the DAS it is the
        matrix E_tau and for SAS it is the matrix C_t from the solved
        differential equation.

        Parameters
        ----------
        tau : list, np.array
            An array containing the decay constants tau.

        Returns
        -------
        M : np.array
            The matrix for the matrix reconstruction algorithm.

        """
        if self.model == 0:  # GLA
            M = self.gen_e_tau(tau)
            self.n = len(tau)
        else:  # GTA
            self.K, n = self.get_kinetic_matrix(tau)
            M = self.solve_differential_equation(ivp_method)
        return M

    def calc_d_tau(self, tau):
        """
        Calculates the matrix D_tau.

        Parameters
        ----------
        tau : list, np.array
            An array containing the decay constants tau.

        Returns
        -------
        D_tau : np.array
            The matrix D_tau.

        """
        AET = self.spectra @ self.M.T
        EET = self.M @ self.M.T
        EET_inv = np.linalg.inv(EET)
        D_tau = AET @ EET_inv
        return D_tau

    def calc_a_tau(self, tau):
        """
        Generates the reconstructed spectra matrix for the values of tau.

        Parameters
        ----------
        tau : list, np.array
            An array containing the decay constants tau.

        Returns
        -------
        A_tau : np.array
            The reconstructed data matrix for the values of tau.

        """
        D_tau = self.calc_d_tau(tau)
        A_tau = D_tau @ self.M
        return A_tau

    def get_difference(self, tau):
        """
        Calculates the measure of difference between the initial spectra
        matrix and the calculated A_tau matrix with given values for tau_guess
        and self.tau_fix, if DAS.

        Parameters
        ----------
        tau_guess : list, np.array
            A list of the variables tau_guess for the DAS or all tau values for
            the SAS.

        Returns
        -------
        get_differences : np.ndarray
            Difference between the modeled data and the experimental data.

        """
        tau_sum = list(tau.valuesdict().values())
        self.M = self.get_m(tau_sum)
        difference = self.calc_a_tau(tau_sum) - self.spectra
        return difference

    def findTau_fit(self, preparam, opt_method):
        """
        The function takes the variable tau_guess and optimizes their values,
        so that ChiSquare takes a minimal value. It outputs a list of the
        optimized tau values and the non-varied ones, if GLA was used.

        Parameters
        ----------
        tau_fix : list, np.array
            A list of the variables tau_fix for the DAS. Empty for SAS.
        tau_guess : list, np.array
            A list of the variables tau_guess for the DAS or all tau values for
            the SAS.
        opt_method: string
            The algorithm used by the optimization function.

        Returns
        -------
        tau_sum : list
            The fitted parameters tau_fit and the fixed values tau_fix combined.

        """
        params = Parameters()
        self.tau_fit = []
        bounds = self.get_tau_bounds(preparam)
        for i in range(len(preparam)):
            params.add('tau' + str(i), preparam[i][0],
                       min=bounds[i][0], max=bounds[i][1], vary=preparam[i][1])
        res_fit = minimize(self.get_difference, params, method=opt_method)
        fit_rep = fit_report(res_fit)
        if hasattr(res_fit, "success"):
            if res_fit.success is False:
                print("Fitting unsuccesful!")
        for name, param in res_fit.params.items():
            self.tau_fit.append(param.value)
        if (self.model == "custom model" or self.model == "custom matrix"):
            tau_sum = self.regenerate_m(self.tau_fit)
        else:
            tau_sum = self.tau_fit
        return tau_sum, fit_rep

    def calcD_fit(self):
        self.M_fit = self.get_m(self.tau_fit)
        AET = self.spectra @ self.M_fit.T
        EET_inv = np.linalg.inv(self.M_fit @ self.M_fit.T)
        D_fit = AET @ EET_inv
        self.D_fit = D_fit
        return D_fit

    def calcA_fit(self):
        A_fit = self.D_fit @ self.M_fit
        self.spec = A_fit
        return A_fit

    def calcResiduals(self):
        A_re = self.D_fit @ self.M_fit
        self.residuals = A_re - self.spectra
        return self.residuals
