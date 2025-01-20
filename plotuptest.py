import numpy as np
import PopUps as pu
import Plotter as pt
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout
import matplotlib.pyplot as plt
import matplotlib.colors as col
plt.style.use('seaborn-v0_8-dark-palette')

# class Main(QWidget):
#     def __init__(self):
#         super(QWidget, self).__init__()
#         wave = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_lambda.txt"
#         delay = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_delays.txt"
#         spec = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_taspectra.txt"
#         del_points = np.genfromtxt(delay)
#         wav_points = np.genfromtxt(wave)
#         spec_points = np.genfromtxt(spec)

#         # wave = [400,500,600]
#         # time = [30,600, 2300]
#         # path = "/home/hackerman/temp"
#         # name = "test"
#         # labels = ["a / b", "c / d", "e / f"]
#         # self.plot = pt.Plotter("seaborn-dark-palette", wav_points, del_points, spec_points, path, name)
#         # self.fig = self.plot.plot_heat(wave, time, None, None, spec_points, 20, 1, labels, add = "")


#         self.layout = QVBoxLayout()
#         self.setLayout(self.layout)
#         self.btn = QPushButton("test")
#         self.btn.clicked.connect(lambda: self.test([wav_points, spec_points, del_points], False, "Wavelength / nm", "$\\Delta$Abs. / a.u."))
#         self.layout.addWidget(self.btn)

#     def test(self, data, log, x, y):
#         self.popup = pu.Animation_Display(data, log, x, y)
#         self.popup.show()

# class Main(QWidget):
#     def __init__(self):
#         super(QWidget, self).__init__()
#         self.layout = QVBoxLayout()
#         self.setLayout(self.layout)
#         self.btn = QPushButton("test")
#         self.btn.clicked.connect(lambda: self.test())
#         self.layout.addWidget(self.btn)

#     def plot(self):
#         '''
#         Script inputs
#         '''

#         #DATA


#         x_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_lambda.txt"
#         y_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_delays.txt"
#         z_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_taspectra.txt"


#         cutting = True
#         x_range = [480,1100]
#         y_range = [0.2, 3000]

#         #PLOT

#         figsize = (6, 4)
#         dpi = 100

#         contour = True
#         contour_lines = 20

#         y_symlog = True
#         lin_log = 10

#         y_log = False

#         x_label = "$\\lambda$ / nm"
#         y_label = "delay / ps" # μs

#         title = "Full Data Heatmap"

#         x_slice = []
#         y_slice = []

#         v_min = None
#         v_max = None

#         '''
#         Script start
#         '''

#         #Getting the Data

#         x_data = np.genfromtxt(x_data_path).T
#         y_data = np.genfromtxt(y_data_path).T
#         z_data = np.genfromtxt(z_data_path).T

#         #Cutting the Data
#         if cutting:
#             x_lv = (x_data >= x_range[0]) & (x_data <= x_range[1])
#             y_lv = (y_data >= y_range[0]) & (y_data <= y_range[1])
#             x_data = x_data[x_lv]
#             y_data = y_data[y_lv]
#             z_data = z_data[:,x_lv]
#             z_data = z_data[y_lv,:]

#         X, Y = np.meshgrid(x_data, y_data)


#         #Plotting

#         fig0, ax0 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")
#         fig1, ax1 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")
#         fig2, ax2 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")

#         if v_min is None:
#             v_min = np.min(z_data)
#         if v_max is None:
#             v_max = np.max(z_data)

#         ##Full Data Heatmap
#         pcm = ax0.pcolormesh(x_data, y_data, z_data, cmap=plt.cm.seismic, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max), shading="auto")
#         # cb = plt.colorbar(pcm)
#         # cb.set_ticks([v_min, 0, v_max])
#         # cb.set_label(colorbar_label)

#         if contour:
#             ax0.contour(x_data, y_data, z_data, levels=np.arange(v_min, v_max, (1 / contour_lines) * (v_max - v_min)), colors="black", linewidths=0.7, linestyles="solid")
#         else:
#             ax0.contourf(X,Y, z_data, cmap = 'seismic', levels=np.arange(v_min, v_max, (1 / contour_lines) * (v_max - v_min)), alpha=0.7, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max))

#         for t in x_slice:
#             ax0.axvline(t, color="black", linestyle="-.")
#         for v in y_slice:
#             ax0.axhline(v, color="black", linestyle="dotted")

#         ax0.axis([np.min(x_data), np.max(x_data), np.min(y_data), np.max(y_data)])

#         ax0.set_xlabel(x_label)
#         ax0.set_ylabel(y_label)

#         ax0.set_title(title)

#         if y_symlog:
#             ax0.set_yscale("symlog", linthresh=lin_log)
#         elif y_log:
#             ax0.set_yscale("log")


