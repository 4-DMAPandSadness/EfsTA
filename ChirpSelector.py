import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import SpanSelector
from matplotlib.widgets import Button

class ChirpSelector():
    
    def __init__(self, wave, time, spec, corrector):
        self.corr = corrector
        self.wave = wave
        self.time = time
        self.spec = spec
        self.bounds = []
        self.axes = []
        self.all_lv = []
        self.initFigure()

    def initFigure(self):
        self.fig = plt.figure(figsize=(6, 5.5), layout="constrained")
        self.gs = self.fig.add_gridspec(4, 4)
        self.axa = self.fig.add_subplot(self.gs[1, 0])
        self.axb = self.fig.add_subplot(self.gs[1, 1])
        self.axc = self.fig.add_subplot(self.gs[1, 2])
        self.axd = self.fig.add_subplot(self.gs[1, 3])
        
        button_width = 0.15
        button_height = 0.05
        button_padding = 0.01  # Abstand zwischen den Buttons
        
        total_width = 4 * button_width + (4 - 1) * button_padding
        start_x = 0.5 - total_width / 2
        
        ax_Show_x = start_x + 0 * (button_width + button_padding)
        ax_Undo_x = start_x + 1 * (button_width + button_padding)
        ax_Res_x = start_x + 2 * (button_width + button_padding)
        ax_Cont_x = start_x + 3 * (button_width + button_padding)
        
        button_y = 0.5 - button_height / 2  # Vertikale Zentrierung
        
        self.ax_Show = Button(self.axa, 'Show')
        self.ax_Undo = Button(self.axb, 'Undo')
        self.ax_Res = Button(self.axc, 'Reset', color='red')
        self.ax_Cont = Button(self.axd, 'Continue', color='green')
        
        self.ax_Show.on_clicked(self.show)
        self.ax_Undo.on_clicked(self.undo)
        self.ax_Res.on_clicked(self.reset)
        self.ax_Cont.on_clicked(self.cont)
        
        self.ax_Show.ax.set_position([ax_Show_x, button_y, button_width, button_height])
        self.ax_Undo.ax.set_position([ax_Undo_x, button_y, button_width, button_height])
        self.ax_Res.ax.set_position([ax_Res_x, button_y, button_width, button_height])
        self.ax_Cont.ax.set_position([ax_Cont_x, button_y, button_width, button_height])
        
        X, Y = np.meshgrid(self.wave,self.time)
        
        ax_full = self.fig.add_subplot(self.gs[0, :])
        
        ax_full.contourf(X,Y, self.spec, cmap="jet")
        
        ax_full.set_title("OKE Measurement")
        
        self.span = SpanSelector(
            ax_full,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True
        )
        
        ax_text = self.fig.add_subplot(self.gs[2, :])
        ax_text.spines['top'].set_visible(False)
        ax_text.spines['right'].set_visible(False)
        ax_text.spines['bottom'].set_visible(False)
        ax_text.spines['left'].set_visible(False)
        ax_text.xaxis.set_ticks([])
        ax_text.yaxis.set_ticks([])
        text = "Please select the data range to use for the chirp fitting. You can select one or more areas with your mouse. \n Click 'Show' to show all selected areas, 'Undo' remove the last selected area, 'Reset' to remove all selected areas and 'Continue' once you are finished to start the fitting process."
        ax_text.text(0.5, 0.5, text, ha='center', va='center', fontsize=12)
    
    def onselect(self,xmin, xmax):
        self.bounds.append([xmin, xmax])
    
    def undo(self, event):
        if len(self.bounds) != 0:
            ax = self.axes.pop()
            self.fig.delaxes(ax)
            self.bounds.pop()
            self.all_lv.pop()
            self.fig.canvas.draw_idle()
            print(self.bounds)
        
    def reset(self, event):
        if len(self.bounds) != 0:
            self.bounds = []
            self.all_lv = []
            for ax in self.axes:
                self.fig.delaxes(ax)
            self.fig.canvas.draw_idle()

    def show(self, event):
        if hasattr(self, "plotgrid"):
            for i in range(self.plotgrid.nrows -1):
                self.plotgrid[0,i].remove()
        self.plotgrid = self.gs[3,:].subgridspec(1, len(self.bounds))
        for ind, pair in enumerate(self.bounds):
            #create data
            lv = (self.wave >= pair[0]) & (self.wave <= pair[1])
            self.all_lv.append(lv)
            region_x = self.wave[lv]
            region_y = self.spec[:,lv]
            #create self.axes
            if len(region_y[1])>= 2:
                ax = self.fig.add_subplot(self.plotgrid[0, ind])
                X, Y = np.meshgrid(region_x,self.time)
                #add self.axes
                ax.contourf(X,Y, region_y, cmap="seismic")
                ax.set_xlim(region_x[0], region_x[-1])
                ax.set_ylim(self.time[0], self.time[-1])
                ax.get_yaxis().set_visible(False)
                self.axes.append(ax)
        self.fig.canvas.draw_idle()
            
    def cont(self, event):
        full_lv = np.array(self.all_lv).any(axis=0)
        
        self.sel_wave = self.wave[full_lv]
        self.sel_spec = self.spec[:,full_lv]
        
        self.corr.prepareFitting(self.sel_wave, self.time, self.sel_spec)
        plt.close(self.fig)
        # ax = self.fig.add_subplot(self.gs[3, :])
        # X, Y = np.meshgrid(self.sel_wave,self.time)
        # ax.contourf(X,Y, self.sel_spec, cmap="seismic")
        # ax.set_xlim(self.sel_wave[0], self.sel_wave[-1])
        # ax.set_ylim(self.time[0], self.time[-1])
        # self.fig.canvas.draw_idle()

# data = np.genfromtxt("/home/hackerman/Documents/Python Tests/gate.dat")

# x = data[0][1:]

# t = data.T[0][1:]
# t = t*100
# t = t.round()
# t = t/100

# lv_t = (t >= -1) & (t <= 1)
# y = t[lv_t]

# spec = data[1:]
# spec = spec.T[1:]

# nan = np.isnan(spec)
# cols, rows = np.where(nan)
# spec = spec

# if cols.any():
#     print("Warning: removeNan() has detected and removed NaNs in spectra.")
#     for i in range(len(cols)):
#         if cols[i] == 0:
#             spec[cols[i],rows[i]] = spec[cols[i]+1,rows[i]]
#         elif cols[i] == len(spec[0]):
#             spec[cols[i],rows[i]] = spec[cols[i]-1,rows[i]]
#         else:
#             new_value = (spec[cols[i]-1,rows[i]] + spec[cols[i]+1,rows[i]]) / 2
#             spec[cols[i],rows[i]] = new_value
# trans = spec.T

# trans = trans[lv_t, :]

# selector = ChirpSelector(x,y,trans)