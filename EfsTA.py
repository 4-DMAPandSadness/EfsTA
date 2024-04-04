from PyQt5 import QtWidgets as QW
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QGuiApplication, QPixmap
import PopUps as PU
import ChirpCorrector as CC
import Controller as Cont
import numpy as np
import os as os
import TTIMG


class MainWindow(QW.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = loadUi("gui.ui", self)
        self.startUp()
        self.functionality()

    def startUp(self):
        """
        Ensures that upon startup everything is shown correctly.

        Returns
        -------
        None.

        """
        self.ui.UI_stack.setCurrentIndex(0)
        self.default_palette = QGuiApplication.palette()
        self.finalInputs = {}
        self.ui.input_tree.header().setSectionResizeMode(QW.QHeaderView.ResizeToContents)
        self.radios = QW.QButtonGroup(self)
        self.radios.addButton(self.ui.GLA_radio)
        self.radios.addButton(self.ui.GTA_radio_preset_model)
        self.radios.addButton(self.ui.GTA_radio_custom_model)
        self.radios.addButton(self.ui.GTA_radio_custom_matrix)
        self.ui.Analysis_stack.setCurrentIndex(0)
        self.createTheme()

    def onQuit(self):
        """
        Resets the color of the application and saves input values.

        Returns
        -------
        None.

        """
        EfsTA.setPalette(self.default_palette)
        self.saveAllInputs()
        self.savePickle()

    def functionality(self):
        """
        Adds functionality to the respective UI element.

        Returns
        -------
        None.

        """
        # All
        self.ui.actionTheme.triggered.connect(self.changeTheme)
        EfsTA.aboutToQuit.connect(self.onQuit)
        # Intro
        self.ui.Exp_TA.clicked.connect(self.initTA)
        self.ui.Exp_trEPR.clicked.connect(self.initEPR)
        # GDV
        self.ui.GVD_skip.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(3))
        self.ui.GVD_correct.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(2))
        # Chirp
        self.ui.Chirp_Browse_Sample.clicked.connect(lambda: self.getFilePaths("button", self.ui.Chirp_Sample_Dir))
        self.ui.Chirp_Browse_Solvent.clicked.connect(lambda: self.getFilePaths("button", self.ui.Chirp_Solvent_Dir))
        self.ui.Chirp_Browse_Chirp.clicked.connect(lambda: self.getFilePaths("button", self.ui.Chirp_Chirp_Dir))
        self.ui.Chirp_Sample_Dir.editingFinished.connect(lambda: self.getFilePaths("text", self.ui.Chirp_Sample_Dir))
        self.ui.Chirp_Solvent_Dir.editingFinished.connect(lambda: self.getFilePaths("text", self.ui.Chirp_Solvent_Dir))
        self.ui.Chirp_Chirp_Dir.editingFinished.connect(lambda: self.getFilePaths("text", self.ui.Chirp_Chirp_Dir))
        self.ui.Chirp_Done.clicked.connect(self.checkChirpFilesIfEmpty)
<<<<<<< HEAD
        # Analysis
=======
        # self.ui.Chirp_ViewData.clicked.connect(self.plotraw)
        #self.ui.Chirp_Visually.clicked.connect(self.selectChirpRange)
        # Analysis        
>>>>>>> 7afbd527bf6476eaafa6784894651a97b05b2c97
        self.ui.Data_directory.editingFinished.connect(lambda: self.getFolderPaths("text", self.ui.Data_directory))
        self.ui.Data_backToChirp.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(2))
        self.ui.Analysis_stack.currentChanged.connect(self.presentInputs)
        self.ui.Data_browse.clicked.connect(lambda: self.getFolderPaths("button", self.ui.Data_directory))
        self.ui.input_confirm.clicked.connect(self.finalCheck)
        self.ui.GTA_input_custom_model_saved_equations.currentIndexChanged.connect(lambda: self.setCustomModel(self.ui.GTA_input_custom_model_saved_equations.currentIndex()))
        self.ui.Data_clear_cache.clicked.connect(self.clearPickle)
        self.ui.GTA_open_table.clicked.connect(self.checkIfCustomMatrixSizeEmpty)
        self.ui.GTA_custom_model_save.clicked.connect(self.saveCustomModel)
        self.ui.GTA_custom_model_del.clicked.connect(self.deleteCustomModel)
        self.ui.Plotting_raw.clicked.connect(self.rawPlotting)
        self.ui.GTA_input_preset_model_tau.editingFinished.connect(lambda: self.summonRadio("preset"))
        self.ui.GTA_input_custom_model_tau.editingFinished.connect(lambda: self.summonRadio("custom"))
        self.ui.GLA_input_tau.editingFinished.connect(lambda: self.summonRadio("gla"))

    def initTA(self):
        self.ui.plot_type.addItems(["fsTA", "nsTA"])
        self.ui.plot_xAxis.setText("$\lambda$ / nm")
        self.ui.plot_yAxis.setText("delay / ps")
        self.ui.plot_zAxis.setText("$\Delta A$")
        self.ui.UI_stack.setCurrentIndex(1)
        self.ui.plot_type.currentIndexChanged.connect(lambda: self.setAxisTA(self.ui.plot_type.currentIndex()))

    def initEPR(self):
        self.ui.plot_type.addItems(["μs trEPR", "ms trEPR"])
        self.ui.plot_xAxis.setText("$B_0$ / mT")
        self.ui.plot_yAxis.setText("time / $\mu$s")
        self.ui.plot_zAxis.setText("d$\chi$'' / d$B_0$")
        self.ui.UI_stack.setCurrentIndex(3)
        self.ui.plot_type.currentIndexChanged.connect(lambda: self.setAxisEPR(self.ui.plot_type.currentIndex()))

