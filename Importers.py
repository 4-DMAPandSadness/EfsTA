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
        self.get_data(path)

    def get_data(self, path):
        """
        Method that loads the needed data from the given folder path into
        the class.

        Parameters
        ----------
        path : string
            Path where the folder with the files is located.

        Returns
        -------
        None.

        """
        file_paths = []
        content = os.listdir(path)
        for file in content:
            file_paths.append(f'{path}/{file}')
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