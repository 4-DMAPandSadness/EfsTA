import numpy as np
import scipy.optimize as sco 
import scipy.interpolate as sci

import matplotlib.pyplot as plt

import ChirpSelector as CS

import os


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
        if self.scale == None:
            scale = 1    
        else:
            scale = (1-10**-self.scale) / (2.3*self.scale)
        background = background[:,self.lv]
        return spec - (background * scale)
    
    def findMinima(self,chirp_wave, chirp_t, chirp_spec):
        centers = np.zeros(len(chirp_wave))
        for i in range(len(chirp_wave)-1):
            ind = np.argmin(chirp_spec[:,i])
            centers[i] = chirp_t[ind]
        return centers
    
    def removeSpikes(self,chirp_wave, centers):
        ns_wave = chirp_wave
        ns_centers = centers
        while True:
            prev_length = len(ns_centers)
            
            diff = np.absolute(np.diff(ns_centers))
            diff = np.insert(diff, 0, diff[0])
            diff = self.sepSpikesAndFollowValues(diff, ns_centers)
            lv = (diff < 0.2)
            
            ns_wave = chirp_wave[lv]
            ns_centers = centers[lv]
            
            new_length = len(ns_centers)
            
            if prev_length == new_length:
                break
        
        return ns_wave, ns_centers
    
    def sepSpikesAndFollowValues(self, diff, centers):
        idx = 0 
        diff_len = len(diff)
        while idx < diff_len - 1:
            if diff[idx] > 0.2:
                temp_idx = idx + 1
                
                while temp_idx < diff_len and abs(centers[idx -1] - centers[temp_idx]) > 0.2:
                    temp_idx += 1
                
                if temp_idx < diff_len and diff[temp_idx] != 0:
                    diff[temp_idx] = 0
                idx = temp_idx
            else:
                idx += 1
        return diff
    
    def fitCurve(self,ns_wave, ns_centers):
        # lb = [];
        # ub = [];
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
    
    def prepareFitting(self, chirp_wave, chirp_t, sel_spec):
        centers = self.findMinima(chirp_wave, chirp_t, sel_spec)
        np.savetxt("centers.txt", centers)
        np.savetxt("wave.txt", chirp_wave)
        # ns_wave, ns_centers = self.removeSpikes(chirp_wave, centers)
        # shift_plot, shift = self.fitCurve(ns_wave, ns_centers)
        
        
        # plt.figure()
        # plt.plot(chirp_wave, centers, '.', markersize="10", mfc='none', color = "blue", label = "Centers with spikes", alpha = 0.5)
        # plt.plot(ns_wave, ns_centers, '.', markersize="10", mfc='none', color = "red", label = "Centers without spikes", alpha = 0.7)
        # plt.plot(ns_wave, shift_plot, 'k-', label=f"a + 105*b / x2 + 106*c / x4 \n a = {round(self.popt[0])}, b = {round(self.popt[1])}, c = {round(self.popt[2])}")
        # plt.show()
        # plt.legend(loc='lower right')
        
        # corr_spec = self.correctShift(shift)
        
        # if self.options["Exclude"] == True:
        #     corr_spec = self.scattering()
        
        # if self.options["Save"] == True:
        #     self.saveToTxt(self.wave, self.time, corr_spec)
        
    def scattering(self, corr_spec):
            exclude = self.exc_del
        
            pos = np.zeros(len(self.exc_del))
        
            for i in len(pos):
                tmp = np.argwhere(abs(self.time - exclude(i)) <= 1e-14);
            
                if len(tmp) > 1:
                    print('load_raw:exclude', 'Indicated delay corresponds to '
                        'more than one spectrum. Decrease tolerance or/and check '
                        'spectra for double occurence.')
                    pos[i] = tmp[1]
                
                elif np.any(tmp) == False:
                    print('load_raw:exclude', f"Indicated delay: {exclude[i]}, not found. Delay ignored.'")
                    pos[i] = 0
                else:
                    pos[i] = tmp
            
            #pos(pos = 0) = []  ???
        
            corr_spec[:,pos] = []
            self.time[pos] = []

            # names = dict()
            # for i in len(self.time):
            #     names{i} = str(self.time[i])
            
            scatter = np.zeros(len(self.wave))
            
            if self.options["Scatter"] == True:
                lv = (self.wave >= self.exc_wave-20) & (self.wave <= self.exc_wave+20)
                
                if self.options["Single"] == True:
                    lv_t = self.time <= -0.4
                    tmp_time = self.time(lv_t)
                    nr_t = len(tmp_time)
                    
                    # names_bg = cell(nr_t,1);
                    # for i = 1 : nr_t
                    #     names_bg{i} = num2str(i);
                    # end
                    fig = plt.Figure()
                    plt.plot(self.wave, corr_spec[:,1:nr_t])
                    #legend(names_bg(1:end))
                    
                    scatter_bg = input('Indicate number of background spectrum to be subtracted: ');
                    
                    if np.any(scatter_bg == True):
                        tmp = corr_spec[:,scatter_bg]
                else:
                    tmp = np.mean(corr_spec[:,-11:],axis=1)
                scatter[lv] = tmp[lv]
            
            data_cc = corr_spec - np.tile(scatter,(1,len(self.time)))
            
            return data_cc
        
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
        
    
    def correctData(self, EfsTA):
        self.prepareBackground()
        self.prepareSample()
        self.prepareChirp()