#         ax1.plot(x_data,z_data.T)
#         ax1.set_ylabel("Eigenvalue")
#         ax1.set_title("Singular Values")
#         ax1.set_xlabel("Eigenvalue Index")

#         ax2.plot(z_data,y_data)
#         ax2.set_yscale("log")
#         ax2.set_title("Left Singular Vectors")
#         ax2.set_ylabel("delay / ps")
#         ax2.axvline(0,lw=0.5,color="black")

#         line = ax0.axvline(480, color="black", linestyle="-.")
#         line2 = ax0.axhline(0, color="black", linestyle="dotted")
#         return(fig0,fig1,fig2,line, line2)

#     def test(self):
#         figs = self.plot()
#         self.popup = pu.Multi_Plot_Display(figs)
#         self.popup.show()

class Main(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.btn = QPushButton("test")
        self.btn.clicked.connect(lambda: self.test())
        self.layout.addWidget(self.btn)

    def mouse_move(self, event):
        x, y = event.xdata, event.ydata
        if y:
            self.popup.no_func(y)
        if x:
            self.popup.no_func2(x)

    def plot(self):
        x_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_lambda.txt"
        y_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_delays.txt"
        z_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_taspectra.txt"
        cutting = True
        x_range = [480,1100]
        y_range = [0.2, 3000]

        #PLOT

        figsize = (6, 4)
        dpi = 100

        contour = True
        contour_lines = 20

        y_symlog = True
        lin_log = 10

        y_log = False

        x_label = "$\\lambda$ / nm"
        y_label = "delay / ps" # μs

        title = "Full Data Heatmap"

        v_min = None
        v_max = None

        '''
        Script start
        '''

        #Getting the Data

        x_data = np.genfromtxt(x_data_path).T
        y_data = np.genfromtxt(y_data_path).T
        z_data = np.genfromtxt(z_data_path).T

        #Cutting the Data
        if cutting:
            x_lv = (x_data >= x_range[0]) & (x_data <= x_range[1])
            y_lv = (y_data >= y_range[0]) & (y_data <= y_range[1])
            x_data = x_data[x_lv]
            y_data = y_data[y_lv]
            z_data = z_data[:,x_lv]
            z_data = z_data[y_lv,:]

        X, Y = np.meshgrid(x_data, y_data)


        #Plotting

        fig0, ax0 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")
        plt.connect('motion_notify_event', self.mouse_move)
        fig1, ax1 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")
        fig2, ax2 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")

        if v_min is None:
            v_min = np.min(z_data)
        if v_max is None:
            v_max = np.max(z_data)

        ##Full Data Heatmap
        pcm = ax0.pcolormesh(x_data, y_data, z_data, cmap=plt.cm.seismic, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max), shading="auto")

        if contour:
            ax0.contour(x_data, y_data, z_data, levels=np.arange(v_min, v_max, (1 / contour_lines) * (v_max - v_min)), colors="black", linewidths=0.7, linestyles="solid")
        else:
            ax0.contourf(X,Y, z_data, cmap = 'seismic', levels=np.arange(v_min, v_max, (1 / contour_lines) * (v_max - v_min)), alpha=0.7, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max))

        ax0.axis([np.min(x_data), np.max(x_data), np.min(y_data), np.max(y_data)])

        ax0.set_xlabel(x_label)
        ax0.set_ylabel(y_label)

        ax0.set_title(title)

        if y_symlog:
            ax0.set_yscale("symlog", linthresh=lin_log)
        elif y_log:
            ax0.set_yscale("log")


        line_ax1 = ax1.plot(x_data,z_data[0])
        ax1.set_ylabel("$\\Delta$ Abs. / a.u.")
        ax1.set_title("Spectral Trace")
        ax1.set_xlabel("$\\lambda$ / nm")
        ax1.set_xmargin(0)
        ax1.margins(x=0)

        line_ax2 = ax2.plot(z_data.T[0],y_data)
        ax2.set_yscale("log")
        ax2.set_title("Time Trace")
        ax2.set_ylabel("delay / ps")
        ax2.set_xlabel("$\\Delta$ Abs. / a.u.")
        ax2.axvline(0,lw=0.5,color="black")
        ax2.margins(x=0)

        line_ax2_in_ax0 = ax0.axvline(480, color="black", linestyle="-.")
        line_ax1_in_ax0 = ax0.axhline(0, color="black", linestyle="dotted")


        return(fig0,fig1,fig2,line_ax1_in_ax0,line_ax2_in_ax0, line_ax1, line_ax2)


    def test(self):
        figs = self.plot()
        self.popup = pu.Multi_Plot_Display(figs)
        self.popup.show()

if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setStyle('Fusion')
    mainwindow = Main()
    mainwindow.show()
    sys.exit(app.exec_())