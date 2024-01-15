import numpy as np
import scipy.optimize as sco
import matplotlib.pyplot as plt
from matplotlib import path
from matplotlib.widgets import Lasso
from matplotlib import colors as mcolors


class LassoSelector:
    def __init__(self, spec_wave, chirp_wave, centers, corr):
        """
        Initializes a LassoSelector object containing a figure displaying
        the chirp to select data points.

        Parameters
        ----------
        spec_wave : np.array
            The wavelengths of the entire sample measurement.
        chirp_wave : np.array
            The wavelengths of the chirp / OKE meaasurement.
        centers : np.array
            The minima for each chirp_wave spectrum.
        corr : ChirpCorrector
            The ChirpCorrector object in which the LassoSelector was
            initialized.

        Returns
        -------
        None.

        """
        self.corr = corr
        self.fig, self.ax = plt.subplots()
        self.collection = self.ax.scatter(chirp_wave, centers, marker='o')
        self.collection.set(alpha=0.5, clim=[0, 1], cmap=mcolors.ListedColormap(["tab:blue", "tab:red"]), edgecolor="black", label="centers")
        self.ax.legend(loc='lower right')
        self.ax.set_title("Please select the data points for the curve fit by pressing and holding the left mouse button and draging the cursor around the data points. \n Press ENTER once you are finished.")
        self.spec_wave = spec_wave
        self.fig.canvas.mpl_connect('key_press_event', self.on_Enter)
        canvas = self.ax.figure.canvas
        canvas.mpl_connect('button_press_event', self.on_press)
        canvas.mpl_connect('button_release_event', self.on_release)

    def callback(self, verts):
        """
        Saves the data points selected by the lasso.

        Parameters
        ----------
        verts : list
            A collection of (x,y) coordinate tuples of the selected data inside
            of the lasso.

        Returns
        -------
        None.

        """
        self.data = self.collection.get_offsets()
        self.collection.set_array(path.Path(verts).contains_points(self.data))
        canvas = self.collection.figure.canvas
        canvas.draw_idle()
        del self.lasso

    def on_press(self, event):
        """
        On pressing the mouse button creates a lasso.

        Parameters
        ----------
        event : mouse press event
            The event triggerd by pressing the mouse button.

        Returns
        -------
        None.

        """
        canvas = self.collection.figure.canvas
        if event.inaxes is not self.collection.axes or canvas.widgetlock.locked():
            return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        canvas.widgetlock(self.lasso)

    def on_release(self, event):
        """
        On releasing the mouse button stops the lasso.

        Parameters
        ----------
        event : mouse press event
            The event triggerd by pressing the mouse button.

        Returns
        -------
        None.

        """
        canvas = self.collection.figure.canvas
        if hasattr(self, 'lasso') and canvas.widgetlock.isowner(self.lasso):
            canvas.widgetlock.release(self.lasso)

    def fitCurve(self, centers):
        """
        Fits a curve to the selected data points and plots the curve.

        Parameters
        ----------
        centers : np.array
            The the minima of the spectrum of each wavelength of the
            OKE / Chirp measurement.

        Returns
        -------
        None.

        """
        if len(self.ax.lines) > 1:
            self.ax.lines.clear()
        fitfun = lambda x, a1, a2, a3: a1 + 1e5 * a2 / x**2 + 1e6 * a3 / x**4
        self.popt, pcov = sco.curve_fit(fitfun, centers[0], centers[1])
        self.shift = fitfun(self.spec_wave, *self.popt)
        self.ax.plot(centers[0], fitfun(centers[0], *self.popt), 'k-', label=f"a + 10**5*b/x**2 + 10**6*c/x**4 \n a = {round(self.popt[0])}, b = {round(self.popt[1])}, c = {round(self.popt[2])}")
        self.ax.legend(loc='lower right')
        self.fig.canvas.draw_idle()

    def on_Enter(self, event):
        """
        Fits a curve to the selected data points and hands over the curvefit
        parameters to the ChirpCorrector object and starts the correction.

        Parameters
        ----------
        event : button press event
            The event trigged by pressing any button.

        Returns
        -------
        None.

        """
        if event.key == "enter":
            if self.collection.get_array().any():
                self.fitCurve(self.data[self.collection.get_array()].T)
                self.corr.popt = self.popt
                self.corr.correctShift(self.shift)


