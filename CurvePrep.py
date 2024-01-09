import numpy as np
import scipy.optimize as sco 

import matplotlib.pyplot as plt

from matplotlib import path
from matplotlib.widgets import Lasso

from matplotlib import colors as mcolors

class LassoSelector:
    def __init__(self,spec_wave, chirp_wave, centers, corr):
        self.corr = corr
        self.fig, self.ax = plt.subplots()
        self.collection = self.ax.scatter(chirp_wave, centers, marker='o')
        self.collection.set(alpha=0.5,clim=[0,1], cmap=mcolors.ListedColormap(["tab:blue", "tab:red"]),edgecolor="black", label="centers")
        self.ax.legend(loc='lower right')
        self.ax.set_title("Please select the data points for the curve fit by pressing and holding the left mouse button and draging the cursor around the data points. \n Press ENTER once you are finished.")
        self.spec_wave = spec_wave
        self.fig.canvas.mpl_connect('key_press_event', self.on_Enter)
        canvas = self.ax.figure.canvas
        canvas.mpl_connect('button_press_event', self.on_press)
        canvas.mpl_connect('button_release_event', self.on_release)

    def callback(self, verts):
        self.data = self.collection.get_offsets()
        self.collection.set_array(path.Path(verts).contains_points(self.data))
        canvas = self.collection.figure.canvas
        canvas.draw_idle()
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
        if len(self.ax.lines) > 1:
            self.ax.lines.clear()

        fitfun = lambda x, a1, a2, a3: a1 + 1e5*a2/x**2 + 1e6*a3/x**4 
        
        self.popt, pcov = sco.curve_fit(fitfun, centers[0] ,centers[1])

        self.shift = fitfun(self.spec_wave, *self.popt)
        
        self.ax.plot(centers[0], fitfun(centers[0], *self.popt), 'k-', label=f"a + 10**5*b/x**2 + 10**6*c/x**4 \n a = {round(self.popt[0])}, b = {round(self.popt[1])}, c = {round(self.popt[2])}")
        self.ax.legend(loc='lower right')
        self.fig.canvas.draw_idle()
    
    def on_Enter(self,event):
        if event.key == "enter":
            if self.collection.get_array().any():
                self.fitCurve(self.data[self.collection.get_array()].T)
                self.corr.popt = self.popt
                self.corr.correctShift(self.shift)
            
class AutoSelector:
    def __init__(self,tot_wave, chirp_wave, centers):
        self.tot_wave = tot_wave
        self.chirp_wave = chirp_wave
        self.centers = centers
    
    def removeSpikes(self):
        ns_wave = self.chirp_wave
        ns_centers = self.centers
        while True:
            prev_length = len(ns_centers)
            
            diff = np.absolute(np.diff(ns_centers))
            diff = np.insert(diff, 0, diff[0])
            diff = self.sepSpikesAndFollowValues(diff, ns_centers)
            lv = (diff < 0.2)
            ns_wave = ns_wave[lv]
            ns_centers = ns_centers[lv]
            
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
        
        fitfun = lambda x, a1, a2, a3: a1 + 1e5*a2/x**2 + 1e6*a3/x**4 
        
        popt, pcov = sco.curve_fit(fitfun, ns_wave, ns_centers)
        
        shift_plot = fitfun(ns_wave, *popt)
        shift = fitfun(self.tot_wave, *popt)
    
        plt.figure()
        plt.plot(self.chirp_wave, self.centers, '.', markersize="10", mfc='none', color = "blue", label = "Centers with spikes", alpha = 0.5)
        plt.plot(ns_wave, ns_centers, '.', markersize="10", mfc='none', color = "red", label = "Centers without spikes", alpha = 0.7)
        plt.plot(ns_wave, shift_plot, 'k-', label=f"a + 105*b / x2 + 106*c / x4 \n a = {round(popt[0])}, b = {round(popt[1])}, c = {round(popt[2])}")
        plt.show()
        plt.legend(loc='lower right')
        
        return shift, popt
    
class CurveClicker:
    def __init__(self, wave, time, spec, corr):
        self.chirp = []
        self.wave = wave
        self.corr = corr

        self.fig, (self.ax1, self.ax2) = plt.subplots(2,1)
        X, Y = np.meshgrid(self.wave,time)

        self.ax1.contourf(X, Y, spec, cmap="seismic")

        self.ax1.set_yscale('symlog')

        self.ax1.set_title("Sample Measurement from -1 to +1 ps \n Please select multiple points along the chirp by left-clicking. \n Press ENTER once you are finished.")
        
        eid = self.fig.canvas.mpl_connect('key_press_event', self.on_Enter)
        cid = self.fig.canvas.mpl_connect('button_press_event', self.on_Click)
        
    def on_Click(self,event):
        if event.xdata != None and event.ydata != None:
            self.chirp.append([event.xdata, event.ydata])
            self.ax1.scatter(event.xdata, event.ydata, color = "black", marker = 'o')
            self.fig.canvas.draw_idle()

    def on_Enter(self,event):
        if event.key == "enter":
            self.chirp = np.array(self.chirp)
            self.chirp = self.chirp.T
            self.ax2.scatter(self.chirp[0], self.chirp[1])
            
            self.fig.canvas.draw_idle()
            shift = self.fitCurve(self.chirp[0], self.chirp[1])
            self.corr.correctShift(shift)

    def fitCurve(self, xs, ys):
        
        fitfun = lambda x, a1, a2, a3: a1 + 1e5*a2/x**2 + 1e6*a3/x**4 
        
        popt, pcov = sco.curve_fit(fitfun, xs ,ys)

        ploty = fitfun(xs, *popt)
        
        shift = fitfun(self.wave, *popt)
        
        self.corr.popt = popt
        
        self.ax2.plot(xs, ploty, 'k-', label=f"a + 10**5*b/x**2 + 10**6*c/x**4 \n a = {round(popt[0])}, b = {round(popt[1])}, c = {round(popt[2])}")
        
        self.ax2.legend()
        
        return shift
    