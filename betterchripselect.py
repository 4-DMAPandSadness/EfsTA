import sys
import numpy as np
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QGridLayout, QTextBrowser
from matplotlib.widgets import SpanSelector

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class ChirpSelector(QDialog):
    def __init__(self, wave, time, spec, corrector):
        super(QDialog, self).__init__()
        
        self.corr = corrector
        self.wave = wave
        self.time = time
        self.spec = spec
        self.bounds = []
        self.axes = []
        self.all_lv = []
        self.initUI()
        
    def initUI(self):
        
        self.fig1, self.ax_full = plt.subplots()
        self.canvas1 = FigureCanvas(self.fig1)
        self.fig2 = plt.Figure()
        self.canvas2 = FigureCanvas(self.fig2)
        self.gridLayout = QGridLayout()
        text = "Please select the data range to use for the chirp fitting. \n You can select one or more areas with your mouse by left-clicking on the figure, holding and draging your mouse. \n Click 'Show' to show all selected areas, 'Undo' remove the last selected area, \n 'Reset' to remove all selected areas and 'Continue' once you are finished to start the fitting process."

        self.textBrowser = QTextBrowser()
        self.textBrowser.setText(text)

        self.gridLayout.addWidget(self.textBrowser, 0, 0, 1, 4)
        
        self.gridLayout.addWidget(self.canvas1, 1, 0, 1, 4)
        
        self.show_btn = QPushButton(text="Show Selected")
        self.gridLayout.addWidget(self.show_btn, 2, 0, 1, 1)
        self.show_btn.clicked.connect(self.show_sel)
        
        self.undo_btn = QPushButton(text="Undo Last")
        self.gridLayout.addWidget(self.undo_btn, 2, 1, 1, 1)
        self.undo_btn.clicked.connect(self.undo)
        
        self.res_btn = QPushButton(text="Reset All")
        self.gridLayout.addWidget(self.res_btn, 2, 2, 1, 1)
        self.res_btn.clicked.connect(self.reset)
        
        self.cont_btn = QPushButton(text="Continue")
        self.gridLayout.addWidget(self.cont_btn, 2, 3, 1, 1)
        self.cont_btn.clicked.connect(self.cont)
        
        self.gridLayout.addWidget(self.canvas2, 3, 0, 1, 4)
        
        self.setLayout(self.gridLayout)
        
        X, Y = np.meshgrid(self.wave, self.time)
        self.ax_full.contourf(X, Y, self.spec, cmap="seismic")
        self.ax_full.set_title("OKE Measurement")
        self.span = SpanSelector(
            self.ax_full,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True
        )



    def onselect(self, xmin, xmax):
        if xmax - xmin > 1:
            self.bounds.append([xmin, xmax])

    def undo(self):
        if len(self.bounds) != 0:
            ax = self.axes.pop()
            self.fig2.delaxes(ax)
            self.bounds.pop()
            self.all_lv.pop()
            if hasattr(self, "plotgrid"):
                for i in range(self.plotgrid.nrows - 1):
                    self.plotgrid[0, i].remove()
            self.canvas2.draw_idle()

    def reset(self):
        if len(self.bounds) != 0:
            self.bounds = []
            self.all_lv = []
        if self.axes:
            while self.axes:
                ax = self.axes.pop()
                self.fig2.delaxes(ax)
            self.canvas2.draw_idle()

    def show_sel(self):
        if self.axes:
            while self.axes:
                ax = self.axes.pop()
                self.fig2.delaxes(ax)
            self.canvas2.draw_idle()
        if self.bounds:
            self.plotgrid = plt.GridSpec(1, len(self.bounds),self.fig2)
        for ind, pair in enumerate(self.bounds):
            lv = (self.wave >= pair[0]) & (self.wave <= pair[1])
            self.all_lv.append(lv)
            region_x = self.wave[lv]
            region_y = self.spec[:, lv]
            if len(region_y[1]) >= 2:
                ax = self.fig2.add_subplot(self.plotgrid[0, ind])
                X, Y = np.meshgrid(region_x, self.time)
                ax.contourf(X, Y, region_y, cmap="seismic")
                ax.set_xlim(region_x[0], region_x[-1])
                ax.set_ylim(self.time[0], self.time[-1])
                ax.get_yaxis().set_visible(False)
                self.axes.append(ax)
        self.canvas2.draw_idle()

    def cont(self):
        if self.axes:
            full_lv = np.array(self.all_lv).any(axis=0)
            self.sel_wave = self.wave[full_lv]
            self.sel_spec = self.spec[:, full_lv]
            self.corr.prepareFitting(self.sel_wave, self.time, self.sel_spec)
            #plt.close(self.fig)
            self.close()
            
    def plot(self):
        pass