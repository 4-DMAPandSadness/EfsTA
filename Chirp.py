import numpy as np
import scipy.optimize as sco 
import scipy.interpolate as sci

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
        time = data.T[0][1:]
        time = (time*100).round / 100
        spec = data[1:]
        spec = spec.T[1:]
        self.time = time
        return wave, spec

    def removeNaN(self, spec):
        nan = np.isnan(spec)
        cols, rows = np.where(nan)
        spec = spec
        if cols.any():
            print("Warning: removeNaN() has detected and removed NaNs in spectra.")
            for i in range(len(cols)):
                if cols[i] == 0:
                    spec[cols[i],rows[i]] = spec[cols[i]+1,rows[i]]
                elif cols[i] == len(spec[0]):
                    spec[cols[i],rows[i]] = spec[cols[i]-1,rows[i]]
                else:
                    new_value = (spec[cols[i]-1,rows[i]] + spec[cols[i]+1,rows[i]]) / 2
                    spec[cols[i],rows[i]] = new_value
        return spec.T
    
    def genLV(self,wave):
        self.lv = (wave >= self.wave_range[0]) & (wave <= self.wave_range[1])
        self.wave = wave[self.lv]
    
    def truncateSpec(self, spec):
        spec = spec[:,self.lv]
        return spec
        
    def removeBackground(self, spec, background):
        scale = (1-10**-self.scale) / (2.3*self.scale)
        background = background[:,self.lv]
        return spec - (background * scale)
    
    def findMinima(self, chirp_t, chirp_spec):
        centers = np.zeros(len(self.wave))
        for i in len(self.wave):
            ind = np.argmin(chirp_spec[:,i])
            centers[i] = chirp_t[ind]
        return centers
    
    def fitCurve(self, centers):
        lb = [];
        ub = [];
        y0 = [3.1,-2.9,-1.8e4]
        # options = optimset('MaxIter', 50, 'TolFun', 1e-17, 'TolX', 1e-16, ...
        #     'MaxFunEvals', 100, 'Display', 'off')
        
        fitfun = lambda y, x: y[0] + 1e5*y[1]/x^2 + 1e6*y[2]/x^4 
        
        p = sco.curvefit(fitfun, y0, self.wave,centers, lb, ub)
        
        shift = fitfun(p,self.wave)
        
        return shift
    
    def correctShift(self, shift):
        data_c = self.sample_spec #' <- complex transponieren?
        data_cc = np.zeros_like(data_c)

        for i in len(data_c[0]):
            t_shift = self.time + shift[i]
            data_cc[i,:] = sci.PchipInterpolator(self.time, data_c[i,:], t_shift)
            #time oder t_shift? eins von beiden muss raus python implementation nur zwei argumente
        return data_c
        
###############################################################################
    
    def prepareSample(self):
        data = self.readData(self.sample_dir)
        wave, spec = self.splitData(data)
        spec_NN = self.removeNaN(spec)
        spec_trunc = self.truncate(wave, spec_NN)
        self.sample_spec = self.removeBackground(spec_trunc, self.background)
        
    def prepareBackground(self):
        data = self.readData(self.solvent_dir)
        wave, spec = self.splitData(data)
        spec_NN = self.removeNaN(spec)
        self.background = self.truncate(wave, spec_NN)

    def prepareChirp(self):
        data = self.readData(self.chirp_dir)
        wave, spec = self.splitData(data)
        spec_NN = self.removeNaN(spec)
        spec_trunc = self.truncate(wave, spec_NN)
        
        lv_t = (self.time >= -1) & (self.time <= 1)
        chirp_t = self.time[lv_t]
        chirp_spec = spec_trunc[lv_t,:]
        
        centers = self.findMinima(chirp_t, chirp_spec)
        
        shift = self.fitCurve(centers)
        
        x = self.correctShift(shift)
        

    
    def correctData(self):
        self.prepareBackground()
        self.prepareSample()
        self.prepareChirp()