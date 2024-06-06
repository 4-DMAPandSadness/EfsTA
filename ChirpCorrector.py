import numpy as np
import scipy.interpolate as sci
import ChirpSelector as CS
import betterchripselect as bcs
import CurvePrep as CP
import os

class ChirpCorrector():
    def __init__(self, parameters, mainwindow):
        """
        Initializes the ChirpCorrector object which handles the correction of
        the chirped data.

        Parameters
        ----------
        parameters : dict
            A dictionary containing all the input parameters.
        mainwindow : MainWindow
            The mainwindow of the program to continue the analysis after the
            correction is finished.

        Returns
        -------
        None.

        """
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

    def readData(self, path):
        """
        Reads the data

        Parameters
        ----------
        path : string
            The path to the file containing the raw data.

        Returns
        -------
        data : np.ndarray
            The raw data in a single array as read by the readData function..

        """
        data = np.genfromtxt(path, skip_header=self.header)
        return data

    def splitData(self, data):
        """
        Splits the original np.ndarray containing all the data into three
        separate np.array containing only wavelengths, delays and absorptions
        respectively.

        Parameters
        ----------
        data : np.ndarray
            The raw data in a single array as read by the readData function.

        Returns
        -------
        wave : np.array
            The wavelength data of the measurement.
        time : np.array
            The delay data of the measurement.
        spec : np.ndarray
            The absorption data of the measurement.

        """
        wave = data[0][1:]
        time = data.T[0][1:] * 100
        time = time.round() / 100
        spec = data[1:]
        spec = spec.T[1:]
        return wave, time, spec

    def removeNaNinf(self, spec):
        """
        Checks the data for NaN, -inf and inf values and removes the by
        replacing them with previous/following values.

        Parameters
        ----------
        spec : np.ndarray
            The absorption data of the measurement.

        Returns
        -------
        spec : np.ndarray
            The absorption data of the measurement without invalid values.

        """
        nan = ~np.isfinite(spec)
        if nan.ndim == 1:
            print("Warning: removeNaNinf() has detected and removed NaNs / infs in spectra.")
            pos = np.where(nan)[0]
            for i, val in enumerate(pos):
                if val == 0:
                    spec[pos[i]] = spec[pos[i] + 1]
                elif val == len(spec) - 1:
                    spec[pos[i]] = spec[pos[i] - 1]
                else:
                    new_value = (spec[pos[i] + 1] + spec[pos[i] - 1]) / 2
                    spec[pos[i]] = new_value
        elif nan.ndim == 2:
            cols, rows = np.where(nan)
            for i, val in enumerate(cols):
                if val == 0:
                    spec[cols[i], rows[i]] = spec[cols[i] + 1, rows[i]]
                elif val == len(spec) - 1:
                    spec[cols[i], rows[i]] = spec[cols[i] - 1, rows[i]]
                else:
                    new_value = (spec[cols[i] - 1, rows[i]] + spec[cols[i] + 1, rows[i]]) / 2
                    spec[cols[i], rows[i]] = new_value
        else:
            spec = spec
        return spec

    def genLV(self, wave):
        """
        Generates a logical vector for the wavelenth and absorption
        data using the bounds input by the user
        and truncates the wavelength data.

        Parameters
        ----------
        wave : np.array
            The wavelength data of the measurement.

        Returns
        -------
        None.

        """
        if self.wave_range != []:
            self.lv = (wave >= self.wave_range[0]) & (wave <= self.wave_range[1])
            self.wave = wave[self.lv]
        else:
            self.lv = (wave >= 0)
            self.wave = wave[self.lv]

    def truncateSpec(self, spec):
        """
        Truncates the absorption data using the logical vector created in the
        genLV function.

        Parameters
        ----------
        spec : np.ndarray
            The absorption data of the measurement.

        Returns
        -------
        spec : np.ndarray
            The truncated absorption data of the measurement.

        """
        spec = spec[:, self.lv]
        return spec

    def removeBackground(self, spec, background):
        """
        If provided scales the background measurement and subtracts it from the
        other measurements. The scaling factor is calculated according to:
        Lorenc, M., Ziolek, M., Naskrecki, R. et al.Appl Phys B 2002, 74, 19–27.

        Parameters
        ----------
        spec : np.ndarray
            The sample or OKE measurement.
        background : np.ndarray
            The background measurement.

        Returns
        -------
        None.

        """
        if self.scale is None:
            scale = 1
        else:
            scale = (1 - 10**-self.scale) / (2.3 * self.scale)
        return spec - (background * scale)

    def findMinima(self, chirp_wave, chirp_t, chirp_spec):
        """
        Finds and returns the minima of the spectrum of each wavelength of the
        OKE / Chirp measurement.

        Parameters
        ----------
        chirp_wave : np.array
            The wavelengths of the measured spectra.
        chirp_t : np.array
            The delays of the measured spectra.
        chirp_spec : np.ndarray
            The OKE / Chirp measurement.

        Returns
        -------
        centers : np.array
            The the minima of the spectrum of each wavelength of the
            OKE / Chirp measurement.

        """
        centers = np.zeros(len(chirp_wave))
        for i in range(len(chirp_wave) - 1):
            ind = np.argmin(chirp_spec[:, i])
            centers[i] = chirp_t[ind]
        return centers

    def correctShift(self, shift):
        """
        Corrects the temporal shift of the spectral data.

        Parameters
        ----------
        shift : np.array
            The shift for each wavelength calculated in the CurvePrep class.

        Returns
        -------
        None.

        """
        data_c = self.sample_spec.T
        data_cc = np.zeros_like(data_c)
        for i in range(len(data_c)):
            t_shift = self.time + shift[i]
            data_nn = self.removeNaNinf(data_c[i])
            data_cc[i, :] = sci.pchip_interpolate(self.time, data_nn, t_shift)
        self.saveToTxt(self.wave, self.time, data_cc)

    def prepareSample(self):
        """
        Prepares the sample data by reading, splitting, truncating and
        subtracting the background as well as removing any NaN values.

        Returns
        -------
        None.

        """
        data = self.readData(self.sample_dir)
        wave, self.time, spec = self.splitData(data)
        self.genLV(wave)
        if self.options["Scatter"] is True and self.exc_wave is not None:
            spec = self.scattering(spec)
        spec_NN = self.removeNaNinf(spec).T
        spec_trunc = self.truncateSpec(spec_NN)
        if self.options["rmBG"] is True:
            self.prepareBackground()
            self.sample_spec = self.removeBackground(spec_trunc, self.background)
        else:
            self.sample_spec = spec_trunc

    def prepareBackground(self):
        """
        Prepares the background data by reading, splitting and truncating
        as well as removing any NaN values.

        Returns
        -------
        None.

        """
        data = self.readData(self.solvent_dir)
        wave, bg_time, spec = self.splitData(data)
        spec_NN = self.removeNaNinf(spec).T
        self.background = self.truncateSpec(spec_NN)
   
    def prepareChirp(self):
        """
        Reads and prepares the OKE / Chirp data.
        If no OKE / Chirp measurement is provided initiates a CurveClicker
        object to manually define the Chirp.
        If an OKE / Chirp measurement is provided initiates a ChirpSelector
        object to select the Chirp area.

        Returns
        -------
        None.

        """
        if self.options["OKE"] is False:
            lv_t = (self.time >= -5) & (self.time <= 5)
            t = self.time[lv_t]
            select_spec = self.sample_spec[lv_t, :]
            self.CPC = CP.CurveClicker(self.wave, t, select_spec, self)
        else:
            data = self.readData(self.chirp_dir)
            wave, chirp_time, spec = self.splitData(data)
            spec_NN = self.removeNaNinf(spec).T
            spec_NN = self.truncateSpec(spec_NN)
            lv_t = (chirp_time >= -1) & (chirp_time <= 1)
            chirp_t = chirp_time[lv_t]
            chirp_spec = spec_NN[lv_t, :]
            #selector = CS.ChirpSelector(self.wave, chirp_t, chirp_spec, self)
            self.selector = bcs.ChirpSelector(self.wave, chirp_t, chirp_spec, self)
            self.selector.show()
            
    def prepareFitting(self, chirp_wave, chirp_t, sel_spec):
        """
        Allows for the automatic removal of data spikes or for the manual
        selection of viable data points.

        Parameters
        ----------
        chirp_wave : np.array
            The wavelengths of the measured spectra.
        chirp_t : np.array
            The delays of the measured spectra.
        sel_spec : np.ndarray
            The selected ranges of the OKE / Chirp measurement.

        Returns
        -------
        None.

        """
        centers = self.findMinima(chirp_wave, chirp_t, sel_spec)
        if self.options["Manually"] is True:
            self.CPL = CP.LassoSelector(self.wave, chirp_wave, centers, self)
        else:
            CPA = CP.AutoSelector(self.wave, chirp_wave, centers)
            ns_wave, ns_centers = CPA.removeSpikes()
            shift, self.popt = CPA.fitCurve(ns_wave, ns_centers)
            self.correctShift(shift)

    def scattering(self, spec):
        """
        Corrects scattering around the excitation wavelength by averaging the
        first few spectra around +- 20 nm of the excitation wavelength.

        Parameters
        ----------
        spec : np.ndarray
            The spectral measurement data of the sample.

        Returns
        -------
        data : np.ndarray
            The scatter corrected spectral measurement data of the sample.

        """
        scatter = np.zeros(len(self.wave))
        lv = (self.wave >= self.exc_wave - 20) & (self.wave <= self.exc_wave + 20)
        tmp = np.mean(spec[:, -11:], axis=1)
        scatter[lv] = tmp[lv]
        data = spec - np.tile(scatter, (1, len(self.time)))
        return data

    def saveToTxt(self, corr_wave, corr_time, corr_spec):
        """
        Saves the corrected and truncated wavelengths, delays, spectral data
        and the curveFit_Parameters as *.txt files in the format expected by
        the EfsTA standard import function. Hands over the new directory of the
        corrected data to the EfsTA object and reads the data, so that an
        anaysis may be performed.

        Parameters
        ----------
        corr_wave : np.array
            The corrected and truncated wavelengths.
        corr_time : np.array
            The corrected and truncated delays.
        corr_spec : np.ndarray
            The corrected and truncated spectral data.

        Returns
        -------
        None.

        """
        file = self.sample_dir.split("/")[-1].split(".")[0]
        path = "/".join(self.sample_dir.split("/")[:-1])
        save_path = f"{path}/corrected_Data/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        np.savetxt(f"{save_path}{file}_taspectra.txt", corr_spec, encoding='-ascii')
        np.savetxt(f"{save_path}{file}_delays.txt", corr_time, encoding='-ascii')
        np.savetxt(f"{save_path}{file}_lambda.txt", corr_wave, encoding='-ascii')
        np.savetxt(f"{save_path}{file}_curveFit_Parameters.txt", self.popt, encoding='-ascii')
        self.mainwindow.ui.Data_directory.setText(save_path)
        self.mainwindow.readData(save_path)
        self.mainwindow.ui.UI_stack.setCurrentIndex(3)

    def correctData(self):
        """
        Starts the data correction process.

        Returns
        -------
        None.

        """
        self.prepareSample()
        self.prepareChirp()
