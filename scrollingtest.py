import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as col
from matplotlib.widgets import SpanSelector
'''
Script inputs
'''

#DATA

# #H2TPP
# x_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/3_HTP-tol_100uM_420exc/corrected_Data/HTP_avg_lambda.txt"
# y_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/3_HTP-tol_100uM_420exc/corrected_Data/HTP_avg_delays.txt"
# z_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/3_HTP-tol_100uM_420exc/corrected_Data/HTP_avg_taspectra.txt"

#HTPCz
x_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_lambda.txt"
y_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_delays.txt"
z_data_path = "/home/hackerman/Documents/Master of Science/4.Semester WS24/fsTA/1_HTPCz-tol_100uM_420exc/corrected_Data/HTPCz_dOD_avg_taspectra.txt"

data_multiplier = 1000

cutting = True
x_range = [480,1100]
y_range = [0.2, 3000]

trEPR = True

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

if data_multiplier == 1:
    colorbar_label = "$\\Delta A$ / a.u."
else:
    zeros = str(data_multiplier).count("0")
    colorbar_label = f"$\\Delta A \\cdot 10^{zeros}$ / a.u."

x_slice = []
y_slice = []

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
fig1, ax1 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")
fig2, ax2 = plt.subplots(nrows=1, ncols=1, figsize = figsize, dpi = dpi, layout = "constrained")

if v_min is None:
    v_min = np.min(z_data)
if v_max is None:
    v_max = np.max(z_data)


def plot():
    ##Full Data Heatmap
    pcm = ax0.pcolormesh(x_data, y_data, z_data, cmap=plt.cm.seismic, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max), shading="auto")
    # cb = plt.colorbar(pcm)
    # cb.set_ticks([v_min, 0, v_max])
    # cb.set_label(colorbar_label)

    if contour:
        ax0.contour(x_data, y_data, z_data, levels=np.arange(v_min, v_max, (1 / contour_lines) * (v_max - v_min)), colors="black", linewidths=0.7, linestyles="solid")
    else:
        ax0.contourf(X,Y, z_data, cmap = 'seismic', levels=np.arange(v_min, v_max, (1 / contour_lines) * (v_max - v_min)), alpha=0.7, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max))

    for t in x_slice:
        ax0.axvline(t, color="black", linestyle="-.")
    for v in y_slice:
        ax0.axhline(v, color="black", linestyle="dotted")

    ax0.axis([np.min(x_data), np.max(x_data), np.min(y_data), np.max(y_data)])

    ax0.set_xlabel(x_label)
    ax0.set_ylabel(y_label)

    ax0.set_title(title)

    if y_symlog:
        ax0.set_yscale("symlog", linthresh=lin_log)
    elif y_log:
        ax0.set_yscale("log")


    ax1.plot(x_data,z_data.T)
    ax1.set_ylabel("Eigenvalue")
    ax1.set_title("Singular Values")
    ax1.set_xlabel("Eigenvalue Index")

    ax2.plot(z_data,y_data)
    ax2.set_yscale("log")
    ax2.set_title("Left Singular Vectors")
    ax2.set_ylabel("delay / ps")
    ax2.axvline(0,lw=0.5,color="black")

# def update(n_points,indices):
#     ##Left Singular Vectors
#     ax3.clear()
#     ax4.clear()
#     ax3.plot(y_data, SVD[0][:n_points].T)#, label=f"{S[indices]}")
#     ax3.set_xscale("log")
#     ax3.set_title("Left Singular Vectors")
#     ax3.set_xlabel("delay / ps")
#     ax3.axhline(0,lw=0.5,color="black")
#     ##Right Singular Values
#     ax4.plot(x_data, SVD[2][:n_points].T)#, label=f"{S[indices]}")
#     ax4.set_title("Right Singular Vectors")
#     ax4.set_xlabel("$\\lambda$ / nm")
#     ax4.axhline(0,lw=0.5,color="black")

#     ax3.legend()
#     ax4.legend()
#     fig.canvas.draw()
#     fig.canvas.flush_events()

plot()
plt.show()
