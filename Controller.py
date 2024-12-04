from Model import Model
import Plotter
import numpy as np
from datetime import datetime
import shelve
from Importers import RichertImport as RI


class Controller:
    def __init__(self, path):
        self.path = path
        files = RI.get_files(self.path)
        self.name = RI.get_name(files[1])
        self.data = RI.get_data(files)

    def gen_model(self, d_limits, l_limits, model, opt_method, ivp_method):
        self.MOD = Model(self.data, d_limits, l_limits, model,
                         opt_method, ivp_method, self.path)

    def truncate_data(self, values, limits):
        d_lv = self.MOD.truncate_data(values, limits)
        l_lv = self.MOD.truncate_data(values, limits)

    def calc_das(self, preparam, opt_method):
        tau = [tau[0] for tau in preparam]
        self.MOD.M = self.MOD.getM(tau)
        tau_fit, fit_report = self.MOD.findTau_fit(preparam, opt_method)
        self.MOD.calcResiduals()
        self.save_results(0, tau, tau_fit,
                         self.MOD.getTauBounds(tau), self.MOD.lambdas,
                         self.MOD.delays, self.MOD.spectra, fit_report)
        return tau_fit

    def calc_sas(self, K, preparam, C_0, model, tau_low, tau_high, opt_method, ivp_method):
        tau = [tau[0] for tau in preparam]
        if (model == "custom model" or model == "custom matrix"):
            M_lin = self.MOD.getM_lin(K)
            K, n = self.MOD.getK(M_lin)
            self.MOD.setTauBounds(tau_low, tau_high, M_lin)
            if model == "custom matrix":
                preparam = [(tau, True) for tau in M_lin]
        else:
            self.MOD.setTauBounds(tau_low, tau_high, tau)
            K, n = self.MOD.getK(tau)
        self.MOD.setInitialConcentrations(C_0)
        self.MOD.solveDiff(ivp_method)
        tau_fit, fit_report = self.MOD.findTau_fit(preparam, opt_method)
        self.MOD.calcD_fit()
        self.MOD.calcA_fit()
        self.MOD.calcResiduals()
        self.save_results(model,
                         tau, 
                         tau_fit,
                         self.MOD.getTauBounds(tau),
                         self.MOD.lambdas,
                         self.MOD.delays,
                         self.MOD.spectra,
                         fit_report)
        return tau_fit

    def plot_3_in_one(self, plot_params, data, model):
        ws = plot_params["ws"]
        ds = plot_params["ds"]
        v_min = plot_params["vmin"]
        v_max = plot_params["vmax"]
        cont = plot_params["cont"]
        mul = plot_params["mul"]

        if model == None:
            plot = Plotter.plot_3_in_one(data, ws, ds, v_min, v_max, cont, mul, self.labels)
        if model == 0:
            plot = Plotter.plot_3_in_one(data, ws, ds, v_min, v_max, cont, mul, self.labels)
        else:
            plot = Plotter.plot_3_in_one(data, ws, ds, v_min, v_max, cont, mul, self.labels)
        return plot

    def plot_3d(self, plot_params, data, model):
        v_min = plot_params["vmin"]
        v_max = plot_params["vmax"]
        mul = plot_params["mul"]
        if model == None:
            plot = Plotter.plot_3d(data, v_min, v_max, mul, self.labels, add="RAW")
        if model == 0:
            plot = Plotter.plot_3d(self.MOD.spec, v_min, v_max, mul, self.labels, add="_GLA")
        else:
            plot = Plotter.plot_3d(self.MOD.spec, v_min, v_max, mul, self.labels, add="_GTA")
            
        return plot

    def plot_solo(self, plot_params, data,  model, solo):
        ws = plot_params["ws"]
        ds = plot_params["ds"]
        v_min = plot_params["vmin"]
        v_max = plot_params["vmax"]
        cont = plot_params["cont"]
        mul = plot_params["mul"]
        
        if model is None:
            plot = Plotter.plot_solo(data, v_min, v_max, solo, cont, mul, self.labels, add="_RAW")
        elif model == 0:
            plot = Plotter.plot_solo(data, v_min, v_max, solo, cont, mul, self.labels, add="_GLA")
        else:
            plot = Plotter.plot_solo(data, v_min, v_max, solo, cont, mul, self.labels, add="_GTA")
        return plot

    def plot_2d_residuals(self, model, mul):
        ltx = str(mul).count("0")
        dot = ""
        if mul != 1:
            dot = " \cdot " + "10^" + str(ltx) + "$"
        if model == 0:
            Plotter.plotData(self.MOD.delays, self.MOD.residuals.T,
                              self.labels[1], self.labels[2] + dot,
                              add="_GLA_Residuals_")
        else:
            Plotter.plotData(self.MOD.delays, self.MOD.residuals.T,
                              self.labels[1], self.labels[2] + dot,
                              add="_GTA_Residuals_")

    def plot_3d_residuals(self, v_min, v_max, model, cont, mul):
        if model == 0:
            plot = Plotter.plotHeat([], [], None, None, self.MOD.residuals, cont, mul,
                              self.labels, add="_GLA_Residuals")
        else:
            plot = Plotter.plotHeat([], [], None, None, self.MOD.residuals, cont, mul,
                              self.labels, add="_GTA_Residuals")
        return plot

    def plot_kinectics(self, model):
        if model == 0:
            plot = Plotter.plotData(self.MOD.delays, self.MOD.M.T, self.labels[1],
                              "concentration", label=None, add="_GLA_kin")
        else:
            plot = Plotter.plotData(self.MOD.delays, self.MOD.M.T, self.labels[1],
                              "concentration", label=None, add="_GTA_kin")
        return plot

    def plot_das(self, model, tau, mul):
        ltx = str(mul).count("0")
        dot = ""
        if mul != 1:
            dot = f" $\cdot 10^{ltx}$"
        unit = self.labels[1].split("/")[1]
        for i, t in enumerate(tau):
            if t < 1:
                tau[i] = round(t, 3)
            elif t < 10 and t > 1:
                tau[i] = round(t, 2)
            elif t < 100 and t > 10:
                tau[i] = round(t, 1)
            else:
                tau[i] = round(t)
        if model == 0:
            label = []
            for ind, tau in enumerate(tau):
                label.append(f"$\\tau_{ind}=$ {tau}{unit}")
            plot = Plotter.plotData(self.MOD.lambdas, self.MOD.D_fit,
                              self.labels[0], self.labels[2] + dot,
                              label=label, add="_DAS")
        elif (model == "custom model" or model == "custom matrix"):
            custom_tau = list(self.MOD.getM_lin(np.array(tau)))
            label = []
            for ind, tau in enumerate(tau):
                label.append(f"$\\tau_{ind}=$ {custom_tau}{unit}")
            plot = Plotter.plotData(self.MOD.lambdas, self.MOD.D_fit,
                              self.labels[0], self.labels[2] + dot,
                              label=label, add="_SAS")
        else:
            label = []
            for ind, tau in enumerate(tau):
                label.append(f"$\\tau_{ind}=$ {tau}{unit}")
            if model == 2:
                label.append("inf")
            plot = Plotter.plotData(self.MOD.lambdas, self.MOD.D_fit,
                              self.labels[0], self.labels[2] + dot,
                              label=label, add="_SAS")    
        return plot
    
    def create_animation(self):
        pass

    def save_results(self, model, tau_start, tau_fit, A_fit,
                    D_fit, bounds, lambdas, delays, spectra, fit_report):
        for i, n in enumerate(tau_fit):
            tau_fit[i] = round(n, 2)
        time_unit = self.labels[1].split("/")[1]
        x_axis_unit = self.labels[0].split("/")[1]
        if model == 0:
            path = self.MOD.path
            name = self.MOD.name + "_GLA"
            txt = name + "_results.txt"
        else:
            path = self.MOD.path
            name = self.MOD.name + "_GTA"
            txt = name + "_results.txt"

        if (model != "custom model" or model != "custom matrix"):
            k_fit = 1 / np.array(tau_fit)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit), where=tau_fit != 0)
        now = datetime.now()
        dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
        summary = (
            f"{dt_string}\n{name}\nSolver: scipy.optimize.minimize\n"
            f"Model: {model}\nStarting Parameters: {tau_start}\n"
            f"Bounds: {bounds}\nWavelength/Field range: {l_limits[0]} - {l_limits[1]} {x_axis_unit}\n"
            f"delay range: {d_limits[0]} - {d_limits[1]} {time_unit}\n\n"
            f"Time constants / {time_unit}: {tau_fit}\n"
            f"Rate constants / {time_unit}^-1: {k_fit}\n\n"
            f"lmfit fit_report:\n\n{fit_report}\n\n"
            f"All results and plots can be found here:\n\n{path}"
        )
        np.savetxt(path + txt, summary)
        np.savetxt(path + name + "_A_fit.txt", A_fit)
        if model == 0:
            np.savetxt(path + name + "_DAS.txt", D_fit)
        else:
            np.savetxt(path + name + "_SAS.txt", D_fit)
        np.savetxt(path + name + "_limited_lambda.txt", lambdas)
        np.savetxt(path + name + "_limited_delays.txt", delays)
        np.savetxt(path + name + "_limited_spectra.txt", spectra)

    def get_results(self, model):
        if model == 0:
            path = self.MOD.path
            name = self.MOD.name + "_GLA"
            txt = name + "_results.txt"
        else:
            path = self.MOD.path
            name = self.MOD.name + "_GTA"
            txt = name + "_results.txt"
        with open(path + txt) as f:
            text = f.read()
        return text

    def pickle_data(self, input_dict):
        path = self.path + "/"
        txt = self.name + "_input_backup"
        s = shelve.open(path + txt, writeback=True)
        s.clear()
        for key, value in input_dict.items():
            s[key] = value
        s.close()

    def get_pickle(self):
        path = self.path + "/"
        txt = self.name + "_input_backup"
        s = shelve.open(path + txt, writeback=False)
        shelf = dict(s).copy()
        s.close()
        return shelf
