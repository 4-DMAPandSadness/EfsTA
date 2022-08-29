from Model import Model
import numpy as np
import os
from pathlib import Path
from datetime import datetime
import shelve


class Controller():

    def __init__(self, path):
        """
        Initiates the controller and loads the data from the given path.

        Parameters
        ----------
        path : string
            Path where the folder with the files is located.

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
            if "lambda.txt" in i:
                self.lambdas_filename = i
            elif "delays.txt" in i:
                self.delays_filename = i
            elif "spectra.txt" in i:
                self.spectra_filename = i

    def calcDAS(self, tau, d_limits, l_limits):
        """
        Calculates the Decay Associated Spectra and outputs the fitted decay
        constants tau, the calculated spectra, the residuals and the DAS.

        Parameters
        ----------
        tau : list
            The decay constants for the DAS.
        d_limits : list with two int/float elements
            Lower and upper limits for the delay values.
        l_limits : list with two int/float elements
            Lower and upper limits for the lambda values.

        Returns
        -------
        tau_fit : list
            The fitted decay constants for the DAS.
        spec : np.array
            The spectra calculated from the fitted tau and the original data.
        res : np.array
            Residuals from the DAS. The difference between the calculated
            and the original spectra.
        D_fit : np.array
            Matrix D with the fitted values for x.

        """
        tau_fix = tau[0]
        tau_guess = tau[1]
        self.DAS = Model(self.delays_filename, self.spectra_filename,
                         self.lambdas_filename, d_limits, l_limits, 0)
        self.DAS.M = self.DAS.getM(np.concatenate((tau_fix, tau_guess)))
        tau_fit = self.DAS.findTau_fit(tau_fix, tau_guess)
        D_fit = self.DAS.calcD_fit()
        spec = self.DAS.calcA_fit()
        res = self.DAS.calcResiduals()
        self.saveResults(0, np.concatenate((tau_fix, tau_guess)), tau_fit,
                         l_limits, d_limits, spec, D_fit,
                         self.DAS.getTauBounds(tau_guess), self.DAS.lambdas,
                         self.DAS.delays, self.DAS.spectra)
        return tau_fit, spec, res, D_fit

    def calcSAS(self, tau, C_0, d_limits, l_limits, model, tau_low, tau_high):
        """
        Calculated the Species Associated Spectra and outputs the fitted
        decay constants tau, the calculated spectra and the residuals.

        Parameters
        ----------
        tau : list/np.array
            The decay constants tau for a model 1-9 or a matrix Tau for a
            "custom" model.
        C_0 : list
            The list that contains values for C_0 set by the user.
            Can be empty.
        d_limits : list with two int/float elements
            Lower and upper limits for the delay values.
        l_limits : list with two int/float elements
            Lower and upper limits for the lambda values.
        model : int/string
            Describes the desired model for the SAS. Can be a number 1-9 or
            "custom" for a custom model.

        Returns
        -------
        tau_fit : list
            The fitted decay constants for the SAS.
        spec : np.array
            The spectra calculated from the fitted tau and the original data.
        res : np.array
            Residuals from the SAS. The difference between the calculated
            and the original spectra.
        D_fit : np.array
            Matrix D with the fitted values for tau.

        """
        self.SAS = Model(self.delays_filename, self.spectra_filename,
                         self.lambdas_filename, d_limits, l_limits, model)
        if model == "custom":
            self.SAS.setTauBounds(tau_low, tau_high, tau)
            M_lin = self.SAS.getM_lin(tau)
            K,n = self.SAS.getK(M_lin)
        else:
            self.SAS.setTauBounds(tau_low, tau_high, tau)
            K,n = self.SAS.getK(tau)
        self.SAS.setInitialConcentrations(C_0)
        self.SAS.solveDiff(self.SAS.K)
        tau_fit = self.SAS.findTau_fit([], tau)
        D_fit = self.SAS.calcD_fit()
        spec = self.SAS.calcA_fit()
        res = self.SAS.calcResiduals()        
        self.saveResults(model, tau, tau_fit, l_limits, d_limits, spec, D_fit,
                         self.SAS.getTauBounds(tau), self.SAS.lambdas,
                         self.SAS.delays, self.SAS.spectra)
        return tau_fit, spec, res, D_fit

    def plot3OrigData(self, wave, time, v_min, v_max, d_limits, l_limits,
                      cont, mul=1):
        """
        Allows the plotting of the original data in a 3-in-1 plot.
        If the lists wave and/or time are empty the corresponding subplots
        won't be plotted.

        Parameters
        ----------
        wave : list
            Can contain 0-10 values for the wavelengths which will be plotted
            in a subplot of delays against absorption change.
        time : list
            Can contain values for the delays which will be plotted in a
            subplot of absorption change against wavelengths.
        v_min : float
            Lower limit for the colorbar.
        v_max : float
            Upper limit for the colorbar.
        d_limits : list with two int/float elements
            Lower and upper limits for the delay values.
        l_limits : list with two int/float elements
            Lower and upper limits for the lambda values.
        cont : float
            Determines how much contour lines will be shown in the 2D plot.
            High values will show more lines.
        mul : float
            The value by which data will be multiplied.

        Returns
        -------
        None.

        """
        if len(list(wave)) <= 0 or len(wave) > 10:
            if len(list(time)) <= 0:
                custom = "2"
            else:
                custom = "2+3"
        elif len(list(time)) <= 0:
            custom = "1+2"
        else:
            custom = "1+2+3"
        origData = Model(self.delays_filename, self.spectra_filename,
                         self.lambdas_filename, d_limits, l_limits, None)
        origData.plotCustom(origData.spectra, wave, time,
                            v_min, v_max, custom, cont, mul=mul)

    def plot3FittedData(self, wave, time, v_min, v_max, model, cont, mul=1):
        """
        Allows the plotting of the fitted data in a 3-in-1 plot.
        If the lists wave and/or time are empty the corresponding subplots
        won't be plotted.

        Parameters
        ----------
        wave : list
            Can contain 0-10 values for the wavelengths which will be plotted
            in a subplot of delays against absorption change.
        time : list
            Can contain values for the delays which will be plotted in a
            subplot of absorption change against wavelengths.
        v_min : float
            Lower limit for the colorbar.
        v_max : float
            Upper limit for the colorbar.
        model : int/string
            Describes the desired model. 0 for the DAS. For SAS it can be a
            number 1-9 or "custom" for a custom model.
        cont : float
            Determines how much contour lines will be shown in the 2D plot.
            High values will show more lines.
        mul : float
            The value by which data will be multiplied.

        Returns
        -------
        None.

        """
        if len(wave) <= 0 or len(wave) > 10:
            if len(time) <= 0:
                custom = "2"
            else:
                custom = "2+3"
        elif len(time) <= 0:
            custom = "1+2"
        else:
            custom = "1+2+3"
        if model == 0:
            self.DAS.plotCustom(self.DAS.spec, wave, time,
                                v_min, v_max, custom, cont, add="_GLA", mul=mul)
        else:
            self.SAS.plotCustom(self.SAS.spec, wave, time,
                                v_min, v_max, custom, cont, add="_GTA", mul=mul)
            
    def createOrigData(self, d_limits, l_limits):
        """
        Creates an object origData to allow the plotting of the original data.

        Parameters
        ----------
        d_limits : TYPE
            DESCRIPTION.
        l_limits : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.origData = Model(self.delays_filename, self.spectra_filename,
                         self.lambdas_filename, d_limits, l_limits, None)
            
    def plotCustom(self, wave, time, v_min, v_max, model, cont, custom, add="",
                   mul=1):
        """
        Allows for the creation of 1-3 subplots in one plot.

        Parameters
        ----------
        wave : list
            Wavelenghts which should be plotted.
        time : list
            Delays which should be plotted.
        v_min : float
            Lower limit for the colorbar.
        v_max : float
            Upper limit for the colorbar.
        model : int/string
            Variable for the choice of model (DAS or which SAS).
        cont : float
            Determines how much contour lines will be shown in the 2D plot.
            High values will show more lines.
        custom : string
            Describes which subplots will be plotted.
        add : string
            Addition to the title of the plot. The default is "".
        mul : float
            The value by which data will be multiplied.

        Returns
        -------
        None.

        """
        if model == None:
            self.origData.plotCustom(self.origData.spectra, wave, time,
                                v_min, v_max, custom, cont, add="_"+add,
                                mul=mul)
        elif model == 0:
            self.DAS.plotCustom(self.DAS.spec, wave, time,
                                v_min, v_max, custom, cont, add="_GLA"+"_"+add,
                                mul=mul)
        else:
            self.SAS.plotCustom(self.SAS.spec, wave, time,
                                v_min, v_max, custom, cont, add="_GTA"+"_"+add,
                                mul=mul)

    def plot1Dresiduals(self, model):
        """
        Allows for the plotting of the residuals in a plot of
        residuals(wavelenght) against the delays.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the DAS. For SAS it can be a
            number 1-9 or "custom" for a custom model.

        Returns
        -------
        None.

        """
        if model == 0:
            self.DAS.plotData(self.DAS.delays, self.DAS.residuals.T,
                              "delays / ps", "$\Delta A \cdot 10^3$",
                              add="_GLA_Residuals_1D")
        else:
            self.SAS.plotData(self.SAS.delays, self.SAS.residuals.T,
                              "delays / ps", "$\Delta A \cdot 10^3$",
                              add="_GTA_Residuals_1D")

    def plot2Dresiduals(self, v_min, v_max, model, cont, mul=1):
        """
        Allows for the ploting of the residuals in a 2D plot.

        Parameters
        ----------
        v_min : float
            Lower limit for the colorbar.
        v_max : float
            Upper limit for the colorbar.
        model : int/string
            Describes the desired model. 0 for the DAS. For SAS it can be a
            number 1-9 or "custom" for a custom model.
        cont : float
            Determines how much contour lines will be shown in the 2D plot.
            High values will show more lines.
        mul : float
            The value by which data will be multiplied.

        Returns
        -------
        None.

        """
        if model == 0:
            self.DAS.plotCustom(self.DAS.residuals, [], [],
                                v_min, v_max, "2", cont,
                                add="_GLA_Residuals_2D", mul=mul)
        else:
            self.SAS.plotCustom(self.SAS.residuals, [], [],
                                v_min, v_max, "2", cont,
                                add="_GTA_Residuals_2D", mul=mul)
            
    def plotKinetics(self, model):
        """
        This method will plot the concentration against the time for the DAS
        or the SAS.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the DAS. For SAS it can be a
            number 1-9 or "custom" for a custom model.

        Returns
        -------
        None.

        """
        if model == 0:
            self.DAS.plotData(self.DAS.delays, self.DAS.M.T, "delays / ps",
                              "concentration", add="_GLA_kin")
        else:
            self.SAS.plotData(self.SAS.delays, self.SAS.M.T, "delays / ps",
                              "concentration", add="_GTA_kin")
            
    def plotDAS(self, model, tau):
        """
        Allows the plotting of the DAS or SAS with the indicated tau_fit
        values.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the DAS. For SAS it can be a
            number 1-9 or "custom" for a custom model.
        tau_fit : list
            The decay constants for the DAS or SAS.

        Returns
        -------
        None.

        """
        tau = list(tau)
        if model == 0:
            self.DAS.plotData(self.DAS.lambdas, self.DAS.D_fit,
                              "$\lambda$ / nm", "$\Delta A \cdot 10^3$", add="_DAS",
                              label = tau)
        elif model == "custom":
            self.SAS.plotData(self.SAS.lambdas, self.SAS.D_fit,
                              "$\lambda$ / nm", "$\Delta A \cdot 10^3$", add="_SAS",
                              label=list(self.SAS.getM_lin(np.array(tau))))
        else:
            self.SAS.plotData(self.SAS.lambdas, self.SAS.D_fit,
                              "$\lambda$ / nm", "$\Delta A \cdot 10^3$", add="_SAS",
                              label=tau)
            
    def saveResults(self, model, tau_start, tau_fit, l_limits, d_limits, A_fit,
                    D_fit, bounds, lambdas, delays, spectra):
        """
        Saves the results of the DAS or SAS at the end of the optimizing in a
        txt file.

        Parameters
        ----------
        model : int/string
           Describes the desired model. 0 for the DAS. For SAS it can be a
           number 1-9 or "custom" for a custom model.
        tau_start : list, np.array
            An array containing the start values for tau.
        tau_fit : list, np.array
            An array containing the fitted tau values.
        l_limits : list with two int/float elements
            Lower and upper limits for the lambda values.
        d_limits : list with two int/float elements
            Lower and upper limits for the delay values.
        A_fit : np.array
            The reconstructed data matrix for the values of tau_fit and x_fix,
            if DAS.
         D_fit : np.array
             Matrix D with the fitted values for tau.

        Returns
        -------
        None.

        """
        if model == 0:
            path = self.DAS.path
            name = self.DAS.name+"_GLA"
            txt = name+"_results.txt"
        else:
            path = self.SAS.path
            name = self.SAS.name+"_GTA"
            txt = name+"_results.txt"
        
        myfile = Path(path+txt)
        myfile.touch(exist_ok=True)
        f = open(myfile, "w")
        
        if model != "custom":
            k_fit = 1/np.array(tau_fit)
        else:
            ones = np.full(tau_fit.shape, 1)
            k_fit = np.divide(ones, tau_fit, out=np.zeros_like(tau_fit), where=tau_fit!=0)
        
        now = datetime.now()
        dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
        
        f.write(dt_string + "\n" + name + "\nSolver: scipy.optimize.minimize"+
            "\nModel: " + str(model) + "\nStarting Parameters: "+
            str(tau_start) + "\nBounds: "+ str(bounds) +
            "\nWavelength range: " + str(l_limits[0])+" - "+str(l_limits[1]) +
            " nm\nTime" + "delay range: " + str(d_limits[0])+" - "
            + str(d_limits[1]) + " ps\n\nTime constants / ps: " + str(tau_fit)
            + "\nRate constants / ps^-1: " + str(k_fit))
        
        np.savetxt(path+name+"_A_fit.txt", A_fit)
        np.savetxt(path+name+"_D_fit.txt", D_fit)
        np.savetxt(path+name+"_limited_lambda.txt", lambdas)
        np.savetxt(path+name+"_limited_delays.txt", delays)
        np.savetxt(path+name+"_limited_spectra.txt", spectra)
        
        f.close()
    
    def getResults(self, model):
        """
        Reads the results txt file in a string variable.

        Parameters
        ----------
        model : int/string
           Describes the desired model. 0 for the DAS. For SAS it can be a
           number 1-9 or "custom" for a custom model.

        Returns
        -------
        text : string
            A string with the content of the results file.

        """
        if model == 0:
            path = self.DAS.path
            name = self.DAS.name+"_GLA"
            txt = name+"_results.txt"
        else:
            path = self.SAS.path
            name = self.SAS.name+"_GTA"
            txt = name+"_results.txt"
        with open(path+txt) as f:
            text = f.read()
        return text
    
    def pickleData(self, **kwargs):
        """
        This method saves the given data in the shelve. 
        Keyword arguments must be given as key=value.

        Parameters
        ----------
        model : int/string
           Describes the desired model. 0 for the DAS. For SAS it can be a
           number 1-9 or "custom" for a custom model.
        d_limits : list with two int/float elements
            Lower and upper limits for the delay values.
        l_limits : list with two int/float elements
            Lower and upper limits for the lambda values.
        cont : float
            Determines how much contour lines will be shown in the 2D plot.
            High values will show more lines.
        time : list
            Can contain values for the delays which will be plotted in a
            subplot of absorption change against wavelengths.
        wave : list
            Can contain 0-10 values for the wavelengths which will be plotted
            in a subplot of delays against absorption change.
        tau : list/np.array
            The decay constants tau for a model 1-9 or a matrix Tau for a
            "custom" model.
       C_0 : list
           The list that contains values for C_0 set by the user.
           The default is None.

        Returns
        -------
        None.

        """
        path = self.path+"/"
        temp = self.delays_filename[::-1]
        temp = temp.index("/")
        name = self.delays_filename[-temp:-11]
        txt = name+"_pickle"
        s = shelve.open(path+txt, writeback=True)
        for key, value in kwargs.items():
            s[key] = value
        s.close()

    def getPickle(self):
        """
        Transforms the shelve in a dictionary which can be accessed to obtain
        the saved information.

        Returns
        -------
        shelf : dict
            A dictionary containing parameters chosen in the last run of the
            programm.

        """
        path = self.path+"/"
        temp = self.delays_filename[::-1]
        temp = temp.index("/")
        name = self.delays_filename[-temp:-11]
        txt = name+"_pickle"
        s = shelve.open(path+txt, writeback=False)
        shelf = dict(s).copy()
        s.close()
        return shelf