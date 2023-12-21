import numpy as np
import scipy.optimize as sco 
import scipy.interpolate as sci

import matplotlib.pyplot as plt

import ChirpSelector as CS

import os

from matplotlib import path
from matplotlib.widgets import Lasso, Button

from matplotlib import colors as mcolors

class LassoManager:
    def __init__(self,spec_wave, chirp_wave, centers, corr):
        self.corr = corr
        self.fig = plt.figure(figsize=(6, 5.5), layout="constrained")
        self.gs = self.fig.add_gridspec(2, 1)
        self.ax = self.fig.add_subplot(self.gs[0, 0])
        self.ax_button = self.fig.add_subplot(self.gs[1, 0])
        self.collection = self.ax.scatter(chirp_wave, centers, marker='o')
        self.collection.set(alpha=0.5,clim=[0,1], cmap=mcolors.ListedColormap(["tab:blue", "tab:red"]),edgecolor="black", label="centers")
        self.ax.legend(loc='lower right')
        self.spec_wave = spec_wave
        self.ax_done = Button(self.ax_button, 'Done')
        self.ax_done.ax.set_position([0.4, 0.3, 0.1, 0.075])
        
        self.ax_done.on_clicked(self.done)
        
        canvas = self.ax.figure.canvas
        canvas.mpl_connect('button_press_event', self.on_press)
        canvas.mpl_connect('button_release_event', self.on_release)

    def done(self, event):
        self.corr.removeShift(self.shift, self.popt)
        plt.close(self.fig)

    def callback(self, verts):
        data = self.collection.get_offsets()
        self.collection.set_array(path.Path(verts).contains_points(data))
        canvas = self.collection.figure.canvas
        canvas.draw_idle()
        if self.collection.get_array().any():
            self.fitCurve(data[self.collection.get_array()].T)
        del self.lasso

    def on_press(self, event):
        canvas = self.collection.figure.canvas
        if event.inaxes is not self.collection.axes or canvas.widgetlock.locked():
            return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        canvas.widgetlock(self.lasso)

    def on_release(self, event):
        canvas = self.collection.figure.canvas
        if hasattr(self, 'lasso') and canvas.widgetlock.isowner(self.lasso):
            canvas.widgetlock.release(self.lasso)
    
    def fitCurve(self,centers):
        y0 = [3.1,-2.9,-1.8e4]
        if len(self.ax.lines) > 1:
            self.ax.lines.clear()

        fitfun = lambda x, a1, a2, a3: a1 + 1e5*a2/x**2 + 1e6*a3/x**4 
        
        self.popt, pcov = sco.curve_fit(fitfun, centers[0] ,centers[1], p0=y0)

        self.shift = fitfun(self.spec_wave, *self.popt)
        
        self.ax.plot(centers[0], fitfun(centers[0], *self.popt), 'k-', label=f"a + 10**5*b/x**2 + 10**6*c/x**4 \n a = {round(self.popt[0])}, b = {round(self.popt[1])}, c = {round(self.popt[2])}")
        self.ax.legend(loc='lower right')

class ChirpCorrector():
    
    def __init__(self, parameters, mainwindow):
        self.sample_dir = parameters["Sample_Dir"]
        self.solvent_dir = parameters["Solvent_Dir"]
        self.chirp_dir = parameters["Chirp_Dir"]
        self.wave_range = parameters["Wave_Range"]
        self.scale = parameters["Scale"]
        self.options = parameters["Options"]
        self.exc_wave = parameters["Exc_Wave"]
        self.mainwindow = mainwindow

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
      self.manager = LassoManager(self.wave, chirp_wave, centers, self)
        
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
        self.removeSpikes(chirp_wave, centers)
        
    
    def removeShift(self, shift, popt):
        corr_spec = self.correctShift(shift)
        self.popt = popt
        if self.options["Exclude"] == True:
            corr_spec = self.scattering()
        
        if self.options["Save"] == True:
            self.saveToTxt(self.wave, self.time, corr_spec)
        
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
        file = self.chirp_dir.split("/")[-1].split(".")[0] # chirp -> sample#
        path = "/".join(self.chirp_dir.split("/")[:-1]) ###dito
        save_path = f"{path}/corrected_Data/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        np.savetxt(f"{save_path}{file}_alt_taspectra.txt",corr_spec,encoding = '-ascii')
        np.savetxt(f"{save_path}{file}_alt_delays.txt",corr_time,encoding = '-ascii')
        np.savetxt(f"{save_path}{file}_alt_lambda.txt",corr_wave,encoding = '-ascii')
        np.savetxt(f"{save_path}{file}_alt_curveFit_Parameters.txt",self.popt,encoding = '-ascii')
        
        self.mainwindow.ui.Data_directory.setText(save_path)
        self.mainwindow.readData(save_path)
        
    
    def correctData(self, EfsTA):
        self.prepareBackground()
        self.prepareSample()
        self.prepareChirp()