class AutoSelector:
    def __init__(self, spec_wave, chirp_wave, centers):
        """
        Initializes an AutoSelector object which automatically removes data
        spikes.

        Parameters
        ----------
        spec_wave : np.array
            The wavelengths of the entire sample measurement.
        chirp_wave : np.array
            The wavelengths of the chirp / OKE meaasurement.
        centers : np.array
            The minima for each chirp_wave spectrum.

        Returns
        -------
        None.

        """
        self.spec_wave = spec_wave
        self.chirp_wave = chirp_wave
        self.centers = centers

    def removeSpikes(self):
        """
        Removes data spikes by if the difference between two consecutive
        values is greater than 0.2 and removing them.

        Returns
        -------
        ns_wave : np.array
            The wavelengths without wavelengths where spikes were detected.
        ns_centers : np.array
            The centers without the spikes.

        """
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
        """
        Makes sure that only spikes and not the following value whos difference
        is also greater than 0.2 are deleted by setting the difference of the
        spike following value to 0.

        Parameters
        ----------
        diff : np.array
            The array containing all the differences.
        centers : np.array
            The the minima of the spectrum of each wavelength of the
            OKE / Chirp measurement.

        Returns
        -------
        diff : np.array
            The array containing all the differences with the spike follow
            value difference set to 0.

        """
        idx = 0
        diff_len = len(diff)
        while idx < diff_len - 1:
            if diff[idx] > 0.2:
                temp_idx = idx + 1
                while temp_idx < diff_len and abs(centers[idx - 1] - centers[temp_idx]) > 0.2:
                    temp_idx += 1
                if temp_idx < diff_len and diff[temp_idx] != 0:
                    diff[temp_idx] = 0
                idx = temp_idx
            else:
                idx += 1
        return diff

    def fitCurve(self, ns_wave, ns_centers):
        """
        Fits a curve to the selected data points and plots the curve.

        Parameters
        ----------
        ns_wave: np.array
            The wavelengths without wavelengths where spikes were detected.
        ns_centers : np.array
            The the minima of the spectrum of each wavelength of the
            OKE / Chirp measurement without the spikes.

        Returns
        -------
        shift : np.array
            The temporal shift for each wavelength.
        popt : np.array
            The curvefit parameters.

        """
        fitfun = lambda x, a1, a2, a3: a1 + 1e5 * a2 / x**2 + 1e6 * a3 / x**4
        popt, pcov = sco.curve_fit(fitfun, ns_wave, ns_centers)
        shift_plot = fitfun(ns_wave, *popt)
        shift = fitfun(self.spec_wave, *popt)
        plt.figure()
        plt.plot(self.chirp_wave, self.centers, '.', markersize="10", mfc='none', color="blue", label="Centers with spikes", alpha=0.5)
        plt.plot(ns_wave, ns_centers, '.', markersize="10", mfc='none', color="red", label="Centers without spikes", alpha=0.7)
        plt.plot(ns_wave, shift_plot, 'k-', label=f"a + 10**5*b/x**2 + 10**6*c/x**4 \n a = {round(popt[0])}, b = {round(popt[1])}, c = {round(popt[2])}")
        plt.show()
        plt.legend(loc='lower right')
        return shift, popt


class CurveClicker:
    def __init__(self, wave, time, spec, corr):
        """
        Initializes a CurveClicker object containing a figure displaying
        the sample measurement to select data points to form the chirp curve.

        Parameters
        ----------
        wave : np.array
            The wavelengths of the sample measurement.
        time : np.array
            The dalays of the sample measurement.
        spec : np.ndarray
            The spectral data of the sample measurement.
        corr : ChirpCorrector
            The ChirpCorrector object in which the CurveClicker was
            initialized.

        Returns
        -------
        None.

        """
        self.chirp = []
        self.wave = wave
        self.corr = corr
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1)
        X, Y = np.meshgrid(self.wave, time)
        self.ax1.contourf(X, Y, spec, cmap="seismic")
        self.ax1.set_yscale('symlog')
        self.ax1.set_title("Sample Measurement from -1 to +1 ps \n Please select multiple points along the chirp by left-clicking. \n Press ENTER once you are finished.")
        self.fig.canvas.mpl_connect('key_press_event', self.on_Enter)
        self.fig.canvas.mpl_connect('button_press_event', self.on_Click)

    def on_Click(self, event):
        """
        Saves the point where the click was registered and plots the point
        for visual confirmation.

        Parameters
        ----------
        event : mouse click event
            The event triggered by a mouse click.

        Returns
        -------
        None.

        """
        if event.xdata is not None and event.ydata is not None:
            self.chirp.append([event.xdata, event.ydata])
            self.ax1.scatter(event.xdata, event.ydata, color="black", marker='o')
            self.fig.canvas.draw_idle()

    def on_Enter(self, event):
        """
        Plots all selected points in another axes and fits a curve to them.

        Parameters
        ----------
        event : button press event
            The event triggered by pressing any button.

        Returns
        -------
        None.

        """
        if event.key == "enter":
            self.chirp = np.array(self.chirp)
            self.chirp = self.chirp.T
            self.ax2.scatter(self.chirp[0], self.chirp[1])
            self.fig.canvas.draw_idle()
            shift = self.fitCurve(self.chirp[0], self.chirp[1])
            self.corr.correctShift(shift)

    def fitCurve(self, xs, ys):
        """
        Fits a curve to the selected data points and plots the curve.

        Parameters
        ----------
        xs : np.array
            The wavelengths of the chirp points.
        ys : np.array
            The delays of the chirp points.

        Returns
        -------
        shift : np.array
            The temporal shift of each wavelength.

        """
        fitfun = lambda x, a1, a2, a3: a1 + 1e5 * a2 / x**2 + 1e6 * a3 / x**4
        popt, pcov = sco.curve_fit(fitfun, xs, ys)
        ploty = fitfun(xs, *popt)
        shift = fitfun(self.wave, *popt)
        self.corr.popt = popt
        self.ax2.plot(xs, ploty, 'k-', label=f"a + 10**5*b/x**2 + 10**6*c/x**4 \n a = {round(popt[0])}, b = {round(popt[1])}, c = {round(popt[2])}")
        self.ax2.legend()
        return shift
