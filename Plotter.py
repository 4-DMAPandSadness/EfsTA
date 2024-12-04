import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib.ticker as mticker
import numpy as np

class Plotter:
    def __init__(self, style_path, lambdas, delays, spectra, path, name):
        plt.style.use(style_path)  # stylesheet
        self.lambdas = lambdas
        self.delays = delays
        self.spectra = spectra
        self.path = path
        self.name = name
    
    @staticmethod
    def log_tick_formatter(val, pos):
        return r"$10^{{{:.0f}}}$".format(val)

    @staticmethod
    def set_v_min(data, mul):
        return np.min(data) * mul

    @staticmethod
    def set_v_max(data, mul):
        return np.max(data) * mul

    @staticmethod
    def find_nearest_index(slices, data):
        slices = np.array(slices)
        return [np.argmin(np.abs(data - val)) for val in slices]

    def plot1(self, grid, wave, wave_index, spectra, mul, labels):
        ltx = str(mul).count("0")
        unit = labels[0].split("/")[1] if "/" in labels[0] else ""
        dot = f" $\cdot 10^{ltx}$" if mul != 1 else ""
        
        ax1 = plt.subplot(grid[0, 0])
        ax1.set_yscale("log")
        ax1.set_xlabel(labels[2] + dot)
        ax1.set_ylabel(labels[1])

        for i, ind in enumerate(wave_index):
            ax1.plot(self.delays, spectra[ind], label=f"{wave[i]} {unit}")
        
        ax1.axvline(0, color="black", lw=0.5, alpha=0.75)
        temp = np.concatenate([spectra[i] for i in wave_index])
        ax1.axis([1.05 * np.min(temp), 1.05 * np.max(temp), np.min(self.delays), np.max(self.delays)])
        ax1.set_xticks(())
        ax1.tick_params(bottom=False)
        ax1.legend(loc="upper left", frameon=False, labelcolor="linecolor", handlelength=0, fontsize=11)

    def plot2(self, grid, wave, time, v_min, v_max, spectra, add, cont, mul, labels):
        ax2 = plt.subplot(grid[0, 1])
        ax2.set_yscale("log")
        ax2.set_xlabel(labels[0])
        A_t = spectra.T * mul
        
        if v_min is None:
            v_min = self.set_v_min(spectra, mul)
        if v_max is None:
            v_max = self.set_v_max(spectra, mul)
        
        pcm = ax2.pcolormesh(self.lambdas, self.delays, A_t, cmap=plt.cm.seismic, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max), shading="auto")
        cb = plt.colorbar(pcm)
        cb.set_ticks([v_min, 0, v_max])
        cb.set_label(labels[2])

        ax2.contour(self.lambdas, self.delays, A_t, levels=np.arange(v_min, v_max, (1 / cont) * (v_max - v_min)), colors="black", linewidths=0.7, linestyles="solid")

        for w in wave:
            ax2.axvline(w, color="black", linestyle="-.")
        for t in time:
            ax2.axhline(t, color="black", linestyle="dotted")

        ax2.axis([np.min(self.lambdas), np.max(self.lambdas), np.min(self.delays) if np.min(self.delays) > 0 else 10**-2, np.max(self.delays)])
        ax2.set_yticks(())
        return ax2, cb

    def plot3(self, grid, time, time_index, spectra, mul, labels):
        """Plot a subplot of absorption change against wavelengths for chosen delays."""
        ltx = str(mul).count("0")
        unit = labels[1].split("/")[1] if "/" in labels[1] else ""
        dot = f" $\cdot 10^{ltx}$" if mul != 1 else ""
        
        ax3 = plt.subplot(grid[0, 2])
        ax3.set_ylabel(labels[2] + dot)
        ax3.set_xlabel(labels[0])

        y = np.zeros(len(self.lambdas))
        hoehe = 0
        temp = np.zeros(len(self.lambdas))
        for i, ind in enumerate(time_index):
            for j in range(len(self.lambdas)):
                temp[j] = spectra[j][ind]
                y[j] = temp[j] + hoehe
            if ind == time_index[0]:
                mini = np.min(y)
            ax3.plot(self.lambdas, y, color="black")
            ax3.annotate(f"{time[i]} {unit}", (0.5 * (np.min(self.lambdas) + np.max(self.lambdas)), hoehe))
            ax3.axhline(hoehe, color="black", lw=0.5, alpha=0.75)
            hoehe += 1.1 * (np.abs(np.max(temp)) + np.abs(np.min(temp)))
        
        ax3.axis([np.min(self.lambdas), np.max(self.lambdas), 1.1 * mini, 1.1 * np.max(y)])
        ax3.set_yticks(())

    def plot3D(self, spectra, v_min, v_max, mul, labels, add = ""):
        """Create a 3D contour plot."""
        fig, ax = plt.subplots(figsize=(11.2, 8), subplot_kw={"projection": "3d"})
        log_delay = np.log10(np.abs(self.delays))
        ltx = str(mul).count("0")
        dot = f" $\cdot 10^{ltx}$" if mul != 1 else ""

        if v_min is None:
            v_min = self.set_v_min(spectra, mul)
        if v_max is None:
            v_max = self.set_v_max(spectra, mul)

        X, Y = np.meshgrid(self.lambdas, log_delay)
        Z = spectra.T * mul
        ax.contour3D(X, Y, Z, 80, cmap='seismic')
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        ax.set_zlabel(labels[0] + dot)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(self.log_tick_formatter))
        yticks = np.linspace(np.min(log_delay), np.max(log_delay), 4)
        yticks[0] = -1
        ax.set_yticks(yticks)
        ax.view_init(20, 250)
        plt.savefig(self.path + self.name + "3DContour" + ".png")
        return fig

    def plot3inOne(self, spectra, wave, time, v_min, v_max, cont, mul, labels, add = ""):
        if v_min is None:
            v_min = self.set_v_min(spectra, mul)
        if v_max is None:
            v_max = self.set_v_max(spectra, mul)

        wave_index = self.find_nearest_index(wave, self.lambdas)
        time_index = self.find_nearest_index(time, self.delays)

        fig = plt.figure(figsize=(9, 3), constrained_layout=False, frameon=True)
        grid = plt.GridSpec(1, 3, wspace=0, width_ratios=[1.0, 1.2, 1.0])

        if wave:
            self.plot1(grid, wave, wave_index, spectra, mul, labels)
        if wave and time:
            ax2, cb = self.plot2(grid, wave, time, v_min, v_max, spectra, add, cont, mul, labels)
        if time:
            self.plot3(grid, time, time_index, spectra, mul, labels)

        plt.subplots_adjust(wspace=0.25)
        plt.savefig(self.path + self.name + ".png")
        return fig



    def plot_data(self, x, y, x_label, y_label, label, add = ""):
        fig, ax = plt.subplots()
        temp = y.flatten()
        ax.axis([min(x), max(x), 1.1 * min(temp), 1.1 * max(temp)])
        ax.plot(x, y)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        
        if add in ("_GTA_kin", "_GLA_kin"):
            ax.set_xscale("log")
            fig.set_size_inches(7.6, 4)
        else:
            ax.axhline(0, color="black", lw=0.5, alpha=0.75)
        
        if label:
            ax.legend([label], frameon=False, labelcolor="linecolor", handlelength=0, loc="lower right")
        
        plt.savefig(self.path + self.name + add + ".png", bbox_inches="tight")
        return fig

    def plot_w_slices(self, wave, spectra, mul, labels, add = ""):
        fig, ax = plt.subplots()
        wave_index = self.find_nearest_index(wave, self.lambdas)
        ltx = str(mul).count("0")
        unit = labels[0].split("/")[1] if "/" in labels[0] else ""
        dot = f" $\cdot 10^{ltx}$" if mul != 1 else ""
        
        ax.set_xscale("log")
        ax.set_ylabel(labels[2] + dot)
        ax.set_xlabel(labels[1])
        
        for i, ind in enumerate(wave_index):
            ax.plot(self.delays, spectra[ind], label=f"{wave[i]} {unit}")
        
        temp = np.concatenate([spectra[i] for i in wave_index])
        ax.axis([min(self.delays), max(self.delays), 1.05 * min(temp), 1.05 * max(temp)])
        ax.axhline(0, color="black", lw=0.5, alpha=0.75)
        ax.set_yticks(())
        ax.tick_params(bottom=False)
        ax.legend(loc="upper right", frameon=False, labelcolor="linecolor", handlelength=0)
        
        plt.savefig(self.path + self.name + "Wavelength_Slices" + ".png")
        return fig

    def plot_heat(self, wave, time, v_min, v_max, spectra, cont, mul, labels, add = ""):
        fig, ax = plt.subplots(figsize=(7.6, 4))
        ltx = str(mul).count("0")
        dot = f" $\cdot 10^{ltx}$" if mul != 1 else ""
        
        ax.set_yscale("log")
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        A_t = spectra.T * mul

        if v_min is None:
            v_min = self.set_v_min(spectra, mul)
        if v_max is None:
            v_max = self.set_v_max(spectra, mul)

        pcm = ax.pcolormesh(self.lambdas, self.delays, A_t, cmap=plt.cm.seismic, norm=col.TwoSlopeNorm(vcenter=0, vmin=v_min, vmax=v_max), shading="auto")
        cb = plt.colorbar(pcm)
        cb.set_ticks([v_min, 0, v_max])
        cb.set_label(labels[2] + dot)
        
        ax.contour(self.lambdas, self.delays, A_t, levels=np.arange(v_min, v_max, (1 / cont) * (v_max - v_min)), colors="black", linewidths=0.7, linestyles="solid")

        for w in wave:
            ax.axvline(w, color="black", linestyle="-.")
        for t in time:
            ax.axhline(t, color="black", linestyle="dotted")

        ax.axis([min(self.lambdas), max(self.lambdas), min(self.delays) if min(self.delays) > 0 else 10**-2, max(self.delays)])
        ax.set_xticks(())

        plt.savefig(self.path + self.name + ("Residuals" if "Residuals" in add else "Heatmap") + ".png")
        return fig

    def plot_d_slices(self, time, spectra, mul, labels, add = ""):
        fig, ax = plt.subplots()
        time_index = self.find_nearest_index(time, self.delays)
        ltx = str(mul).count("0")
        unit = labels[1].split("/")[1] if "/" in labels[1] else ""
        dot = f" $\cdot 10^{ltx}$" if mul != 1 else ""

        ax.set_ylabel(labels[2] + dot)
        ax.set_xlabel(labels[0])
        
        for i, ind in enumerate(time_index):
            ax.plot(self.lambdas, spectra.T[ind], label=f"{time[i]} {unit}")
        
        temp = np.concatenate([spectra.T[i] for i in time_index])
        ax.axis([min(self.lambdas), max(self.lambdas), 1.05 * min(temp), 1.05 * max(temp)])
        ax.set_yticks(())
        ax.axhline(0, color="black", lw=0.5, alpha=0.75)
        ax.tick_params(bottom=False)
        ax.legend(loc="upper left", frameon=False, labelcolor="linecolor", handlelength=0)

        plt.savefig(self.path + self.name + "Delay_Slices" + ".png")
        return fig
