import os

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

        Parameters
        ----------
        path : string
            Path where the folder with the files is located.

        Returns
        -------
        None.

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
    
    def get_ChirpData(self):
        """
        Method that loads the needed data from the given folder path for the
        Chirp object.

        Parameters
        ----------
        path : string
            Path where the folder with the files is located.

        Returns
        -------
        None.

        """
        file_paths = []
        content = os.listdir(self.path)
        for file in content:
            file_paths.append(f'{self.path}/{file}')
        for i in file_paths:
            if "GATE.dat" in i:
                new = i[:-3] + "txt"
                os.rename(i, new)
                gate_filename = new
            elif "LM.dat" in i:
                new = i[:-3] + "txt"
                os.rename(i, new)
                lm_filename = new
            elif "sample.dat" in i:
                new = i[:-3] + "txt"
                os.rename(i, new)
                sample_filename = new
                
        return gate_filename, lm_filename, sample_filename