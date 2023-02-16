import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLineEdit, 
                             QSpinBox, QComboBox, QTreeWidgetItemIterator,
                             QButtonGroup)
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QGuiApplication
import Controller as Cont
import numpy as np
import os as os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import TTIMG

class TableWindow(QWidget):
    def __init__(self,size):
        """
        Initializes the popup window where the user inputs their own lifetime
        matrix through a QTableWidget.

        Parameters
        ----------
        size : int
            Size of the square table.

        Returns
        -------
        None.

        """
        super(QWidget,self).__init__()
        self.ui = loadUi("table_gui.ui",self)
        self.ui.custom_Matrix.setRowCount(size)
        self.ui.custom_Matrix.setColumnCount(size)
        self.ui.save.clicked.connect(self.onSave)
        self.setWindowModality(Qt.ApplicationModal)
        
    def readTable(self):
        """
        Reads the lifetime matrix input by the user and saves the matrix in a
        numpy array as an attribute.

        Returns
        -------
        None.

        """
        row = self.ui.custom_Matrix.rowCount()
        col = self.ui.custom_Matrix.columnCount()
        K = np.zeros((row,col))
        for i in range(row):
            for j in range(col):
                if self.ui.custom_Matrix.item(i,j) == None:
                    K[i][j] = 0
                else:
                    K[i][j] = float(self.ui.custom_Matrix.item(i,j).text())
        self.custom_matrix = K
        
    def onSave(self):
        """
        Executes the readTable function and closes the popup window, when the 
        user clicks the "Save"-Button.

        Returns
        -------
        None.

        """
        self.readTable()
        self.close()

class FailSafeWindow(QWidget):
    def __init__(self,msg):
        """
        Initializes the failsafe popup window, where the most common GUI input
        errors will be displayed in a QTextEdit.

        Parameters
        ----------
        msg : string
            Description of the user error.

        Returns
        -------
        None.

        """
        super(QWidget,self).__init__()
        self.ui = loadUi("failsafe_gui.ui",self)
        self.ui.closeFailsafe.clicked.connect(lambda: self.close)
        self.ui.textFailsafe.setText(msg)
        self.setWindowModality(Qt.ApplicationModal)
        
class ResultsWindow(QWidget):
    def __init__(self, model, Controller, fit_report):
        """
        Initializes the results popup window, where the results of the fitting
        routine will be displayed in a QTextEdit.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the GLA. For GTA it can be a
            number 1-10 or "custom" for a custom model.
        Controller : Controller
            An Object of the Controller class.
        fit_report : string
            The report of the minimize routine by lmfit.

        Returns
        -------
        None.

        """
        super(QWidget,self).__init__()
        self.ui = loadUi("results_gui.ui",self)
        self.ui.closeResults.clicked.connect(lambda: self.close)
        self.setText(model, Controller, fit_report)
        
    def setText(self, model, Controller, fit_report):
        """
        Fills the QTextEdit object with the corresponding data.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the GLA. For GTA it can be a
            number 1-10 or "custom" for a custom model.
        Controller : Controller
            An Object of the Controller class.
        fit_report : string
            The report of the minimize routine by lmfit.

        Returns
        -------
        None.

        """
        self.ui.textResults.clear()
        text = Controller.getResults(model)
        self.ui.textResults.append(text)
        self.ui.textResults.append(fit_report)
   
class PlotViewer(QWidget):
    def __init__(self, fig):
        """
        Initializes the PlotViewer popup window, where the plots given by
        the program can be slightly modified.

        Parameters
        ----------
        fig: matplotlib.pyplot.figure
            The figure containing the plot.

        Returns
        -------
        None.

        """
        super(PlotViewer,self).__init__()
        self.ui = loadUi("plotviewer_gui.ui",self)
        plot = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar(plot, self)
        self.ui.verticalLayout.addWidget(toolbar)
        self.ui.verticalLayout.addWidget(plot)