###################################Utility#####################################

    def readSingleValue(self, UI_element):
        '''
        Take a QLineEdit, reads the text and returns the value as a float.

        Parameters
        ----------
        UI_element : QLineEdit
            The UI element from which the input is read..

        Returns
        -------
        value : float
            The converted input text.

        '''
        text = UI_element.text()
        if text == "":
            value = None
        else:
            value = float(text)
        return value

    def readList(self, UI_element):
        '''
        Take a QLineEdit, reads the text and returns a list of floats.

        Parameters
        ----------
        UI_element : QLineEdit
            The UI element from which the input is read..

        Returns
        -------
        value : list
            A list of the converted text elements.

        '''
        text = UI_element.text()
        if text == "":
            values = []
        else:
            values = text.split(',')
            for ind, val in enumerate(values):
                if val != "":
                    values[ind] = float(val)
                else:
                    val.remove("")
        return values

    def getFolderPaths(self, input_type, UI_element):
        '''
        Opens a filedialog window for the user to select the folder directory, where the data is stored.

        Returns
        -------
        None.

        '''
        if input_type == "button":
            directory = QW.QFileDialog.getExistingDirectory(self, 'Select Folder')
            UI_element.setText(directory)
        elif input_type == "text":
            directory = UI_element.text()
        if UI_element == self.ui.Data_directory:
            self.readData(directory)

    def getFilePaths(self, input_type, UI_element):
        '''
        Opens a filedialog window for the user to select a file.
        Returns
        -------
        None.

        '''
        if input_type == "button":
            directory = QW.QFileDialog.getOpenFileName(self, 'Select File')
            UI_element.setText(directory[0])
        elif input_type == "text":
            directory = UI_element.text()

####################################GVD########################################

    def checkChirpFilesIfEmpty(self):
        '''
        Checks which file paths are provided for the import.

        Returns
        -------
        sample_dir : string
            Sample measurement file path.
        solvent_dir : string
            Solvent measurement file path.
        chirp_dir : string
            Chirp/OKE measurement file path.

        '''
        sample_dir = self.ui.Chirp_Sample_Dir.text()
        solvent_dir = self.ui.Chirp_Solvent_Dir.text()
        chirp_dir = self.ui.Chirp_Chirp_Dir.text()
        rmBG = True
        OKE = True
        if sample_dir == "":
            self.openFailSafe("Please provide a sample file.")
            return
        if solvent_dir == "":
            rmBG = False
            self.openFailSafe("Warning! No background provided. Correction will proceede without background subtraction.")
        if chirp_dir == "":
            self.openFailSafe("Warning! No chirp/OKE measurment provided. Correction quality will be lower.")
            OKE = False
            self.ui.Chirp_Manually.setChecked(False)
        self.corrChirp(sample_dir, solvent_dir, chirp_dir, rmBG, OKE)

    def corrChirp(self, sample_dir, solvent_dir, chirp_dir, rmBG, OKE):
        options = {"Scatter": self.ui.Chirp_Scatter.isChecked(),
                   "Manually": self.ui.Chirp_Manually.isChecked(),
                   "rmBG": rmBG,
                   "OKE": OKE
                   }
        x = {"Sample_Dir": sample_dir,
             "Solvent_Dir": solvent_dir,
             "Chirp_Dir": chirp_dir,
             "Wave_Range": self.readList(self.ui.Chirp_Wave_Range),
             "Scale": self.readSingleValue(self.ui.Chirp_Scale),
             "Exc_Wave": self.readSingleValue(self.ui.Chirp_Exclude_Wave),
             "Header": self.ui.Chirp_Header.value(),
             "Options": options
             }
        CCorr = CC.ChirpCorrector(x, self)
        CCorr.correctData()

#####################################DATA######################################

    def checkIfBrowseEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.Data_directory.text() == "":
            self.openFailSafe("Please select a folder directory.")
            return True

    def readData(self, directory):

        self.finalInputs['Directory'] = directory
        if directory != "":
            self.Controller = Cont.Controller(directory)
            path = self.Controller.path + "/"
            names = ["delays_filename", "lambdas_filename", "spectra_filename"]
            if all(hasattr(self.Controller, attr) for attr in names) is False:
                self.openFailSafe('Please make sure the selected folder ' +
                                  'contains *.txt files ending with: \n' +
                                  '"taspectra.txt", "delays.txt" and' +
                                  '"lambda.txt" for TA or \n' +
                                  '"eprspectra.txt", "time.txt" and' +
                                  '"field.txt" for trEPR.')
            else:
                temp = self.Controller.delays_filename[::-1]
                temp = temp.index("/")
                name = self.Controller.delays_filename[-temp:-11]
                txt = name + "_input_backup"
                pickle = path + txt + ".dir"
                if os.path.isfile(pickle):
                    self.setPickle()
        else:
            self.openFailSafe("Please select a folder directory.")

    def getLowerDelayBound(self):
        """
        Reads the lower delay bound input by the user if empty returns None.

        Returns
        -------
        delay_lb: float
            The lower delay bound input by the user.

        """
        return self.readSingleValue(self.ui.Data_delay_input_lb)

    def getUpperDelayBound(self):
        """
        Reads the upper delay bound input by the user if empty returns None.

        Returns
        -------
        delay_ub: float
            The upper delay bound input by the user.

        """
        return self.readSingleValue(self.ui.Data_delay_input_ub)

    def getLowerWavelengthBound(self):
        """
        Reads the lower lambda bound input by the user if empty returns None.

        Returns
        -------
        lambda_lb: float
            The lower lambda bound input by the user.

        """
        return self.readSingleValue(self.ui.Data_wavelength_input_lb)

    def getUpperWavelengthBound(self):
        """
        Reads the upper lambda bound input by the user if empty returns None.

        Returns
        -------
        lambda_ub: float
            The upper lambda bound input by the user.

        """
        return self.readSingleValue(self.ui.Data_wavelength_input_ub)

    def getMultiplier(self):
        """
        Reads the ΔA data multiplier input by the user if empty returns 1.

        Returns
        -------
        mul : int
            The multiplier for the ΔA data input by the user.

        """
        if (self.ui.Data_input_multiplier.text() == "" or
                int(self.ui.Data_input_multiplier.text()) <= 0):
            mul = 1
        else:
            mul = int(self.ui.Data_input_multiplier.text())
        return mul

    def checkIfAxisEmpty(self):
        """
        Checks if a label for each axis was input.

        Returns
        -------
        None.

        """
        if (self.ui.plot_xAxis.text() or self.ui.plot_yAxis.text() or self.ui.plot_zAxis.text()) == "":
            self.openFailSafe("Please input guessed lifetimes.")
            return True

    def getAxis(self):
        """
        Reads the labels for each axis and returns them in a list.

        Returns
        -------
        labels : list
            A list containing the axis labels x,y,z.

        """
        self.Controller.labels = [self.ui.plot_xAxis.text(), self.ui.plot_yAxis.text(), self.ui.plot_zAxis.text()]

    def setAxisTA(self, ind):
        """
        Sets the axis labels for the selected experiment.

        Parameters
        ----------
        ind : int
            The index of the experiment type.

        Returns
        -------
        None.

        """
        if ind == 0:
            self.ui.plot_xAxis.setText("$\lambda$ / nm")
            self.ui.plot_yAxis.setText("delay / ps")
            self.ui.plot_zAxis.setText("$\Delta A$")
        if ind == 1:
            self.ui.plot_xAxis.setText("$\lambda$ / nm")
            self.ui.plot_yAxis.setText("delay / ns")
            self.ui.plot_zAxis.setText("$\Delta A$")

    def setAxisEPR(self, ind):
        """
        Sets the axis labels for the selected experiment.

        Parameters
        ----------
        ind : int
            The index of the experiment type.

        Returns
        -------
        None.

        """
        if ind == 0:
            self.ui.plot_xAxis.setText("$B_0$ / mT")
            self.ui.plot_yAxis.setText("time / $\mu$s")
            self.ui.plot_zAxis.setText("d$\chi$'' / d$B_0$")
        if ind == 1:
            self.ui.plot_xAxis.setText("$B_0$ / mT")
            self.ui.plot_yAxis.setText("time / ms")
            self.ui.plot_zAxis.setText("d$\chi$'' / d$B_0$")

