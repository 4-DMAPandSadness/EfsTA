import numpy as np
import scipy.interpolate as sci

import ChirpSelector as CS
import CurvePrep as CP

import os

class ChirpCorrector():
    
    def __init__(self, parameters, mainwindow):
        self.sample_dir = parameters["Sample_Dir"]
        self.solvent_dir = parameters["Solvent_Dir"]
        self.chirp_dir = parameters["Chirp_Dir"]
        self.wave_range = parameters["Wave_Range"]
        self.scale = parameters["Scale"]
        self.options = parameters["Options"]
        self.exc_wave = parameters["Exc_Wave"]
        self.header = parameters["Header"]
        self.mainwindow = mainwindow
        self.popt = []

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
            print("Warning: removeNaNinf() has detected and removed NaNs / infs in spectra.")
            pos = np.where(nan)[0]
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
            self.lv = (wave >= 0)
            self.wave = wave[self.lv]
    
    def truncateSpec(self, spec):
        spec = spec[:,self.lv]
        return spec
        
    def removeBackground(self, spec, background):
        if self.scale == None:
            scale = 1    
        else:
            scale = (1-10**-self.scale) / (2.3*self.scale)
        return spec - (background * scale)
    
    def findMinima(self,chirp_wave, chirp_t, chirp_spec):
        centers = np.zeros(len(chirp_wave))
        for i in range(len(chirp_wave)-1):
            ind = np.argmin(chirp_spec[:,i])
            centers[i] = chirp_t[ind]
        return centers
                    
    def correctShift(self,shift):
        data_c = self.sample_spec.T
        data_cc = np.zeros_like(data_c)
        for i in range(len(data_c)):
            t_shift = self.time + shift[i]
            data_nn = self.removeNaNinf(data_c[i])
            data_cc[i,:] = sci.pchip_interpolate(self.time, data_nn, t_shift)
        print(self.wave)
        self.saveToTxt(self.wave, self.time, data_cc)
    
###############################################################################
    
    def prepareSample(self):
        data = self.readData(self.sample_dir)
        wave,  self.time, spec= self.splitData(data)
        self.genLV(wave)
        if self.options["Exclude"] == True:
            self.scattering(spec)
        spec_NN = self.removeNaNinf(spec).T
        spec_trunc = self.truncateSpec(spec_NN)
        if self.options["rmBG"] == True:
            self.prepareBackground()
            self.sample_spec = self.removeBackground(spec_trunc, self.background)
        else:
            self.sample_spec = spec_trunc
        
    def prepareBackground(self):
        data = self.readData(self.solvent_dir)
        wave, bg_time, spec = self.splitData(data)
        spec_NN = self.removeNaNinf(spec).T
        self.background = self.truncateSpec(spec_NN)
   
    def prepareChirp(self):
        if self.options["OKE"] == False:
            lv_t = (self.time >= -1) & (self.time <= 1)
            t = self.time[lv_t]
            select_spec = self.sample_spec[lv_t,:]
            self.CPC = CP.CurveClicker(self.wave, t, select_spec, self)
        else:
            data = self.readData(self.chirp_dir)
            wave, chirp_time, spec = self.splitData(data)
            spec_NN = self.removeNaNinf(spec).T
            lv_t = (chirp_time >= -1) & (chirp_time <= 1)
            chirp_t = chirp_time[lv_t]
            chirp_spec = spec_NN[lv_t,:]
            
            selector = CS.ChirpSelector(wave, chirp_t, chirp_spec, self)

    def prepareFitting(self, chirp_wave, chirp_t, sel_spec):
        centers = self.findMinima(chirp_wave, chirp_t, sel_spec)
        if self.options["Manually"] == True:
            self.CPL = CP.LassoSelector(self.wave, chirp_wave, centers, self)    
        else:
            CPA = CP.AutoSelector(self.wave, chirp_wave, centers)
            ns_wave, ns_centers = CPA.removeSpikes()
            shift, self.popt = CPA.fitCurve(ns_wave, ns_centers)
            self.correctShift(shift)

    def scattering(self, corr_spec):
        '''
        
        Vor Korrktur ausführen?

        Parameters
        ----------
        corr_spec : TYPE
            DESCRIPTION.

        Returns
        -------
        data_cc : TYPE
            DESCRIPTION.

        '''
        
        ### entfernen von spektrum einer speziellen delay
        exclude = self.exc_del
    
        pos = np.zeros(len(self.exc_del))
    
        for i in len(pos):
            tmp = np.argwhere(abs(self.time - exclude(i)) <= 1e-14) #warum nicht einfach nach exclude suchen
        
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
        
        ### spektren vor 0.2 | 0.3 | 0.4 average abziehen
        
        if self.options["Scatter"] == True:
            lv = (self.wave >= self.exc_wave-20) & (self.wave <= self.exc_wave+20)
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
        
        self.mainwindow.ui.Data_directory.setText(save_path)
        self.mainwindow.readData(save_path)
        
    def correctData(self):
        self.prepareSample()
        self.prepareChirp()