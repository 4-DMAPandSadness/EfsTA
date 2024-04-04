import os
import numpy as np


class RichertImport():
    def __init__(self, path):
        """
        Initiates the controller and loads the data from the given path.

        Parameters
        ----------
        path : string
            Path where the folder containing the data is located.

        Returns
        -------
        None.

        """
        self.path = path

    def get_Data(self):
        """
        Method that loads the needed data from the given folder path for the
        Controller object.

        Returns
        -------
        lambdas_filename : string
            DESCRIPTION.
        delays_filename : string
            DESCRIPTION.
        spectra_filename : string
            DESCRIPTION.

        """
        file_paths = []
        content = os.listdir(self.path)
        for file in content:
            file_paths.append(f'{self.path}/{file}')
        for i in file_paths:
            if "lambda" in i or "field" in i:
                new = i[:-3] + "txt"
                os.rename(i, new)
                lambdas_filename = new
            elif "delays" in i or "time" in i:
                new = i[:-3] + "txt"
                os.rename(i, new)
                delays_filename = new
            elif "taspectra" in i or "eprspectra" in i:
                new = i[:-3] + "txt"
                os.rename(i, new)
                spectra_filename = new
        return lambdas_filename, delays_filename, spectra_filename


class RichertOKEImport():
    def __init__(self, path):
        """
        Initiates the controller and loads the data from the given path.

        Parameters
        ----------
        path : string
            The path of the file containing the data.

        Returns
        -------
        None.

        """
        self.path = path

    def readData(self):
        """
        Reads the data

        Returns
        -------
        data : np.ndarray
            The measurment data.

        """
        data = np.genfromtxt(self.path, delimiter=' ', skip_header=self.header)
        return data

    def splitData(self, data):
        wave = data[0][1:]
        time = data.T[0][1:] * 100
        time = time.round() / 100
        spec = data[1:]
        spec = spec.T[1:]
        return wave, time, spec