#####################################GLA#######################################

    def checkIfGLATauEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.GLA_input_tau.text() == "":
            self.openFailSafe("Please input guessed lifetimes.")
            return True

    def getGLATaus(self):
        """
        Reads the lifetimes input by the user, if GLA is selected.

        Returns
        -------
        list
            The lifetimes input by the user.

        """
        return self.readList(self.ui.GLA_input_tau)

    def getGLAOptMethod(self):
        """
        Reads the algorithm choice for the minimization of the ChiSquare
        function by the user.

        Returns
        -------
        string
            The name of the minimization algorithm.

        """
        return self.ui.GLA_algorithm_optimize.currentText()

    def calculationGLA(self, db, wb):
        '''
        Starts the calculation for the global lifetime analysis and opens up
        a popup window with the results.

        Parameters
        ----------
        db : list
            Lower and upper bound for the delays.
        wb : list
            Lower and upper bound for the wavelengths.

        Returns
        -------
        None.

        '''
        self.tau_fit, spec, res, D_fit, fit_report = self.Controller.calcDAS(self.prepareParam("gla"), db, wb, self.getGLAOptMethod())
        self.openPopUpResults(0, self.Controller)

#####################################GTA#######################################

    def checkIfBoundsMatch(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.GTA_input_tau_lb.text() != "":
            if (self.ui.GTA_input_tau_lb.text().count(",") !=
                    self.ui.GTA_input_preset_model_tau.text().count(",")):
                self.openFailSafe("Please provide a bound for each lifetime.")
                return False
        if self.ui.GTA_input_tau_ub.text() != "":
            if (self.ui.GTA_input_tau_ub.text().count(",") !=
                    self.ui.GTA_input_preset_model_tau.text().count(",")):
                self.openFailSafe("Please provide a bound for each lifetime.")
                return False

    def getTauBounds(self):
        """
        Reads the bounds for the lifetimes during the calculation.

        Returns
        -------
        list
            A list containing the lower bounds and upper bounds list.

        """
        tau_lb = self.readList(self.ui.GTA_input_tau_lb)
        tau_ub = self.readList(self.ui.GTA_input_tau_ub)
        if any(isinstance(obj, float) for obj in tau_lb):
            tau_lb = [None if item == '' else item for item in tau_lb]
        else:
            tau_lb = []
        if any(isinstance(obj, float) for obj in tau_ub):
            tau_ub = [None if item == '' else item for item in tau_ub]
        else:
            tau_ub = []
        return [tau_lb, tau_ub]

    def getCustomConcentration(self):
        """
        Reads the concentration vector input by the user and returns it.

        Returns
        -------
        c0 : list
            The concentration vector set by the user.

        """
        c0 = self.readList(self.ui.GTA_input_concentration)
        if any(isinstance(obj, float) for obj in c0):
            c0 = c0
        else:
            c0 = []
        return c0

    def getGTAOptMethod(self):
        """
        Returns the current selected optimization algorithm.

        Returns
        -------
        string
            The name of the selected optimization algorithm.

        """
        return self.ui.GTA_algorithm_optimize.currentText()

    def getGTAIvpMethod(self):
        """
        Returns the current selected ivp solver algorithm.

        Returns
        -------
        string
            The name of the selected ivp solver algorithm.

        """
        return self.ui.GTA_algorithm_initial_value_problem.currentText()

    def calculationGTA(self, db, wb, model, K):
        '''
        Starts the calculation for the global target analysis and opens up
        a popup window with the results.

        Parameters
        ----------
        db : list
            Lower and upper bound for the delays.
        wb : list
            Lower and upper bound for the wavelengths.
        model : int/string
            The chosen kinetic model.
        K : np.ndarray
            The kinetic matrix.

        Returns
        -------
        None.

        '''
        K = np.array(K)
        if model == "custom matrix":
            self.tau_fit, spec, res, D_fit, fit_report = self.Controller.calcSAS(K, [], self.getCustomConcentration(), db, wb, model, [], [], self.getGTAOptMethod(), self.getGTAIvpMethod())
        elif model == "custom model":
            self.tau_fit, spec, res, D_fit, fit_report = self.Controller.calcSAS(K, self.prepareParam("custom"), self.getCustomConcentration(), db, wb, model, [], [], self.getGTAOptMethod(), self.getGTAIvpMethod())
        else:
            self.tau_fit, spec, res, D_fit, fit_report = self.Controller.calcSAS(K, self.prepareParam("preset"), self.getCustomConcentration(), db, wb, model, self.getTauBounds()[0], self.getTauBounds()[1], self.getGTAOptMethod(), self.getGTAIvpMethod())
        self.openPopUpResults(model, self.Controller)

#Preset

    def getPresetModel(self):
        """
        Returns the currently selected kinetic model.
        Returns
        -------
        int
            The integer corresponding to a kinetic model.

        """
        return self.ui.GTA_preset_model_selection.currentIndex()

    def checkIfPresetModelTauEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.GTA_input_preset_model_tau.text() == "":
            self.openFailSafe("Please input guessed lifetimes.")
            return True

    def getGTAPresetModelTaus(self):
        """
        Reads the lifetimes input by the user, if a preset model is selected.

        Returns
        -------
        tau : list
            The lifetimes input by the user.

        """
        return self.readList(self.ui.GTA_input_preset_model_tau)

#Custom

    def checkIfCustomModelEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.GTA_input_custom_model_equation.text() == "":
            self.openFailSafe("Please input a transition equation.")
            return True
        elif self.ui.GTA_input_custom_model_tau.text() == "":
            self.openFailSafe("Please input guessed lifetimes.")
            return True

    def getGTACustomModelTaus(self):
        """
        Reads the lifetimes input by the user, if a custom model is selected.

        Returns
        -------
        tau : list
            The lifetimes input by the user.

        """
        return self.readList(self.ui.GTA_input_custom_model_tau)

    def saveCustomModel(self):
        """
        Saves the currently input transition equation to the combobox.

        Returns
        -------
        None.

        """
        if self.ui.GTA_input_custom_model_equation.text() == "":
            pass
        elif self.ui.GTA_input_custom_model_saved_equations.findText(self.ui.GTA_input_custom_model_equation.text()) != -1:
            pass
        else:
            self.ui.GTA_input_custom_model_saved_equations.addItem(self.ui.GTA_input_custom_model_equation.text())

    def deleteCustomModel(self):
        """
        Deletes the currently selected transition equation from the combobox.

        Returns
        -------
        None.

        """
        if self.ui.GTA_input_custom_model_saved_equations.currentText() == "":
            pass
        else:
            self.ui.GTA_input_custom_model_saved_equations.removeItem(self.ui.GTA_input_custom_model_saved_equations.currentIndex())

    def setCustomModel(self, ind):
        '''
        Sets the custom model to the previously selected model.

        Parameters
        ----------
        ind : int
            The index of the selected custom model.

        Returns
        -------
        None.

        '''
        self.ui.GTA_input_custom_model_saved_equations.setCurrentIndex(ind)
        model = self.ui.GTA_input_custom_model_saved_equations.currentText()
        self.ui.GTA_input_custom_model_equation.setText(model)

    def getCustomModelEquation(self):
        """
        Returns the custom transition equation.

        Returns
        -------
        str
            The custom transition equation.

        """
        return self.ui.GTA_input_custom_model_equation.text()

    def getCustomModel(self):
        '''
        Transforms the custom model input by the user as a transition equation into the corresponding kinetic matrix with the input lifetimes.

        Returns
        -------
        M : np.ndarray
            The kinetic matrix created from the transition equation and the
            lifetime imputs.

        '''
        #dictionary used to convert species names to corresponding matrix coordinates
        letterstonumbers = {"A": 0,
                            "B": 1,
                            "C": 2,
                            "D": 3,
                            "E": 4,
                            "F": 5,
                            "G": 6,
                            "H": 7,
                            "I": 8,
                            "J": 9,
                            "K": 10,
                            "L": 11,
                            "M": 12,
                            "N": 13,
                            "O": 14,
                            "P": 15,
                            "Q": 16,
                            "R": 17,
                            "S": 18,
                            "T": 19,
                            "U": 20,
                            "V": 21,
                            "W": 22,
                            "X": 23,
                            "Y": 24,
                            "Z": 25,
                            "v": -1  #not a coordinate just a way to identify void decays
                            }
        #GUI input
        eq = self.getCustomModelEquation()
        tau = self.getGTACustomModelTaus()
        #checks if the equation used arrows
        arrow = False
        if "->" in eq:
            arrow = True
        #checks if there are any void transitions
        void = False
        if "v" in eq:
            void = True
        #splitting different decay paths
        eq_split = eq.split(";")
        #splitting each path into involved species
        separated_species = []
        if arrow is True:
            for string in eq_split:
                temp = string.split("->")
                separated_species.append(temp)
        else:
            for string in eq_split:
                temp = list(string)
                separated_species.append(temp)
        #forming pairs of two to set up matrix input
        paired_species = []
        for list_ in separated_species:
            for i in range(len(list_) - 1):
                paired_species.append([list_[i], list_[i + 1]])
        #converting species names to numbers for matrix coordinates
        for list_ in paired_species:
            for i in range(len(list_)):
                list_[i] = letterstonumbers[list_[i]]
        #determining and creating the matrix dimensions by unique species
        all_letters = np.array(paired_species).flatten()
        if void is False:
            species = len(np.unique(all_letters))
        else:
            species = len(np.unique(all_letters)) - 1
        M = np.zeros((species, species))
        #filling the matrix with the lifetimes using the determined coordinates
        tau_index = 0
        for list_ in paired_species:
            if list_[1] == -1:
                M[list_[0]][list_[0]] += tau[tau_index]
            else:
                if list_[0] < list_[1]:
                    M[list_[0]][list_[0]] += tau[tau_index]
                    M[list_[1]][list_[0]] += tau[tau_index]
                elif list_[0] > list_[1]:
                    M[list_[0]][list_[0]] += tau[tau_index]
                    M[list_[1]][list_[0]] += tau[tau_index]
                else:
                    M[list_[0]][list_[0]] += tau[tau_index]
            tau_index += 1
        #adjusting the signs for the main diagonal to be negative
        N = np.ones((species, species))
        np.fill_diagonal(N, -1)
        M = M * N
        if M[-1][-1] == -0:
            M[-1][-1] *= -1
        return M

#Matrix

    def checkIfCustomMatrixSizeEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.GTA_input_rows_and_columns.value() != 0:
            self.ui.GTA_radio_custom_matrix.setChecked(True)
            self.openPopUpMatrixInput(self.ui.GTA_input_rows_and_columns.value())
        else:
            self.openFailSafe("Please input a table size.")
            return True

    def checkIfCustomMatrixEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if hasattr(self, 'custom_Matrix') is False:
            self.openFailSafe("Please input a kinetic matrix.")
            return True

    def closePopupMatrix(self, popup):
        """
        Transfers the custom matrix input by the user from the popup object to
        the main window and closes the popup window.

        Parameters
        ----------
        popup : TableWindow
            The TableWindow object created by the main window.

        Returns
        -------
        None.

        """
        self.custom_Matrix = popup.custom_Matrix
        popup.close()

#####################################PREPARE PARAMETERS########################

    def summonRadio(self, layout_origin):
        """
        Summons radio buttons corresponding to the input lifetimes for the selection
        of fixed values.

        Parameters
        ----------
        layout_origin : string
            "preset","custom" or "gla" depending on the last edited QLineEdit.

        Returns
        -------
        None.

        """
        if layout_origin == "preset":
            layout = self.ui.GTA_preset_model_fix_layout
            taus = self.getGTAPresetModelTaus()
            self.ui.GTA_radio_preset_model.setChecked(True)
        elif layout_origin == "custom":
            layout = self.ui.GTA_custom_model_fix_layout
            taus = self.getGTACustomModelTaus()
            self.ui.GTA_radio_custom_model.setChecked(True)
        elif layout_origin == "gla":
            layout = self.ui.GLA_fix_layout
            taus = self.getGLATaus()
            self.ui.GLA_radio.setChecked(True)
        for i in reversed(range(layout.count())):
            widgetToRemove = layout.itemAt(i).widget()
            widgetToRemove.deleteLater()
        for tau in taus:
            layout.addWidget(QW.QRadioButton(str(tau), autoExclusive=False))

    def prepareParam(self, method):
        """
        Prepares the user inputs for the conversion to lmfit parameters.

        Parameters
        ----------
        method : string
            "preset","custom" or "gla" depending on the selected analysis method.

        Returns
        -------
        prepParam : list
            A list containing tuples with the lifetime and a boolean stating if the
            lifetime will be varied.

        """
        if method == "preset":
            layout = self.ui.GTA_preset_model_fix_layout
            taus = self.getGTAPresetModelTaus()
        elif method == "custom":
            layout = self.ui.GTA_custom_model_fix_layout
            taus = self.getGTACustomModelTaus()
        elif method == "gla":
            layout = self.ui.GLA_fix_layout
            taus = self.getGLATaus()
        widgets = (layout.itemAt(i).widget() for i in range(layout.count()))
        if layout.count() == 0:
            prepParam = [(t, True) for t in taus]
        else:
            prepParam = []
        for widget in widgets:
            if isinstance(widget, QW.QRadioButton):
                prepParam.append((float(widget.text()), not widget.isChecked()))
        return prepParam

#####################################PLOT######################################

    def checkIfWavelengthSlicesEmpty(self):
        """
        Checks if the user provided specific wavelengths for data slicing.
        If not disables corresponding plot option.

        Returns
        -------
        None.

        """
        if self.ui.plot_input_wavelength_slices.text() == "":
            self.ui.plot_wavelength_slices.setChecked(False)

    def getWavelengthSlices(self):
        """
        Reads the lambdas input by the user if empty, returns an empty list.

        Returns
        -------
        user_lambdas: list
            A list containing the lambdas input by the user.

        """
        return self.readList(self.ui.plot_input_wavelength_slices)

    def checkIfDelaySlicesEmpty(self):
        """
        Checks if the user provided specific delays for data slicing.
        If not disables corresponding plot option.

        Returns
        -------
        None.

        """
        if self.ui.plot_input_delay_slices.text() == "":
            self.ui.plot_delay_slices.setChecked(False)

    def getDelaySlices(self):
        """
        Reads the delays input by the user if empty, returns an empty list.

        Returns
        -------
        user_delays: list
            A list containing the delays input by the user.

        """
        return self.readList(self.ui.plot_input_delay_slices)

    def getUserContour(self):
        """
        Reads the contour input by the user, if empty returns 20.

        Returns
        -------
        cont : int
            The amount of contour lines shown in the heatmap plot input by
            the user.

        """
        if self.ui.plot_input_contour.value() == 0:
            cont = 20
        else:
            cont = self.ui.plot_input_contour.value()
        return cont

    def getVmin(self):
        """
        Reads the colormap normalization minimum input by the user, if empty
        returns None.

        Returns
        -------
        None.

        """
        if self.ui.plot_input_vmin.text() == "":
            vmin = None
        else:
            vmin = float(self.ui.plot_input_vmin.text())
        return vmin

    def getVmax(self):
        """
        Reads the colormap normalization maximum input by the user, if empty
        returns None.

        Returns
        -------
        None.

        """
        if self.ui.plot_input_vmax.text() == "":
            vmax = None
        else:
            vmax = float(self.ui.plot_input_vmax.text())
        return vmax

    def rawPlotting(self):
        '''
        Plots only the raw unanalysed data.

        Returns
        -------
        None.

        '''
        if hasattr(self, "Controller") is False:
            self.openFailSafe("Please select a directory first.")
        else:
            if hasattr(self.Controller, "delays_filename") is False:
                self.openFailSafe("Please select a valid directory first.")
            else:
                self.getAxis()
                ds = sorted(self.getDelaySlices())
                ws = sorted(self.getWavelengthSlices())
                db = [self.getLowerDelayBound(), self.getUpperDelayBound()]
                wb = [self.getLowerWavelengthBound(), self.getUpperWavelengthBound()]
                self.Controller.createOrigData(db, wb, None, None)
                self.ui.plot_concentrations.setChecked(False)
                self.ui.plot_das_sas.setChecked(False)
                self.ui.plot_residuals.setChecked(False)
                if (self.ui.plot_delay_slices.isChecked() is False and
                        self.ui.plot_wavelength_slices.isChecked() is False):
                    self.ui.plot_three_in_one.setChecked(False)
                self.plotting(ds, ws, 0, True)

    def plotting(self, ds, ws, model, raw):
        """
        Creates the plots selected by the user and opens them in popup windows
        for inspection/modification.

        Parameters
        ----------
        ds : list
            The specific delay values the user wants to examine.
        ws : list
            The specific wavelenght values the user wants to examine.
        model : int/string
            Describes the desired model. 0 for the GLA. For GTA it can be a
            number 1-8, "custom model" or "custom matrix".
        raw : bool
            Dictates if raw or analysed data will be plotted.
        Returns
        -------
        None.

        """
        if raw is True:
            if self.ui.plot_wavelength_slices.isChecked() is True:
                self.Controller.plotSolo(ws, ds, self.getVmin(), self.getVmax(), None, self.getUserContour(), "WS", self.getMultiplier())
            if self.ui.plot_delay_slices.isChecked() is True:
                self.Controller.plotSolo(ws, ds, self.getVmin(), self.getVmax(), None, self.getUserContour(), "DS", self.getMultiplier())
            if self.ui.plot_heatmap.isChecked() is True:
                self.Controller.plotSolo(ws, ds, self.getVmin(), self.getVmax(), None, self.getUserContour(), "H", self.getMultiplier())
            if self.ui.plot_three_in_one.isChecked() is True:
                self.Controller.plot3OrigData(ws, ds, self.getVmin(), self.getVmax(), self.getUserContour(), self.getMultiplier())
            if self.ui.plot_threed_contour.isChecked() is True:
                self.Controller.plot3DOrigData(self.getVmin(), self.getVmax(), self.getMultiplier())
        if raw is False:
            if self.ui.plot_wavelength_slices.isChecked() is True:
                self.Controller.plotSolo(ws, ds, self.getVmin(), self.getVmax(), model, self.getUserContour(), "WS", self.getMultiplier())
            if self.ui.plot_delay_slices.isChecked() is True:
                self.Controller.plotSolo(ws, ds, self.getVmin(), self.getVmax(), model, self.getUserContour(), "DS", self.getMultiplier())
            if self.ui.plot_heatmap.isChecked() is True:
                self.Controller.plotSolo(ws, ds, self.getVmin(), self.getVmax(), model, self.getUserContour(), "H", self.getMultiplier())
            if self.ui.plot_three_in_one.isChecked() is True:
                self.Controller.plot3FittedData(ws, ds, self.getVmin(), self.getVmax(), model, self.getUserContour(), self.getMultiplier())
            if self.ui.plot_threed_contour.isChecked() is True:
                self.Controller.plot3DFittedData(self.getVmin(), self.getVmax(), model, self.getMultiplier())
            if self.ui.plot_residuals.isChecked() is True:
                self.Controller.plot2Dresiduals(self.getVmin(), self.getVmax(), model, self.getUserContour(), self.getMultiplier())
            if self.ui.plot_das_sas.isChecked() is True:
                self.Controller.plotDAS(model, self.tau_fit, self.getMultiplier())
            if self.ui.plot_concentrations.isChecked() is True:
                self.Controller.plotKinetics(model)

#####################################CONFIRM###################################

    def checkIfMethodSelected(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            False if not.

        """
        if(self.ui.GLA_radio.isChecked() is False and
               self.ui.GTA_radio_preset_model.isChecked() is False and
               self.ui.GTA_radio_custom_model.isChecked() is False and
               self.ui.GTA_radio_custom_matrix.isChecked() is False):
            self.openFailSafe("Please select an analysis method.")
            return False

    def finalCheck(self):
        """
        Checks all required data fields before starting the program.

        Returns
        -------
        None.

        """
        self.checkIfWavelengthSlicesEmpty()
        self.checkIfDelaySlicesEmpty()
        self.checkIfAxisEmpty()
        if self.checkIfBrowseEmpty() is True:
            return
        if (self.checkIfMethodSelected() is False):
            return
        if self.checkIfBoundsMatch() is False:
            return
        if (self.ui.GLA_radio.isChecked() is True and
                self.checkIfGLATauEmpty() is True):
            return
        elif (self.ui.GTA_radio_preset_model.isChecked() is True and
                self.checkIfPresetModelTauEmpty() is True):
            return
        elif (self.ui.GTA_radio_custom_model.isChecked() is True and
                self.checkIfCustomModelEmpty() is True):
            return
        elif (self.ui.GTA_radio_custom_matrix.isChecked() is True and
                self.checkCustomMatrixIfEmpty() is True):
            return
        else:
            self.programStart()

    def programStart(self):
        """
        Starts the program and saves the user
        inputs. Executes the corresponding plotting/calculation,
        depending on the model chosen by the user.

        Returns
        -------
        None.

        """
        self.getAxis()
        self.savePickle()
        ds = sorted(self.getDelaySlices())
        ws = sorted(self.getWavelengthSlices())
        db = [self.getLowerDelayBound(), self.getUpperDelayBound()]
        wb = [self.getLowerWavelengthBound(), self.getUpperWavelengthBound()]
        if self.GLA_radio.isChecked() is True:
            self.calculationGLA(db, wb)
            self.plotting(ds, ws, 0, False)
        elif self.GTA_radio_preset_model.isChecked() is True:
            model = self.getPresetModel() + 1
            K = self.getGTAPresetModelTaus()
            self.calculationGTA(db, wb, model, K)
            self.plotting(ds, ws, model, False)
        elif self.GTA_radio_custom_model.isChecked() is True:
            model = "custom model"
            K = self.getCustomModel()
            self.calculationGTA(db, wb, model, K)
            self.plotting(ds, ws, model, False)
        elif self.GTA_radio_custom_matrix.isChecked() is True:
            model = "custom matrix"
            K = self.custom_Matrix
            self.calculationGTA(db, wb, model, K)
            self.plotting(ds, ws, model, False)

#####################################POPUP#####################################

    def openPopUpMatrixInput(self, size):
        """
        Opens the custom matrix popup window.

        Parameters
        ----------
        size : int
            The size n of the n*n table.

        Returns
        -------
        None.

        """
        popup = PU.TableWindow(size)
        popup.show()
        popup.save.clicked.connect(lambda: self.closePopupMatrix(popup))

    def openPopUpResults(self, model, Controller):
        """
        Opens up the results popup window.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the GLA. For GTA it can be a
            number 1-8, "custom model" or "custom matrix".
        Controller : Controller
            An object of the Controller class.
        fit_report : string
            The results of the fit and some goodness of fit statistics.

        Returns
        -------
        None.

        """
        self.resultView = PU.TextWindow(model, Controller, None)
        self.resultView.show()

    def openFailSafe(self, msg):
        """
        Opens up the failsafe popup window, displaying an error message.

        Parameters
        ----------
        msg : string
            The error message.

        Returns
        -------
        None.

        """
        if hasattr(self, "popup"):
            self.popup.text_browser.append(f"\n{msg}")
        else:
            self.popup = PU.TextWindow(None, None, msg)
            self.popup.show()

    def presentInputs(self, ind):
        '''
        Presents all relevant user inputs in a treewidget.

        Parameters
        ----------
        ind : int
            The index of the Input Confirmation-tab widget.

        Returns
        -------
        None.

        '''
        if ind == 5:
            self.saveAllInputs()
            iterator = QW.QTreeWidgetItemIterator(self.ui.input_tree)
            while iterator.value():
                item = iterator.value()
                if item.text(0) in self.finalInputs:
                    item.setText(1, self.finalInputs[item.text(0)])
                if item.text(0) == 'Data':
                    item.setExpanded(True)
                if item.text(0) == 'Plotting':
                    item.setExpanded(True)
                if item.text(0) == 'Algorithms':
                    algorithm_pointer = item
                if item.text(0) == 'GLA':
                    GLA_pointer = item
                    if self.ui.GLA_radio.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setHidden(True)
                if item.text(0) == 'GTA':
                    GTA_pointer = item
                    if GLA_pointer.isHidden() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setHidden(True)
                if item.text(0) == 'Preset Model':
                    if self.ui.GTA_radio_preset_model.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setExpanded(False)
                        item.setHidden(True)
                elif item.text(0) == 'Custom Model':
                    if self.ui.GTA_radio_custom_model.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setExpanded(False)
                        item.setHidden(True)
                elif item.text(0) == 'Custom Matrix':
                    if self.ui.GTA_radio_custom_matrix.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setExpanded(False)
                        item.setHidden(True)
                iterator += 1
            if self.radios.checkedId() == -1:
                GLA_pointer.setHidden(True)
                GTA_pointer.setHidden(True)
            algorithm_pointer.setExpanded(True)

#####################################INTRO#####################################

    def createTheme(self):
        darkmode = QPalette()
        darkmode.setColor(darkmode.Window, QColor(53, 53, 53))
        darkmode.setColor(darkmode.WindowText, Qt.white)
        darkmode.setColor(darkmode.Base, QColor(25, 25, 25))
        darkmode.setColor(darkmode.AlternateBase, QColor(53, 53, 53))
        darkmode.setColor(darkmode.ToolTipBase, Qt.black)
        darkmode.setColor(darkmode.ToolTipText, Qt.white)
        darkmode.setColor(darkmode.Text, Qt.white)
        darkmode.setColor(darkmode.Button, QColor(53, 53, 53))
        darkmode.setColor(darkmode.ButtonText, Qt.white)
        darkmode.setColor(darkmode.BrightText, Qt.green)
        darkmode.setColor(darkmode.Link, QColor(42, 130, 218))
        darkmode.setColor(darkmode.Highlight, QColor(42, 130, 218))
        darkmode.setColor(darkmode.HighlightedText, Qt.black)
        self.darkmode = [darkmode, "active"]
        EfsTA.setPalette(self.darkmode[0])

    def changeTheme(self):
        """
        Changes the colour theme of the program to either light or dark.

        Returns
        -------
        None.

        """
        if self.darkmode[1] == "active":
            EfsTA.setPalette(self.default_palette)
            self.darkmode[1] = "inactive"
        else:
            EfsTA.setPalette(self.darkmode[0])
            self.darkmode[1] = "active"

#####################################PICKLE####################################

    def saveAllInputs(self):
        '''
        Saves all user inputs in a dictionary to pickle and display them.

        Returns
        -------
        None.

        '''
        self.finalInputs.clear()
        self.finalInputs['Lower Delay/Time Bound'] = self.ui.Data_delay_input_lb.text()
        self.finalInputs['Upper Delay/Time Bound'] = self.ui.Data_delay_input_ub.text()
        self.finalInputs['Lower Wavelength/Field Bound'] = self.ui.Data_wavelength_input_lb.text()
        self.finalInputs['Upper Wavelength/Field Bound'] = self.ui.Data_wavelength_input_ub.text()
        self.finalInputs['Data Multiplier'] = self.ui.Data_input_multiplier.text()
        self.finalInputs['Directory'] = self.ui.Data_directory.text()
        self.finalInputs['Lower Tau Bounds'] = self.ui.GTA_input_tau_lb.text()
        self.finalInputs['Upper Tau Bounds'] = self.ui.GTA_input_tau_ub.text()
        self.finalInputs['x-Axis'] = self.ui.plot_xAxis.text()
        self.finalInputs['y-Axis'] = self.ui.plot_yAxis.text()
        self.finalInputs['z-Axis'] = self.ui.plot_zAxis.text()
        if self.ui.GLA_radio.isChecked() is True:
            self.finalInputs['GLA'] = ""
            self.finalInputs['Optimizer'] = self.ui.GLA_algorithm_optimize.currentText()
            self.finalInputs['Taus'] = str(self.prepareParam("gla")).replace("True", "Vary").replace("False", "Fix")
            self.finalInputs['Tau Cache'] = str([tau[0] for tau in self.prepareParam("gla")])
            self.finalInputs['Buttons'] = self.prepareParam("gla")
        if self.ui.GTA_radio_preset_model.isChecked() is True:
            self.finalInputs['Preset Model'] = ""
            self.finalInputs['Concentrations'] = self.ui.GTA_input_concentration.text()
            self.finalInputs['Model'] = self.ui.GTA_preset_model_selection.currentText()
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Taus'] = str(self.prepareParam("preset")).replace("True", "Vary").replace("False", "Fix")
            self.finalInputs['Tau Cache'] = str([tau[0] for tau in self.prepareParam("preset")])
            self.finalInputs['Buttons'] = self.prepareParam("preset")
            self.finalInputs['Preset Model Index'] = self.ui.GTA_preset_model_selection.currentIndex() + 1
        if self.ui.GTA_radio_custom_model.isChecked() is True:
            self.finalInputs['Custom Model'] = ""
            self.finalInputs['Concentrations'] = self.ui.GTA_input_concentration.text()
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Model'] = self.ui.GTA_input_custom_model_equation.text()
            self.finalInputs['Taus'] = str(self.prepareParam("custom")).replace("True", "Vary").replace("False", "Fix")
            self.finalInputs['Tau Cache'] = str([tau[0] for tau in self.prepareParam("custom")])
            self.finalInputs['Buttons'] = self.prepareParam("custom")
            self.finalInputs['Saved Models'] = [self.ui.GTA_input_custom_model_saved_equations.itemText(i) for i in range(self.ui.GTA_input_custom_model_saved_equations.count())]
        if self.ui.GTA_radio_custom_matrix.isChecked() is True:
            self.finalInputs['Custom Matrix'] = ""
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Concentrations'] = self.ui.GTA_input_concentration.text()
            if hasattr(self, "custom_Matrix"):
                self.finalInputs['Matrix'] = str(self.custom_Matrix)
            else:
                self.finalInputs['Matrix'] = "Missing Input."
        self.finalInputs['Selected Plots'] = ""
        if self.ui.plot_das_sas.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', DAS/SAS'
        if self.ui.plot_delay_slices.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Delay/Time Slices'
        if self.ui.plot_heatmap.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Heatmap'
        if self.ui.plot_wavelength_slices.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Wavelength/Field Slices'
        if self.ui.plot_concentrations.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Concentrations'
        if self.ui.plot_residuals.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Residuals'
        if self.ui.plot_three_in_one.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Three In One'
        if self.ui.plot_threed_contour.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', 3D Contour'
        self.finalInputs['Vmin'] = self.ui.plot_input_vmin.text()
        self.finalInputs['Vmax'] = self.ui.plot_input_vmax.text()
        self.finalInputs['Contour Lines'] = str(self.getUserContour())
        self.finalInputs['Delay/Time Slices'] = self.ui.plot_input_delay_slices.text()
        self.finalInputs['Wavelength/Field Slices'] = self.ui.plot_input_wavelength_slices.text()
        self.finalInputs['Selected Plots'] = self.finalInputs['Selected Plots'][2:]

    def savePickle(self):
        '''
        Pickles the data, if a path was selected and therefore the controller object generated.

        Returns
        -------
        None.

        '''
        if hasattr(self, 'Controller') is True:
            self.Controller.pickleData(self.finalInputs)

    def getPickle(self):
        """
        Reloads the saved user inputs.

        Returns
        -------
        None.

        """
        if hasattr(self, 'Controller') is False:
            self.Controller = Cont.Controller(self.getFolderPath())
        self.shelf = self.Controller.getPickle()

    def setPickle(self):
        """
        Sets the reloaded user inputs in the GUI.

        Returns
        -------
        None.

        """
        self.getPickle()
        if "Custom Model" in self.shelf:
            models = self.shelf["Saved Models"]
            for i in range(len(models)):
                self.ui.GTA_input_custom_model_saved_equations.addItem(models[i])
        if "Custom Matrix" in self.shelf:
            self.custom_Matrix = self.shelf["Matrix"]
        if "Buttons" in self.shelf:
            buttons = self.shelf["Buttons"]
        for key in self.shelf:
            val = str(self.shelf[key])
            val = val.replace("[", "")
            val = val.replace("]", "")
            val = val.replace("None", "")
            val = val.replace(" ", "")
            if key == "Data Multiplier":
                self.ui.Data_input_multiplier.setText(val)
            if key == "Lower Delay/Time Bound":
                self.ui.Data_delay_input_lb.setText(val)
            if key == "Upper Delay/Time Bound":
                self.ui.Data_delay_input_ub.setText(val)
            if key == "Lower Wavelength/Field Bound":
                self.ui.Data_wavelength_input_lb.setText(val)
            if key == "Upper Wavelength/Field Bound":
                self.ui.Data_wavelength_input_ub.setText(val)
            if key == "Lower Tau Bounds":
                self.ui.GTA_input_tau_lb.setText(val)
            if key == "Upper Tau Bounds":
                self.ui.GTA_input_tau_ub.setText(val)
            if key == "GLA":
                self.ui.GLA_radio.setChecked(True)
            if key == "Preset Model":
                self.ui.GTA_radio_preset_model.setChecked(True)
            if key == "Custom Model":
                self.ui.GTA_radio_custom_model.setChecked(True)
            if key == "Custom Matrix":
                self.ui.GTA_radio_custom_matrix.setChecked(True)
            if self.ui.GLA_radio.isChecked() is True:
                if key == "Tau Cache":
                    self.ui.GLA_input_tau.setText(val)
                if key == "Buttons":
                    for button in buttons:
                        radio = QW.QRadioButton(str(button[0]), autoExclusive=False)
                        radio.setChecked(not bool(button[1]))
                        self.ui.GLA_fix_layout.addWidget(radio)
            if self.ui.GTA_radio_preset_model.isChecked() is True:
                if key == "Preset Model Index":
                    self.ui.GTA_preset_model_selection.setCurrentIndex(int(val) - 1)
                if key == "Tau Cache":
                    self.ui.GTA_input_preset_model_tau.setText(val)
                if key == "Buttons":
                    for button in buttons:
                        radio = QW.QRadioButton(str(button[0]), autoExclusive=False)
                        radio.setChecked(not bool(button[1]))
                        self.ui.GTA_preset_model_fix_layout.addWidget(radio)
            if self.ui.GTA_radio_custom_model.isChecked() is True:
                if key == "Model":
                    self.ui.GTA_input_custom_model_equation.setText(val)
                if key == "Tau Cache":
                    self.ui.GTA_input_custom_model_tau.setText(val)
                if key == "Buttons":
                    for button in buttons:
                        radio = QW.QRadioButton(str(button[0]), autoExclusive=False)
                        radio.setChecked(not bool(button[1]))
                        self.ui.GTA_custom_model_fix_layout.addWidget(radio)
            if key == "Concentrations":
                self.ui.GTA_input_concentration.setText(val)
            if key == "Delay/Time Slices":
                self.ui.plot_input_delay_slices.setText(val)
            if key == "Wavelength/Field Slices":
                self.ui.plot_input_wavelength_slices.setText(val)
            if key == "Contour Lines":
                self.ui.plot_input_contour.setValue(int(val))
            if key == "Vmin":
                self.ui.plot_input_vmin.setText(val)
            if key == "Vmax":
                self.ui.plot_input_vmax.setText(val)

    def clearPickle(self):
        """
        Clears the set reloaded user inputs.

        Returns
        -------
        None.

        """
        for lineedit in self.findChildren(QW.QLineEdit):
            if lineedit != self.ui.Data_directory:
                lineedit.clear()
        for spinbox in self.findChildren(QW.QSpinBox):
            spinbox.setValue(0)
        for combobox in self.findChildren(QW.QComboBox):
            combobox.setCurrentIndex(0)
        if hasattr(self, 'cm') is True:
            self.cm = None

#####################################APP#######################################            


if __name__ == '__main__':
    import sys
    if not QW.QApplication.instance():
        EfsTA = QW.QApplication(sys.argv)
    else:
        EfsTA = QW.QApplication.instance()
    EfsTA.setStyle('Fusion')
    mainwindow = MainWindow()
    EfsTA.setQuitOnLastWindowClosed(True)
    mainwindow.show()
    sys.exit(EfsTA.exec_())
