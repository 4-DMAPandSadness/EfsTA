import numpy as np
import scipy.optimize as sco 
import scipy.interpolate as sci

import matplotlib.pyplot as plt

import ChirpSelector as CS

import os

def correction(parameters):
    pass

#for sample data / bg
# getData -> splitData -> reemoveNaN -> truncate -> removeBG

#for chirp
# getData -> splitData ->

class ChirpCorrector():
    
    def __init__(self, parameters):
        self.sample_dir = parameters["Sample_Dir"]
        self.solvent_dir = parameters["Solvent_Dir"]
        self.chirp_dir = parameters["Chirp_Dir"]
        self.wave_range = parameters["Wave_Range"]
        self.scale = parameters["Scale"]
        self.options = parameters["Options"]
        self.exc_wave = parameters["Exc_Wave"]

######################Basis Funktionen#########################################

    def readData(self, directory):
        data = np.genfromtxt(directory, delimiter = ' ') #, skip_header=10
        return data

    def splitData(self, data):
        wave = data[0][1:]
        time = data.T[0][1:]*100
        time = time.round() / 100
        spec = data[1:]
        spec = spec.T[1:]
        return wave, time, spec

    def removeNaNinf(self, spec):
        nan = ~np.isfinite(spec)
        if nan.ndim == 1:
            pos = np.where(nan)[0]
            print("Warning: removeNaNinf() has detected and removed NaNs / infs in spectra.")
            for i, val in enumerate(pos):
                if val == 0:
                    spec[pos[i]] = spec[pos[i]+1]
                elif val == len(spec)-1:
                    spec[pos[i]] = spec[pos[i]-1]
                else:
                    new_value = (spec[pos[i]+1] + spec[pos[i]-1]) / 2
                    spec[pos[i]] = new_value
        elif nan.ndim == 2:
            cols, rows = np.where(nan)
            print("Warning: removeNaNinf() has detected and removed NaNs / infs in spectra.")
            for i, val in enumerate(cols):
                if val == 0:
                    spec[cols[i],rows[i]] = spec[cols[i]+1,rows[i]]
                elif val == len(spec)-1:
                    spec[cols[i],rows[i]] = spec[cols[i]-1,rows[i]]
                else:
                    new_value = (spec[cols[i]-1,rows[i]] + spec[cols[i]+1,rows[i]]) / 2
                    spec[cols[i],rows[i]] = new_value
        else:
            spec = spec
        return spec
    
    def genLV(self,wave):
        if self.wave_range != []:
            self.lv = (wave >= self.wave_range[0]) & (wave <= self.wave_range[1])
            self.wave = wave[self.lv]
        else:
            self.lv = wave >= 0
            self.wave = wave[self.lv]
    
    def truncateSpec(self, spec):
        spec = spec[:,self.lv]
        return spec
        
    def removeBackground(self, spec, background):
        scale = (1-10**-self.scale) / (2.3*self.scale)
        background = background[:,self.lv]
        return spec - (background * scale)
    
    def findMinima(self,chirp_wave, chirp_t, chirp_spec):
        centers = np.zeros(len(chirp_wave))
        for i in range(len(chirp_wave)-1):
            ind = np.argmin(chirp_spec[:,i])
            centers[i] = chirp_t[ind]
        return centers
    
    def fitCurve(self,ns_wave, ns_centers):
        lb = [];
        ub = [];
        y0 = [3.1,-2.9,-1.8e4]
        # options = optimset('MaxIter', 50, 'TolFun', 1e-17, 'TolX', 1e-16, ...
        #     'MaxFunEvals', 100, 'Display', 'off')
        
        fitfun = lambda x, a1, a2, a3: a1 + 1e5*a2/x**2 + 1e6*a3/x**4 
        
        self.popt, pcov = sco.curve_fit(fitfun, ns_wave, ns_centers, p0=y0)
        
        shift_plot = fitfun(ns_wave, *self.popt)
        shift = fitfun(self.wave, *self.popt)
        return shift_plot, shift
        
    def correctShift(self,shift):
        data_c = self.sample_spec.T
        data_cc = np.zeros_like(data_c)

        # print(f"self.time: {self.time.shape} \n self.data: {data_c[0,:].shape} \n t_shift: {shift.shape}")
        for i in range(len(data_c)):
            t_shift = self.time + shift[i]
            data_nn = self.removeNaNinf(data_c[i])
            data_cc[i,:] = sci.pchip_interpolate(self.time, data_nn, t_shift)
        return data_cc
        
###############################################################################
    
    def prepareSample(self):
        data = self.readData(self.sample_dir)
        wave,  self.time, spec= self.splitData(data)
        spec_NN = self.removeNaNinf(spec).T
        spec_trunc = self.truncateSpec(spec_NN)
        self.sample_spec = self.removeBackground(spec_trunc, self.background)
        
    def prepareBackground(self):
        data = self.readData(self.solvent_dir)
        wave, bg_time, spec = self.splitData(data)
        self.genLV(wave)
        spec_NN = self.removeNaNinf(spec).T
        self.background = self.truncateSpec(spec_NN)

    def prepareChirp(self):
        data = self.readData(self.chirp_dir)
        wave, chirp_time, spec = self.splitData(data)
        spec_NN = self.removeNaNinf(spec).T
        lv_t = (chirp_time >= -1) & (chirp_time <= 1)
        chirp_t = chirp_time[lv_t]
        chirp_spec = spec_NN[lv_t,:]
        
        selector = CS.ChirpSelector(wave, chirp_t, chirp_spec, self)
    
    def removeSpikes(self,chirp_wave, centers):
        diff = np.absolute(np.diff(centers))
        diff = np.insert(diff, 0, diff[0])
        lv = (diff < 0.1)
        
        ns_wave = chirp_wave[lv]
        ns_centers = centers[lv]
        
        return ns_wave, ns_centers
    
    def prepareFitting(self, chirp_wave, chirp_t, sel_spec):
        centers = self.findMinima(chirp_wave, chirp_t, sel_spec)
        ns_wave, ns_centers = self.removeSpikes(chirp_wave, centers)
        shift_plot, shift = self.fitCurve(ns_wave, ns_centers)
        plt.plot(chirp_wave, centers, '.', markersize="10", mfc='none', color = "blue", label = "Centers with spikes", alpha = 0.5)
        plt.plot(ns_wave, ns_centers, '.', markersize="10", mfc='none', color = "red", label = "Centers without spikes", alpha = 0.7)
        plt.plot(ns_wave, shift_plot, 'k-', label=f"a + 10**5*b/x**2 + 10**6*c/x**4 \n a = {round(self.popt[0])}, b = {round(self.popt[1])}, c = {round(self.popt[2])}")
        plt.show()
        plt.legend()
        
        corr_spec = self.correctShift(shift)
        
        self.saveToTxt(self.wave, self.time, corr_spec)
        
    def saveToTxt(self, corr_wave, corr_time, corr_spec):
        file = self.sample_dir.split("/")[-1].split(".")[0]
        path = "/".join(self.sample_dir.split("/")[:-1])
        save_path = f"{path}/corrected_Data/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        np.savetxt(f"{save_path}{file}_taspectra.txt",corr_spec,encoding = '-ascii')
        np.savetxt(f"{save_path}{file}_delays.txt",corr_time,encoding = '-ascii')
        np.savetxt(f"{save_path}{file}_lambda.txt",corr_wave,encoding = '-ascii')
        np.savetxt(f"{save_path}{file}_curveFit_Parameters.txt",self.popt,encoding = '-ascii')
        
    
    def correctData(self):
        self.prepareBackground()
        self.prepareSample()
        self.prepareChirp()