class MainWindow(QMainWindow):
    def __init__(self): 
        super(MainWindow,self).__init__()
        self.ui = loadUi("gui.ui",self)
        self.startUp()
        self.functionality()
  
    def startUp(self):
        """
        Ensures that upon startup everything is shown correctly. Sets the 
        GUI to show the widgets in the right order.

        Returns
        -------
        None.

        """
        self.default_palette = QGuiApplication.palette()
        self.finalInputs = {}
        self.PltView = []
        self.ui.user_input_tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.radios = QButtonGroup(self)
        self.radios.addButton(self.ui.GLA_radio)
        self.radios.addButton(self.ui.GTA_radio_preset_model)
        self.radios.addButton(self.ui.GTA_radio_custom_model)
        self.radios.addButton(self.ui.GTA_radio_custom_matrix)
        self.ui.stack.setCurrentIndex(0)
        self.ui.Theme.setChecked(False)
        self.changeTheme()
        
        
    def onQuit(self):
        """
        Resets the color theme of the application and saves input values.

        Returns
        -------
        None.

        """
        EfsTA.setPalette(self.default_palette)
        self.savePickle()
        
    def functionality(self):
        """
        Adds functionality to the respective UI element.

        Returns
        -------
        None.

        """
        self.ui.stack.currentChanged.connect(self.presentInputs)
        self.ui.Data_browse.clicked.connect(self.selectFolderPath)
        self.ui.Theme.stateChanged.connect(self.changeTheme)
        self.ui.user_confirm.clicked.connect(self.finalCheck)      
        self.ui.GTA_input_custom_model_saved_equations.currentIndexChanged.connect(lambda: self.setCustomModel(self.ui.GTA_input_custom_model_saved_equations.currentIndex()))
        self.ui.Data_clear_cache.clicked.connect(self.clearPickle)
        self.ui.GTA_open_table.clicked.connect(self.checkIfCustomMatrixSizeEmpty)
        self.ui.Plotting_plot.clicked.connect(self.onlyPlotting)
        self.ui.plot_fitted.stateChanged.connect(self.disableFitted)
        self.ui.GTA_custom_model_save.clicked.connect(self.saveCustomModel)
        self.ui.GTA_custom_model_del.clicked.connect(self.deleteCustomModel)
        EfsTA.aboutToQuit.connect(self.onQuit)      
        
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
            
    def checkIfMethodSelected(self):
        if(self.ui.GLA_radio.isChecked() == False and 
           self.ui.GTA_radio_preset_model.isChecked() == False and 
           self.ui.GTA_radio_custom_model.isChecked() == False and 
           self.ui.GTA_radio_custom_matrix.isChecked() == False):
            self.openFailSafe("Please select an evaluation method.")
            return False
            
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
    
    def checkIfCustomMatrixSizeEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.GTA_input_rows_and_columns.value() !=  0:
            self.openPopUpMatrixInput(self.ui.GTA_input_rows_and_columns.value())
        else:
            self.openFailSafe("Please input table size.")
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
        if hasattr(self, 'custom_matrix') == False:
            self.openFailSafe("Please input custom reaction rate constant matrix.")
            return True
        
    def checkIfGLATauEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if (self.ui.GLA_user_input_tau_fix.text() == "" and self.ui.GLA_user_input_tau_var.text() == ""):
            self.openFailSafe("Please input guessed decay times.")
            return True

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
            self.openFailSafe("Please choose a folder directory.")
            return True

    def checkIfPlotChoicesEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if (self.ui.plot_raw.isChecked() == False 
            and self.ui.plot_fitted.isChecked() == False):
            self.openFailSafe("Please choose which data to plot.")
            return True
        else:
            if (self.ui.plot_wavelength_slices.isChecked() == False and
                self.ui.plot_delay_slices.isChecked() == False and
                self.ui.plot_heatmap.isChecked() == False and
                self.ui.plot_three_in_one.isChecked() == False and
                self.ui.plot_residuals.isChecked() == False and 
                self.ui.plot_concentrations.isChecked() == False and 
                self.ui.plot_das_sas.isChecked() == False and
                self.ui.plot_threed_contour.isChecked() == False):
                self.openFailSafe("Please choose which data to plot.")
                return True
            
        def checkIfCustomModelEmpty(self):
            if self.ui.GTA_input_custom_model_equation.text() == "":
               self.openFailSafe("Please input a reaction equation.")
               return True
            elif self.ui.GTA_user_input_custom_model_tau.text() == "":
                self.openFailSafe("Please input lifetimes.")
                return True
            
    def finalCheck(self):
        """
        Checks all required data fields before starting the program.

        Returns
        -------
        None.

        """
        self.checkIfWavelengthSlicesEmpty()
        self.checkIfDelaySlicesEmpty()
        if (self.checkIfPlotChoicesEmpty() == True or self.checkIfBrowseEmpty() == True):
            pass
        if (self.ui.plot_fitted.isChecked() == False):
            self.programStart()
        if (self.checkIfMethodSelected() == False):
            pass
        if (self.ui.GLA_radio.isChecked() == True and 
            self.checkIfGLATauEmpty() == True):
            pass
        elif (self.ui.GTA_radio_preset_model.isChecked() == True and 
              self.checkIfPresetModelTauEmpty() == True):
            pass
        elif (self.ui.GTA_radio_custom_model.isChecked() == True and 
              self.checkIfCustomModelEmpty() == True):
            pass
        elif (self.ui.GTA_radio_custom_matrix.isChecked() == True and 
              self.checkCustomMatrixIfEmpty() == True):
            pass
        else:
            self.programStart()

    def programStart(self):
        """
        Starts the program creating a controller object and saving the user 
        inputs. Executes the corresponding plotting/calculation, 
        depending on the model chosen by the user. Opens a popup with the 
        results.

        Returns
        -------
        None.

        """
        self.Controller = Cont.Controller(self.getFolderPath())
        self.savePickle()
        ds = sorted(self.getDelaySlices())
        ws = sorted(self.getWavelengthSlices())
        db = [self.getLowerDelayBound(), self.getUpperDelayBound()]
        wb = [self.getLowerWavelengthBound(), self.getUpperWavelengthBound()]
        
        if self.GLA_radio.isChecked() == True:
            model = 0
            self.calculationGLA(db, wb)
            self.plottingDAS(ds,ws)
        
        elif self.GTA_radio_preset_model.isChecked() == True:
            model = self.getPresetModel()+1
            K = np.array(self.getGTAPresetModelTaus())
            self.calculationGTA(db,wb,model,K)
            self.plottingSAS(ds,ws, self.tau_fit)
        
        elif self.GTA_radio_custom_model.isChecked() == True:
            model = "custom model"
            K = self.getUserModel()
            self.calculationGTA(db,wb,model,K)
            self.plottingSAS(ds,ws, self.tau_fit)
        
        elif self.GTA_radio_custom_matrix.isChecked() == True:
            model = "custom matrix"
            K = self.custom_matrix
            self.calculationGTA(db,wb,model,K)
            self.plottingSAS(ds,ws, self.tau_fit)

    def onlyPlotting(self):
        ds = sorted(self.getDelaySlices())
        ws = sorted(self.getWavelengthSlices())
        # db = [self.getLowerDelayBound(), self.getUpperDelayBound()]
        # wb = [self.getLowerWavelengthBound(), self.getUpperWavelengthBound()]
        
        if self.GLA_radio.isChecked() == True:
            model = 0
            self.plottingDAS(ds,ws)
        
        elif self.GTA_radio_preset_model.isChecked() == True:
            model = self.getPresetModel()+1
            self.plottingSAS(ds,ws, model)
        
        elif self.GTA_radio_custom_model.isChecked() == True:
            model = "custom model"
            self.plottingSAS(ds,ws, model)
        
        elif self.GTA_radio_custom_matrix.isChecked() == True:
            model = "custom matrix"
            self.plottingSAS(ds,ws, model)

    def calculationGLA(self,db,wb):
        
        #raw
        self.Controller.createOrigData(db,wb, self.getGTAOptMethod(), None) 
        #fit
        self.tau_fit, spec, res, D_fit, fit_report = self.Controller.calcDAS(self.getGLATaus(), db, wb, self.getGLAOptMethod())
        self.openPopUpResults(0, self.Controller, fit_report)
        
    def calculationGTA(self,db,wb,model,K):
        K =  np.array(K)
        
        #raw
        self.Controller.createOrigData(db,wb, self.getGTAOptMethod(), self.getGTAIvpMethod())
        #fit
        self.tau_fit, spec, res, D_fit, fit_report = self.Controller.calcSAS(K, self.getCustomConcentration(), db, wb,
                    model,self.getPresetModelTauBounds()[0], self.getPresetModelTauBounds()[1],self.getGTAOptMethod(), self.getGTAIvpMethod())
        self.openPopUpResults(model, self.Controller, fit_report)
        
    def plottingDAS(self,ds,ws):
        """
        Creates the plots selected by the user and opens them in popup windows
        for inspection/modification.
        
        Parameters
        ----------
        ds : list
            The specific delay values the user wants to examine.
        ws : list
            The specific wavelenght values the user wants to examine..

        Returns
        -------
        None.

        """
    
        if self.ui.plot_raw.isChecked() == True:
            if self.ui.plot_wavelength_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, None, self.getUserContour(), "3", self.getMultiplier(), add="3")
                self.openPlotViewer(plot)
            if self.ui.plot_delay_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, None, self.getUserContour(), "1", self.getMultiplier(), add="1")
                self.openPlotViewer(plot)
            if self.ui.plot_heatmap.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, None, self.getUserContour(), "2", self.getMultiplier(), add="2")
                self.openPlotViewer(plot)
            if self.ui.plot_three_in_one.isChecked() == True:
                plot = self.Controller.plot3OrigData(ws, ds, None, None, self.getUserContour(), self.getMultiplier(), self.getGTAOptMethod(), self.getGTAIvpMethod())
                self.openPlotViewer(plot)
            if self.ui.plot_threed_contour.isChecked() == True:
                plot = self.Controller.plot3DOrigData(None, None, self.getMultiplier(), self.getGTAOptMethod(), self.getGTAIvpMethod())
                self.openPlotViewer(plot)
        
        if self.ui.plot_fitted.isChecked() == True:
            if self.ui.plot_wavelength_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, 0, self.getUserContour(), "3", self.getMultiplier(), add="3")
                self.openPlotViewer(plot)
            if self.ui.plot_delay_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, 0, self.getUserContour(), "1", self.getMultiplier(), add="1")
                self.openPlotViewer(plot)
            if self.ui.plot_heatmap.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, 0, self.getUserContour(), "2", self.getMultiplier(), add="2")
                self.openPlotViewer(plot)
            if self.ui.plot_three_in_one.isChecked() == True:
                plot = self.Controller.plot3FittedData(ws, ds, None, None, 0, self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_threed_contour.isChecked() == True:
                plot = self.Controller.plot3DFittedData(None, None, 0, self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_residuals.isChecked() == True:
                plot = self.Controller.plot2Dresiduals(None,None,0,self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_das_sas.isChecked() == True:
                plot = self.Controller.plotDAS(0, self.tau_fit, self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_concentrations.isChecked() == True:
                plot = self.Controller.plotKinetics(0)
                self.openPlotViewer(plot)
            
    def plottingSAS(self,ds,ws,model):
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
            number 1-10 or "custom" for a custom model.
        K : np.ndarray
            The reaction rate matrix.
        Returns
        -------
        None.

        """
        
        if self.ui.plot_raw.isChecked() == True:
            if self.ui.plot_wavelength_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, None, self.getUserContour(), "3", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_delay_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, None, self.getUserContour(), "1", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_heatmap.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, None, self.getUserContour(), "2", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_three_in_one.isChecked() == True:
                plot = self.Controller.plot3OrigData(ws, ds, None, None, self.getUserContour(), self.getMultiplier(), self.getGTAOptMethod(), self.getGTAIvpMethod())
                self.openPlotViewer(plot)
            if self.ui.plot_threed_contour.isChecked() == True:
                plot = self.Controller.plot3DOrigData(None, None, self.getMultiplier(), self.getGTAOptMethod(), self.getGTAIvpMethod())
                self.openPlotViewer(plot)
                
        if self.ui.plot_fitted.isChecked() == True:
            if self.ui.plot_wavelength_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, model, self.getUserContour(), "3", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_delay_slices.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, model, self.getUserContour(), "1", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_heatmap.isChecked() == True:
                plot = self.Controller.plotCustom(ws, ds, None, None, model, self.getUserContour(), "2", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_three_in_one.isChecked() == True:
                plot = self.Controller.plot3FittedData(ws, ds, None, None, model, self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_threed_contour.isChecked() == True:
                plot = self.Controller.plot3DFittedData(None, None, model, self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_residuals.isChecked() == True:
                plot = self.Controller.plot2Dresiduals(None, None, model, self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_das_sas.isChecked() == True:
                plot = self.Controller.plotDAS(model, self.tau_fit, self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.plot_concentrations.isChecked() == True:
                plot = self.Controller.plotKinetics(model)
                self.openPlotViewer(plot)
                
    def disableFitted(self):
        """
        Makes sure fitting dependent plots can't be selected if only raw data
        is selected.

        Returns
        -------
        None.

        """
        if self.ui.plot_fitted.isChecked() == False:
            self.ui.plot_concentrations.setChecked(False)
            self.ui.plot_concentrations.setEnabled(False)
            self.ui.plot_das_sas.setChecked(False)
            self.ui.plot_das_sas.setEnabled(False)
            self.ui.plot_residuals.setChecked(False)
            self.ui.plot_residuals.setEnabled(False)
        else:
            self.ui.plot_concentrations.setEnabled(True)
            self.ui.plot_das_sas.setEnabled(True)
            self.ui.plot_residuals.setEnabled(True)
            
    def getFolderPath(self):
        """
        Checks if a folder directory was selected and returns it.

        Returns
        -------
        self.ui.folderpath.text() : string
            The folder directory.

        """
        if self.ui.Data_directory == "":
            self.openFailSafe("Please select a folder directory.")
        else:
            return self.ui.Data_directory.text()
        
    def getDelaySlices(self):
        """
        Reads the delays input by the user if empty, returns preset values.

        Returns
        -------
        user_delays: list
            A list containing the delays input by the user.

        """
        if self.ui.plot_input_delay_slices.text() == "":
            delay_slices = []
        else: 
            delay_slices = self.ui.plot_input_delay_slices.text().split(',')
            for i in range(len(delay_slices)):
                if delay_slices[i] != "":
                    delay_slices[i] = float(delay_slices[i])
        return delay_slices
    
    def getWavelengthSlices(self):
        """
        Reads the lambdas input by the user if empty, returns preset values.

        Returns
        -------
        user_lambdas: list
            A list containing the lambdas input by the user.

        """
        if self.ui.plot_input_wavelength_slices.text() == "":
            wavelength_slices = []
        else:
            wavelength_slices = self.ui.plot_input_wavelength_slices.text().split(',')
            for i in range(len(wavelength_slices)):
                if wavelength_slices[i] != "":
                    wavelength_slices[i] = float(wavelength_slices[i])
        return wavelength_slices

    def getLowerDelayBound(self):
        """
        Reads the lower delay bound input by the user if empty returns preset
        a value.

        Returns
        -------
        delay_lb: float
            The lower delay bound input by the user.

        """
        if self.ui.Data_delay_input_lb.text() == "":
            delay_lb = None
        else:
            lb_text=self.ui.Data_delay_input_lb.text()
            delay_lb = float(lb_text)
        return delay_lb
        
    def getUpperDelayBound(self):
        """
        Reads the upper delay bound input by the user if empty returns preset
        a value.

        Returns
        -------
        delay_ub: float
            The upper delay bound input by the user.

        """
        if self.ui.Data_delay_input_ub.text() == "":
            delay_ub = None
        else:
            ub_text=self.ui.Data_delay_input_ub.text()
            delay_ub = float(ub_text)
        return delay_ub
    
    
    def getLowerWavelengthBound(self):
        """
        Reads the lower lambda bound input by the user if empty returns preset
        a value.

        Returns
        -------
        lambda_lb: float
            The lower lambda bound input by the user.

        """
        if self.ui.Data_wavelength_input_lb.text() == "":
            lambda_lb = None
        else:
            lb_text=self.ui.Data_wavelength_input_lb.text()
            lambda_lb = float(lb_text)
        return lambda_lb
    
    def getUpperWavelengthBound(self):
        """
        Reads the upper lambda bound input by the user if empty returns preset
        a value.

        Returns
        -------
        lambda_ub: float
            The upper lambda bound input by the user.

        """
        if self.ui.Data_wavelength_input_ub.text() == "":
            lambda_ub = None
        else:
            ub_text=self.ui.Data_wavelength_input_ub.text()
            lambda_ub = float(ub_text)
        return lambda_ub
    
    def getUserContour(self):
        """
        Reads the contour input by the user if empty returns preset value.

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
    
    def getMultiplier(self):
        """
        Reads the ΔA data multiplier input by the user if empty returns 
        preset value.

        Returns
        -------
        mul : int
            The multiplier for the ΔA data input by the user.

        """
        if (self.ui.Data_input_multiplier.text() == "" or 
            int(self.ui.Data_input_multiplier.text()) <=0):
            mul = 1
        else:
            mul = int(self.ui.Data_input_multiplier.text())
        return mul

    def getGLATaus(self):
        """
        Checks which lifetime guesses are given (fixed, variable or both) and 
        reads them.

        Returns
        -------
        list
            The lifetimes input by the user.

        """
        tau_var = self.ui.GLA_user_input_tau_var.text().split(',')
        tau_fix = self.ui.GLA_user_input_tau_fix.text().split(',')
        for i in range(len(tau_var)):
            if tau_var[i] != "":
                tau_var[i] = float(tau_var[i])
        for i in range(len(tau_fix)):
            if tau_fix[i] != "":
                tau_fix[i] = float(tau_fix[i])
        if any(isinstance(obj,float) for obj in tau_var):
            tau_var = [None if item == '' else item for item in tau_var]
        else:
            tau_var = []
            
        if any(isinstance(obj,float) for obj in tau_fix):
            tau_fix = [None if item == '' else item for item in tau_fix]
        else:
            tau_fix = [] 
        return [tau_fix, tau_var]
    
    def getGTAPresetModelTaus(self):
        """
        Reads the lifetimes input by the user, if a linear model is 
        selected.

        Returns
        -------
        tau : list
            The lifetimes input by the user.

        """
        if self.ui.GTA_input_preset_model_tau.text() == "":
            tau = []
        else:
            tau = self.ui.GTA_input_preset_model_tau.text().split(',')
            for i in range(len(tau)):
                if tau[i] != "":
                    tau[i] = float(tau[i])
        return tau
    
    def getPresetModelTauBounds(self):
        """
        Reads the bounds for the lifetimes during the calculation.

        Returns
        -------
        list
            A list containing the lower bounds and upper bounds list.

        """
        tau_lb = self.ui.GTA_input_preset_model_tau_lb.text().split(',')
        tau_ub = self.ui.GTA_input_preset_model_tau_ub.text().split(',')
        for i in range(len(tau_lb)):
            if tau_lb[i] != "":
                tau_lb[i] = float(tau_lb[i])
        for i in range(len(tau_ub)):
            if tau_ub[i] != "":
                tau_ub[i] = float(tau_ub[i])
        if any(isinstance(obj,float) for obj in tau_lb):
            tau_lb = [None if item == '' else item for item in tau_lb]
        else:
            tau_lb = []
            
        if any(isinstance(obj,float) for obj in tau_ub):
            tau_ub = [None if item == '' else item for item in tau_ub]
        else:
            tau_ub = []
        return [tau_lb,tau_ub]
        
    def getCustomConcentration(self):
        """
        Reads the concentration vector input by the user and returns it.

        Returns
        -------
        c0 : list
            The concentration vector set by the user.

        """
        c0 = self.ui.GTA_concentration.text().split(',')
        for i in range(len(c0)):
            if c0[i] != "":
                c0[i] = float(c0[i])
        if any(isinstance(obj,float) for obj in c0):
            c0 = c0
        else:
            c0 = []
        return c0
    
    def getPresetModel(self):
        """
        Returns the current selected kinetic model.
        Returns
        -------
        int
            The integer corresponding to a kinetic model.

        """
        return self.ui.GTA_preset_model_selection.currentIndex()
    
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

    def getUserModel(self):
        '''
        Transforms the custom model input by the user as a reaction equation into the corresponding reaction matrix with the input lifetimes.

        Returns
        -------
        M : TYPE
            DESCRIPTION.

        '''
        #dictionary used to convert species names to corresponding matrix coordinates
        letterstonumbers = {"A":0,
                            "B":1,
                            "C":2,
                            "D":3,
                            "E":4,
                            "F":5,
                            "G":6,
                            "H":7,
                            "I":8,
                            "J":9,
                            "K":10,
                            "L":11,
                            "M":12,
                            "N":13,
                            "O":14,
                            "P":15,
                            "Q":16,
                            "R":17,
                            "S":18,
                            "T":19,
                            "U":20,
                            "V":21,
                            "W":22,
                            "X":23,
                            "Y":24,
                            "Z":25,
                            "v":-1 #not a coordinate just a mean to identify void decays
                            }
        #GUI input 
        eq = self.ui.GTA_input_custom_model_equation.text()

        tau = self.ui.GTA_user_input_custom_model_tau.text().split(',')

        #checks if the equation used arrows
        arrow = False
        if "->" in eq:
            arrow = True
        #checks if there are any void reactions
        void = False
        if "v" in eq:
            void = True
        #splitting different decay paths
        eq_split = eq.split(";")
        #splitting each path into involved species     
        separated_species = []
        if arrow == True:
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
            for i in range(len(list_)-1):
                paired_species.append([list_[i],list_[i+1]])
        #converting species names to numbers for matrix coordinates
        for list_ in paired_species:
            for i in range(len(list_)):
                list_[i] = letterstonumbers[list_[i]]
        #determining and creating the matrix dimensions by unique species
        all_letters = np.array(paired_species).flatten()
        if void == False:
            species = len(np.unique(all_letters))
        else:
            species = len(np.unique(all_letters)) - 1
        M = np.zeros((species,species))
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
        N = np.ones((species,species))
        np.fill_diagonal(N,-1)
        M = M*N
        if M[-1][-1] == -0:
           M[-1][-1] *= -1 
        return M
    
    def saveCustomModel(self):
        """
        Saves the currently input reaction equation to the combobox.

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
        Deletes the currently selected reaction equation from the combobox.

        Returns
        -------
        None.

        """
        if self.ui.GTA_input_custom_model_saved_equations.currentText() == "":
            pass
        else:
            self.ui.GTA_input_custom_model_saved_equations.removeItem(self.ui.GTA_input_custom_model_saved_equations.currentIndex())
 
    def setCustomModel(self,ind):
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
 
    def closePopupMatrix(self,popup):
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
        self.custom_matrix = popup.custom_matrix
        popup.close()
    
    def openPopUpMatrixInput(self,size):
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
        popup = TableWindow(size)
        popup.show()
        popup.save.clicked.connect(lambda: self.closePopupMatrix(popup))       

    def openPopUpResults(self, model, Controller, fit_report):
        """
        Opens up the results popup window.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the GLA. For GTA it can be a
            number 1-10 or "custom" for a custom model.
        Controller : Controller
            DESCRIPTION.
        fit_report : string
            The results of the fit and some goodness of fit statistics.

        Returns
        -------
        None.

        """
        self.resultView = ResultsWindow(model, Controller, fit_report)
        self.resultView.show()
        self.resultView.closeResults.clicked.connect(lambda: self.resultView.close())
        
    def openFailSafe(self,msg):
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
        popup = FailSafeWindow(msg)
        popup.show()
        popup.closeFailsafe.clicked.connect(lambda: popup.close())

    def openPlotViewer(self,fig):
        """
        Opens up a plotviewer popup window for each plot selected by the user.
        Can take a moment if many plots were selected, might be improved in the
        future.

        Parameters
        ----------
        fig: matplotlib.pyplot.figure
            The figure containing the plot.

        Returns
        -------
        None.

        """
        popup = PlotViewer(fig)
        popup.show()
        if hasattr(self, "pltView") == False:
            self.pltView = []
        self.pltView.append(popup)

    def presentInputs(self,ind):
        '''
        Presents all relevant user inputs in a treewidget.

        Parameters
        ----------
        ind : int
            The index of the user input display tab widget.

        Returns
        -------
        None.

        '''
        if ind == 5:
            self.saveAllInputs()
            iterator = QTreeWidgetItemIterator(self.ui.user_input_tree)
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
                if (item.text(0) == 'GLA' and item.text(0) in self.finalInputs):
                    item.setExpanded(True)
                if item.text(0) == 'GTA':
                    GTA_pointer = item
                if (item.text(0) == 'Preset Model' and self.ui.GTA_radio_preset_model.isChecked() == True):
                    item.setExpanded(True)
                    GTA_pointer.setExpanded(True)
                elif (item.text(0) == 'Custom Model' and self.ui.GTA_radio_custom_model.isChecked() == True):
                    item.setExpanded(True)
                    GTA_pointer.setExpanded(True)
                elif (item.text(0) == 'Custom Matrix' and self.ui.GTA_radio_custom_matrix.isChecked() == True):
                    item.setExpanded(True)    
                    GTA_pointer.setExpanded(True)
                iterator+=1
            algorithm_pointer.setExpanded(True)
    
        
    def saveAllInputs(self):
        '''
        Saves all user inputs in a dictionary to pickle and display them.

        Returns
        -------
        None.

        '''
        self.finalInputs.clear()
        self.finalInputs['Lower Delay Bound'] = self.ui.Data_delay_input_lb.text()
        self.finalInputs['Upper Delay Bound'] = self.ui.Data_delay_input_ub.text()
        self.finalInputs['Lower Wavelength Bound'] = self.ui.Data_wavelength_input_lb.text()
        self.finalInputs['Upper Wavelength Bound'] = self.ui.Data_wavelength_input_ub.text()
        self.finalInputs['Data Multiplier'] = self.ui.Data_input_multiplier.text()
        self.finalInputs['Selected Data'] = ''
        self.finalInputs['Directory'] = self.getFolderPath()
        if self.ui.GLA_radio.isChecked() == True:
            self.finalInputs['GLA'] = "Selected"
            self.finalInputs['Optimizer'] = self.ui.GLA_algorithm_optimize.currentText()
            self.finalInputs['Variable Taus'] = self.ui.GLA_user_input_tau_var.text()
            self.finalInputs['Fixed Taus'] = self.ui.GLA_user_input_tau_fix.text()
        if self.ui.GTA_radio_preset_model.isChecked() == True:
            self.finalInputs['Preset Model'] = "Selected"
            self.finalInputs['Concentrations'] = self.ui.GTA_concentration.text()
            self.finalInputs['Model'] = self.ui.GTA_preset_model_selection.currentText()
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Taus'] = self.ui.GTA_input_preset_model_tau.text()
            self.finalInputs['Lower Tau Bounds'] = self.ui.GTA_input_preset_model_tau_lb.text()
            self.finalInputs['Upper Tau Bounds'] = self.ui.GTA_input_preset_model_tau_ub.text()
            self.finalInputs['Preset Model Index'] = self.ui.GTA_preset_model_selection.currentIndex()+1
        if self.ui.GTA_radio_custom_model.isChecked() == True:
            self.finalInputs['Custom Model'] = "Selected"
            self.finalInputs['Concentrations'] = self.ui.GTA_concentration.text()
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Model'] = self.ui.GTA_input_custom_model_equation.text()
            self.finalInputs['Taus'] = self.ui.GTA_user_input_custom_model_tau.text()
            self.finalInputs['Lower Tau Bounds'] = self.ui.GTA_user_input_custom_model_tau_lb.text()
            self.finalInputs['Upper Tau Bounds'] = self.ui.GTA_user_input_custom_model_tau_ub.text()
            self.finalInputs['Saved Models'] = [self.ui.GTA_input_custom_model_saved_equations.itemText(i) for i in range(self.ui.GTA_input_custom_model_saved_equations.count())]
        if self.ui.GTA_radio_custom_matrix.isChecked() == True:
            self.finalInputs['Custom Matrix'] = "Selected"
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Concentrations'] = self.ui.GTA_concentration.text()
            self.finalInputs['Matrix'] = str(self.custom_matrix)
        if self.ui.plot_raw.isChecked() == True:
            self.finalInputs['Selected Data'] = ', Raw Data'
        if self.ui.plot_fitted.isChecked() == True:
            self.finalInputs['Selected Data'] += ', Fitted Data'
        if self.ui.plot_das_sas.isChecked() == True:
            self.finalInputs['Selected Plots'] = ', DAS/SAS' 
        if self.ui.plot_delay_slices.isChecked() == True:
            self.finalInputs['Selected Plots'] += ', Delay Slices'
        if self.ui.plot_heatmap.isChecked() == True:
            self.finalInputs['Selected Plots'] += ', Heatmap'
        if self.ui.plot_wavelength_slices.isChecked() == True:
            self.finalInputs['Selected Plots'] += ', Wavelength Slices'
        if self.ui.plot_concentrations.isChecked() == True:
            self.finalInputs['Selected Plots'] += ', Kinetics'
        if self.ui.plot_residuals.isChecked() == True:
            self.finalInputs['Selected Plots'] += ', Residuals'
        if self.ui.plot_three_in_one.isChecked() == True:
            self.finalInputs['Selected Plots'] += ', Three In One'
        if self.ui.plot_threed_contour.isChecked() == True:
            self.finalInputs['Selected Plots'] += ', 3D Contour'
        if self.ui.plot_input_contour.value() !=0:
            self.finalInputs['Contour Lines'] = str(self.ui.plot_input_contour.value())
        else:
            self.finalInputs['Contour Lines'] = str(20)
        self.finalInputs['Delay Slices'] = self.ui.plot_input_delay_slices.text()      
        self.finalInputs['Wavelength Slices'] = self.ui.plot_input_wavelength_slices.text()
        self.finalInputs['Selected Data'] = self.finalInputs['Selected Data'][2:]
        self.finalInputs['Selected Plots'] = self.finalInputs['Selected Plots'][2:]
        

    def selectFolderPath(self):
        '''
        Opens a filedialog window for the user to select the folder directory, where the data is stored.

        Returns
        -------
        None.

        '''
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.ui.Data_directory.setText(directory)
        self.finalInputs['Directory'] = directory 
        if self.ui.Data_directory.text() != "":
            C = Cont.Controller(directory)
            path = C.path+"/"
            names = ["delays_filename","lambdas_filename", "spectra_filename"]
            if all(hasattr(C, attr) for attr in names) == False:
                self.openFailSafe('Please make sure the selected folder ' + 
                                  'contains *.txt files with "spectra",' + 
                                  '"delays" and "lambda" in their name.')
            else:
                temp = C.delays_filename[::-1]
                temp = temp.index("/")
                name = C.delays_filename[-temp:-11]
                txt = name+"_pickle"
                pickle = path + txt + ".dir"
                if os.path.isfile(pickle):
                    self.setPickle()
        

    def changeTheme(self):
        """
        Changes the colour theme of the program to either light or dark.

        Returns
        -------
        None.

        """
        if self.ui.Theme.isChecked() == True:
            EfsTA.setPalette(self.default_palette)
        else:
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
            EfsTA.setPalette(darkmode)
            
    def savePickle(self):
        '''
        Pickles the data, if a path was selected and therefore the controller object generated.

        Returns
        -------
        None.

        '''
        if hasattr(self, 'Controller') == True:
            self.Controller.pickleData(self.finalInputs)

    def getPickle(self):
        """
        Reloads the saved user inputs.

        Returns
        -------
        None.

        """
        if hasattr(self, 'Controller') == False:
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
            models = self.shelf["Saved Custom Models"]
            for i in range(len(models)):
                self.ui.GTA_input_custom_model_saved_equations.addItem(models[i])
        if "Custom Matrix" in self.shelf:
            self.custom_matrix = self.shelf["Matrix"]
        for key in self.shelf:
            val = str(self.shelf[key])
            val = val.replace("[","")
            val = val.replace("]","")
            val = val.replace("None","")
            val = val.replace(" ","")
            if key == "Data Multiplier":
                self.ui.Data_input_multiplier.setText(val)
            if key == "Lower Delay Bound":
                self.ui.Data_delay_input_lb.setText(val)
            if key == "Upper Delay Bound":
                self.ui.Data_delay_input_ub.setText(val)
            if key == "Lower Wavelength Bound":
                self.ui.Data_wavelength_input_lb.setText(val)
            if key == "Upper Wavelength Bound":
                self.ui.Data_wavelength_input_ub.setText(val)
            if key == "GLA":
                self.ui.GLA_radio.setChecked(True)
            if key == "Preset Model":
                self.ui.GTA_radio_preset_model.setChecked(True)
            if key == "Custom Model":
                self.ui.GTA_radio_custom_model.setChecked(True)
            if key == "Custom Matrix":
                self.ui.GTA_radio_custom_matrix.setChecked(True) 
            if self.ui.GLA_radio.isChecked() == True:
                if key == "Fixed Taus":
                    self.ui.GLA_user_input_tau_fix.setText(val)
                if key == "Variable Taus":
                    self.ui.GLA_user_input_tau_var.setText(val)
            if self.ui.GTA_radio_preset_model.isChecked() == True:
                if key == "Preset Model Index":
                    self.ui.GTA_preset_model_selection.setCurrentIndex(int(val)-1)
                if key == "Taus":
                    self.ui.GTA_input_preset_model_tau.setText(val)
                if key == "Lower Tau Bounds":
                    self.ui.GTA_input_preset_model_tau_lb.setText(val)
                if key == "Upper Tau Bounds":
                    self.ui.GTA_input_preset_model_tau_ub.setText(val)
            if self.ui.GTA_radio_custom_model.isChecked() == True:
               if key == "Model":
                   self.ui.GTA_input_custom_model_equation.setText(val)
               if key == "Taus":
                   self.ui.GTA_input_custom_model_tau.setText(val)
               if key == "Lower Tau Bounds":
                   self.ui.GTA_input_custom_model_tau_lb.setText(val)
               if key == "Upper Tau Bounds":
                   self.ui.GTA_input_custom_model_tau_ub.setText(val)
            if key == "Concentrations":
                self.ui.GTA_concentration.setText(val)
            if key == "Delay Slices":
                self.ui.plot_input_delay_slices.setText(val)
            if key == "Wavelength Slices":
                self.ui.plot_input_wavelength_slices.setText(val)
            if key == "Contour Lines":
                self.ui.plot_input_contour.setValue(int(val))

    def clearPickle(self):
        """
        Clears the set reloaded user inputs.

        Returns
        -------
        None.

        """
        for lineedit in self.findChildren(QLineEdit):
            if lineedit != self.ui.Data_directory:
                lineedit.clear()
        for spinbox in self.findChildren(QSpinBox):
            spinbox.setValue(0)
        for combobox in self.findChildren(QComboBox):
            combobox.setCurrentIndex(0)
        if hasattr(self, 'cm') == True:
            self.cm = None
            
if __name__ == '__main__':
    EfsTA = QApplication(sys.argv)
    EfsTA.setStyle('Fusion')
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(EfsTA.exec_())
