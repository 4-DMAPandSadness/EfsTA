import os
import numpy as np


class RichertImport:
    @staticmethod
    def get_files(path):
        """
        Method that loads the needed data from the given folder path for the
        Controller object.

        Returns
        -------
        lambdas_filename : string
            A path to a file containing the wavelength data.
        delays_filename : string
            A path to a file containing the delay data.
        spectra_filename : string
            A path to a file containing the absorption data.

        """
        file_paths = []
        content = os.listdir(path)
        for file in content:
            file_paths.append(f'{path}/{file}')
        for i in file_paths:
            if "lambda" in i or "field" in i:
                lambdas_filename = i
            elif "delays" in i or "time" in i:
                delays_filename = i
            elif "taspectra" in i or "eprspectra" in i:
                spectra_filename = i
        return lambdas_filename, delays_filename, spectra_filename
    
    @staticmethod
    def get_data(files):
        values = []
        for file in files:
            values.append(np.genfromtxt(file))
        return values
    
    @staticmethod
    def get_name(file):
        """
        Find the name of the mesured data.

        Parameters
        ----------
        delays_filename : string
            The path to the file for the delay values.

        Returns
        -------
        name : string
            Name of the measured data.

        """
        temp = file[::-1]
        temp = temp.index("/")
        name = file[-temp:-11]
        path = file[:-temp]
        if not os.path.exists(path + 'analysis'):
            os.makedirs(path + 'analysis')
        path = file[:-temp] + "analysis/"
        return name


class RichertOKEImport:
    @staticmethod
    def get_data(path, header):
        """
        Reads the data

        Returns
        -------
        data : np.ndarray
            The measurment data.

        """
        data = np.genfromtxt(path, skip_header=header)
        return data
    
    @staticmethod
    def split_data(data):
        wave = data[0][1:]
        time = data.T[0][1:] * 100
        time = time.round() / 100
        spec = data[1:]
        spec = spec.T[1:]
        return wave, time, spec
