import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLineEdit, 
                             QSpinBox, QComboBox)
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import Controller as Cont
import numpy as np
import os as os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import TTIMG

''' 0.0 Additional classes'''

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
        self.CM = K
        
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
        
        ''' 1.0 MainWindow initiation'''
        
        super(MainWindow,self).__init__()
        self.ui = loadUi("gui.ui",self)
        self.startUp()
        self.PltView = []

        ''' 2.0 Button functionality '''

        ''' 2.1 Browse files '''
        
        self.browse.clicked.connect(self.selectFolderPath)
        
        ''' 2.2 SASorDAS Stacked Widget '''
        
        self.SAS_radio.toggled.connect(self.SASreset)
        self.DAS_radio.toggled.connect(self.DASreset)
        
        ''' 2.3 SAS Stacked Widget '''
        
        self.ui.SAS_next_eq.clicked.connect(self.checkEqIfEmpty)
        self.ui.SAS_next_lin.clicked.connect(self.checkLinIfEmpty)
        self.ui.SAS_back_ks_eq.clicked.connect(lambda: self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page1))
        self.ui.SAS_back_ks_lin.clicked.connect(lambda: self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page1))
        self.ui.SAS_back_fin.clicked.connect(lambda: self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page1))
        self.ui.SAS_next_model.clicked.connect(self.chooseModel)
        self.ui.SAS_next_custom.clicked.connect(self.checkUserMatrixIfEmpty)
        self.ui.SAS_back_custom.clicked.connect(lambda: self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page1))
        self.ui.SAS_table_custom.clicked.connect(self.checkRandCIfEmpty)
        self.ui.SAS_alg_done.clicked.connect(lambda: self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page6))
        self.ui.SAS_alg_back.clicked.connect(lambda: self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page1))
        
        ''' 2.4 DAS Stacked Widget '''
        
        self.ui.DAS_next.clicked.connect(self.checkTauIfEmpty)
        self.ui.DAS_back.clicked.connect(lambda: self.ui.DAS_stack.setCurrentWidget(self.ui.DAS_page2))
        self.ui.DAS_alg_back.clicked.connect(lambda: self.ui.DAS_stack.setCurrentWidget(self.ui.DAS_page1))
        self.ui.DAS_alg_done.clicked.connect(lambda: self.ui.DAS_stack.setCurrentWidget(self.ui.DAS_page3))
        ''' 2.5 Plot Stacked Widget '''
        
        self.ui.plot_next.clicked.connect(lambda: self.ui.Plot_stack.setCurrentWidget(self.ui.plot_page2))
        self.ui.plot_back.clicked.connect(lambda: self.ui.Plot_stack.setCurrentWidget(self.ui.plot_page1))
        self.ui.fitted.stateChanged.connect(self.disableFitted)
        ''' 2.6 Change GUI Theme '''

        self.ui.Theme.stateChanged.connect(self.changeTheme)
        
        ''' 2.7 Starting or closing the program '''
        
        self.OK.clicked.connect(self.finalCheck)
        self.cancel.clicked.connect(self.onCancel)
        
        ''' 2.8 Pickle '''
        
        self.clearCache.clicked.connect(self.clearPickle)
        
    ''' 3.0 Initiation '''
    
    def startUp(self):
        """
        Ensures that upon startup everything is shown correctly. Sets the 
        GUI to show the widgets in the right order.

        Returns
        -------
        None.

        """
        self.ui.SASorDAS_stack.setCurrentWidget(self.ui.SASorDAS_page3)
        self.ui.Plot_stack.setCurrentWidget(self.ui.plot_page1)
        self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page1)
        self.ui.DAS_stack.setCurrentWidget(self.ui.DAS_page1)
        self.ui.Theme.setChecked(False)
        self.changeTheme()
        self.ui.contour.setMinimum(0)
        self.ui.contour.setValue(0)
        self.ui.kinetics.setEnabled(False)
        
    ''' 4.0 Selecting Analysis methods '''
    
    ''' 4.1 SAS '''
        
    def SASreset(self):
        """
        Resets the widgets upon changing the analysis method.

        Returns
        -------
        None.

        """
        self.ui.SASorDAS_stack.setCurrentWidget(self.ui.SASorDAS_page2)
        self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page1)
        self.ui.fitted.setChecked(True)
        self.ui.kinetics.setEnabled(True)
        self.ui.kinetics.setChecked(True)

    def chooseModel(self):
        """
        Moves to the correct widget after the model for the GTA was 
        selected.

        Returns
        -------
        None.

        """
        if self.ui.SAS_modelSelect.currentText() == "Custom Model":
            self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page4)
        elif self.ui.SAS_modelSelect.currentIndex() <=1 or self.ui.SAS_modelSelect.currentIndex()>3:
            self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page3)
        else:
            self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page2)
    
    ''' 4.2 DAS '''
    
    def DASreset(self):
        """
        Resets the widgets upon changing the analysis method.

        Returns
        -------
        None.

        """
        self.ui.SASorDAS_stack.setCurrentWidget(self.ui.SASorDAS_page3)
        self.ui.fitted.setChecked(True)
        self.ui.kinetics.setEnabled(False)
        self.ui.kinetics.setChecked(False)

    ''' 5.0  Idiot Checkpoints '''
            
    def checkEqIfEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if (self.ui.ks_forwards_eq.text() and 
            self.ui.ks_backwards_eq.text()) != "":
            self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page5)
        else:
            self.openFailSafe("Please input all guessed reaction rates.")
            return True
    
    def checkLinIfEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.ks_forwards_lin.text() != "":
            self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page5)
        else:
            self.openFailSafe("Please input guessed reaction rates.")
            return True
    
    def checkRandCIfEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.rows_and_columns.value() !=  0:
            self.openPopUpMatrixInput(self.ui.rows_and_columns.value())
        else:
            self.openFailSafe("Please input table size.")
            return True
    
    def checkUserMatrixIfEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if hasattr(self, 'cm') == True:
            self.ui.SAS_stack.setCurrentWidget(self.ui.SAS_page5)
        else:
            self.openFailSafe("Please input custom reaction rate constant matrix.")
            return True
    
    def checkTauIfEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.tau_var.text() != "" or self.ui.tau_fix.text() != "":
            self.ui.DAS_stack.setCurrentWidget(self.ui.DAS_page2)
        else:
            self.openFailSafe("Please input guessed decay times.")
            return True

    def checkBrowseIfEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if self.ui.folderpath.text() == "":
            self.openFailSafe("Please choose a folder directory.")
            return True
            
    def checkPlotChoicesIfEmpty(self):
        """
        Checks if the required information is provided, if not opens up a popup
        window, letting the user know which information is missing.

        Returns
        -------
        bool
            True if empty.

        """
        if (self.ui.raw.isChecked() == False 
            and self.ui.fitted.isChecked() == False):
            self.openFailSafe("Please choose which data to plot.")
            return True
        else:
            if (self.ui.A_wave.isChecked() == False and
                self.ui.del_A.isChecked() == False and
                self.ui.heat.isChecked() == False and
                self.ui.three_in_one.isChecked() == False and
                self.ui.residuals.isChecked() == False and 
                self.ui.kinetics.isChecked() == False and 
                self.ui.reconstructed.isChecked() == False and
                self.ui.threeD_contour.isChecked() == False):
                self.openFailSafe("Please choose which data to plot.")
                return True
    
    def finalCheck(self):
        """
        Checks all required data fields before starting the program.

        Returns
        -------
        None.

        """
        if (self.checkPlotChoicesIfEmpty() or self.checkBrowseIfEmpty()) == True:
            pass
        else:
            if self.SAS_radio.isChecked() == True:
                if (self.ui.fitted.isChecked() == False):
                    self.programStart()
                elif ((self.ui.SAS_modelSelect.currentIndex() <=1 or
                     self.ui.SAS_modelSelect.currentIndex()>3) and 
                    self.checkLinIfEmpty() == True):
                    pass
                elif (self.ui.SAS_modelSelect.currentText() == "Custom Model" and 
                    self.checkUserMatrixIfEmpty() == True):
                    pass
                elif ((self.ui.SAS_modelSelect.currentIndex() == 2 or
                     self.ui.SAS_modelSelect.currentIndex() == 3) and 
                      self.checkEqIfEmpty() == True):
                    pass
                else:
                    self.programStart()
            else:
                if (self.ui.fitted.isChecked() == False):
                    self.programStart()
                elif self.checkTauIfEmpty() == True:
                    pass
                else:
                    self.programStart()

    ''' 6.0 Starting or closing '''

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
        ud = sorted(self.getUserDelay())
        uw = sorted(self.getUserWavelength())
        db = [self.getUserDelayBoundsLow(), self.getUserDelayBoundsUp()]
        wb = [self.getUserWavelengthBoundsLow(), self.getUserWavelengthBoundsUp()]
            
        if self.SAS_radio.isChecked() == True:
            if self.ui.SAS_modelSelect.currentText() == "Custom Model":
                model = "custom"
                self.plottingSAS(self.Controller, ud, uw, db, wb, "custom", self.getUserMatrix())
            elif self.ui.SAS_modelSelect.currentIndex() <=1 or self.ui.SAS_modelSelect.currentIndex()>3:
                model = self.getModel()+1
                self.plottingSAS(self.Controller, ud, uw, db, wb, model, np.array(self.getK_lin()))   
            else:
                model = self.getModel()+1
                self.plottingSAS(self.Controller, ud, uw, db, wb, model,np.array(self.getK_eq()).flatten())
        else:
            model = 0
            self.plottingDAS(self.Controller,ud,uw,db,wb)
        if self.ui.fitted.isChecked() == True:
            self.openPopUpResults(model, self.Controller, self.fit_report)
            
    def onCancel(self):
        """
        Saves the user inputs, if there are any, and then closes the program.

        Returns
        -------
        None.

        """
        if hasattr(self, 'Controller') == True:
            self.savePickle()
            self.close()
        else:
            self.close()

    ''' 7.0 Plotting functions '''

    def plottingDAS(self, Controller,ud,uw,db,wb):
        """
        Creates the plots selected by the user and opens them in popup windows
        for inspection/modification.
        
        Parameters
        ----------
        Controller : Controller
            DESCRIPTION.
        ud : list
            The specific delay values the user wants to examine.
        uw : list
            The specific wavelenght values the user wants to examine..
        db : list
            The lower and upper bound for the delay data.
        wb : list
            The lower and upper bound for the wavelength data.

        Returns
        -------
        None.

        """
    
        if self.ui.raw.isChecked() == True:
            Controller.createOrigData(db,wb, self.getDASOptMethod(), None) 
            if self.ui.A_wave.isChecked() == True:
                plot = Controller.plotCustom(uw, ud, None, None, None, self.getUserContour(), "3", self.getMultiplier(), add="3")
                self.openPlotViewer(plot)
            if self.ui.del_A.isChecked() == True:
                plot = Controller.plotCustom(uw, ud, None, None, None, self.getUserContour(), "1", self.getMultiplier(), add="1")
                self.openPlotViewer(plot)
            if self.ui.heat.isChecked() == True:
                plot = Controller.plotCustom(uw, ud, None, None, None, self.getUserContour(), "2", self.getMultiplier(), add="2")
                self.openPlotViewer(plot)
            if self.ui.three_in_one.isChecked() == True:
                plot = Controller.plot3OrigData(uw, ud, None, None, db, wb, self.getUserContour(), self.getMultiplier(), self.getSASOptMethod(), self.getSASIvpMethod())
                self.openPlotViewer(plot)
            if self.ui.threeD_contour.isChecked() == True:
                plot = Controller.plot3DOrigData(None, None, db, wb, self.getMultiplier(), self.getSASOptMethod(), self.getSASIvpMethod())
                self.openPlotViewer(plot)
        
        if self.ui.fitted.isChecked() == True:
            tau_fit, spec, res, D_fit, self.fit_report = Controller.calcDAS(self.getTaus(), db, wb, self.getDASOptMethod())
            
            if self.ui.A_wave.isChecked() == True:
                plot = Controller.plotCustom(uw, ud, None, None, 0, self.getUserContour(), "3", self.getMultiplier(), add="3")
                self.openPlotViewer(plot)
            if self.ui.del_A.isChecked() == True:
                plot = Controller.plotCustom(uw, ud, None, None, 0, self.getUserContour(), "1", self.getMultiplier(), add="1")
                self.openPlotViewer(plot)
            if self.ui.heat.isChecked() == True:
                plot = Controller.plotCustom(uw, ud, None, None, 0, self.getUserContour(), "2", self.getMultiplier(), add="2")
                self.openPlotViewer(plot)
            if self.ui.three_in_one.isChecked() == True:
                plot = Controller.plot3FittedData(uw, ud, None, None, 0, self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.threeD_contour.isChecked() == True:
                plot = Controller.plot3DFittedData(None, None, 0, self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.residuals.isChecked() == True:
                plot = Controller.plot2Dresiduals(None,None,0,self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.reconstructed.isChecked() == True:
                plot = Controller.plotDAS(0, tau_fit, self.getMultiplier())
                self.openPlotViewer(plot)
                
    def plottingSAS(self,Controller,ud,uw,db,wb,model,K):
        """
        Creates the plots selected by the user and opens them in popup windows
        for inspection/modification.
        
        Parameters
        ----------
        Controller : Controller
            DESCRIPTION.
        ud : list
            The specific delay values the user wants to examine.
        uw : list
            The specific wavelenght values the user wants to examine..
        db : list
            The lower and upper bound for the delay data.
        wb : list
            The lower and upper bound for the wavelength data.
        model : int/string
            Describes the desired model. 0 for the GLA. For GTA it can be a
            number 1-10 or "custom" for a custom model.
        K : np.ndarray
            The reaction rate matrix.
        Returns
        -------
        None.

        """
        
        if self.ui.raw.isChecked() == True:
            self.Controller.createOrigData(db,wb, self.getSASOptMethod(), self.getSASIvpMethod())
            if self.ui.A_wave.isChecked() == True:
                plot = self.Controller.plotCustom(uw, ud, None, None, None, self.getUserContour(), "3", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.del_A.isChecked() == True:
                plot = self.Controller.plotCustom(uw, ud, None, None, None, self.getUserContour(), "1", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.heat.isChecked() == True:
                plot = self.Controller.plotCustom(uw, ud, None, None, None, self.getUserContour(), "2", self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.three_in_one.isChecked() == True:
                plot = self.Controller.plot3OrigData(uw, ud, None, None, db, wb, self.getUserContour(), self.getMultiplier(), self.getSASOptMethod(), self.getSASIvpMethod())
                self.openPlotViewer(plot)
            if self.ui.threeD_contour.isChecked() == True:
                plot = Controller.plot3DOrigData(None, None, db, wb, self.getMultiplier(), self.getSASOptMethod(), self.getSASIvpMethod())
                self.openPlotViewer(plot)
                
        if self.ui.fitted.isChecked() == True:
            K =  np.array(K)
            tau_fit, spec, res, D_fit, self.fit_report = self.Controller.calcSAS(K, self.getUserConc(), db, wb,
                    model,self.getK_lin_bounds()[0], self.getK_lin_bounds()[1],self.getSASOptMethod(), self.getSASIvpMethod()) 
            if self.ui.A_wave.isChecked() == True:
                plot = self.Controller.plotCustom(uw, ud, None, None, model, self.getUserContour(), self.getMultiplier(), "3")
                self.openPlotViewer(plot)
            if self.ui.del_A.isChecked() == True:
                plot = self.Controller.plotCustom(uw, ud, None, None, model, self.getUserContour(), self.getMultiplier(), "1")
                self.openPlotViewer(plot)
            if self.ui.heat.isChecked() == True:
                plot = self.Controller.plotCustom(uw, ud, None, None, model, self.getUserContour(), self.getMultiplier(), "2")
                self.openPlotViewer(plot)
            if self.ui.three_in_one.isChecked() == True:
                plot = self.Controller.plot3FittedData(uw, ud, None, None, model, self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.threeD_contour.isChecked() == True:
                plot = Controller.plot3DFittedData(None, None, model, self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.residuals.isChecked() == True:
                plot = self.Controller.plot2Dresiduals(None, None, model, self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.reconstructed.isChecked() == True:
                plot = Controller.plotDAS(model, tau_fit, self.getMultiplier())
                self.openPlotViewer(plot)
            if self.ui.kinetics.isChecked() == True:
                plot = Controller.plotKinetics(model)
                self.openPlotViewer(plot)
                
    ''' 7.1 Usability of widgets ''' 
    
    def disableFitted(self):
        """
        Makes sure fitting dependent plots can't be selected if only raw data
        is selected.

        Returns
        -------
        None.

        """
        if self.ui.fitted.isChecked() == True:
            if self.ui.DAS_radio.isChecked() == True:
                self.ui.kinetics.setChecked(False)
                self.ui.kinetics.setEnabled(False)
                self.ui.reconstructed.setEnabled(True)
                self.ui.residuals.setEnabled(True)
            else:
                self.ui.kinetics.setEnabled(True)
                self.ui.reconstructed.setEnabled(True)
                self.ui.residuals.setEnabled(True)
        else:
            self.ui.kinetics.setChecked(False)
            self.ui.kinetics.setEnabled(False)
            self.ui.reconstructed.setChecked(False)
            self.ui.reconstructed.setEnabled(False)
            self.ui.residuals.setChecked(False)
            self.ui.residuals.setEnabled(False)
            
    ''' 8.0 Data collection '''
    
    ''' 8.1 Necessary files '''

    def selectFolderPath(self):
        """
        Opens directory selection dialog, checks if given directory contains
        delays,lambdas and spectra data and if so creates a Controller object.
        If pickled data from previous evaluations is available, the user input
        will be restored.

        Returns
        -------
        None.

        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.ui.folderpath.setText(directory)
        if self.ui.folderpath.text() != "":
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
        
    def getFolderPath(self):
        """
        Checks if a folder directory was selected and returns it.

        Returns
        -------
        self.ui.folderpath.text() : string
            The folder directory.

        """
        if self.ui.folderpath == "":
            self.openFailSafe("Please select a folder directory.")
        else:
            return self.ui.folderpath.text()
    
    ''' 8.2 Input for delays and wavelengths '''
    
    def getUserDelay(self):
        """
        Reads the delays input by the user if empty, returns preset values.

        Returns
        -------
        user_delays: list
            A list containing the delays input by the user.

        """
        if self.ui.delaysinput.text() == "":
            user_delays = []
        else: 
            user_delays = self.ui.delaysinput.text().split(',')
            for i in range(len(user_delays)):
                if user_delays[i] != "":
                    user_delays[i] = float(user_delays[i])
        return user_delays
    
    def getUserWavelength(self):
        """
        Reads the lambdas input by the user if empty, returns preset values.

        Returns
        -------
        user_lambdas: list
            A list containing the lambdas input by the user.

        """
        if self.ui.wavelengthsinput.text() == "":
            user_lambdas = []
        else:
            user_lambdas = self.ui.wavelengthsinput.text().split(',')
            for i in range(len(user_lambdas)):
                if user_lambdas[i] != "":
                    user_lambdas[i] = float(user_lambdas[i])
        return user_lambdas
        
    def getUserDelayBoundsLow(self):
        """
        Reads the lower delay bound input by the user if empty returns preset
        a value.

        Returns
        -------
        delay_lb: float
            The lower delay bound input by the user.

        """
        if self.ui.lowdelay.text() == "":
            delay_lb = 0
        else:
            lb_text=self.ui.lowdelay.text()
            delay_lb = float(lb_text)
        return delay_lb
        
    def getUserDelayBoundsUp(self):
        """
        Reads the upper delay bound input by the user if empty returns preset
        a value.

        Returns
        -------
        delay_ub: float
            The upper delay bound input by the user.

        """
        if self.ui.updelay.text() == "":
            delay_ub = 4000
        else:
            ub_text=self.ui.updelay.text()
            delay_ub = float(ub_text)
        return delay_ub

    def getUserWavelengthBoundsLow(self):
        """
        Reads the lower lambda bound input by the user if empty returns preset
        a value.

        Returns
        -------
        lambda_lb: float
            The lower lambda bound input by the user.

        """
        if self.ui.lowwave.text() == "":
            lambda_lb = 350
        else:
            lb_text=self.ui.lowwave.text()
            lambda_lb = float(lb_text)
        return lambda_lb
    
    def getUserWavelengthBoundsUp(self):
        """
        Reads the upper lambda bound input by the user if empty returns preset
        a value.

        Returns
        -------
        lambda_ub: float
            The upper lambda bound input by the user.

        """
        if self.ui.lowwave.text() == "":
            lambda_ub = 800
        else:
            ub_text=self.ui.upwave.text()
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
        if self.ui.contour.value() == 0:
            cont = 20
        else:
            cont = self.ui.contour.value()
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
        if self.ui.multiplier.text() == "":
            mul = 1
        else:
            mul = int(self.ui.multiplier.text())
        return mul
    
    ''' 8.3 DAS details '''    
    
    def getTaus(self):
        """
        Checks which lifetime guesses are given (fixed, variable or both) and 
        reads them.

        Returns
        -------
        list
            The lifetimes input by the user.

        """
        tau_var = self.ui.tau_var.text().split(',')
        tau_fix = self.ui.tau_fix.text().split(',')
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
        
    def getDASOptMethod(self):
        """
        Reads the algorithm choice for the minimization of the ChiSquare 
        function by the user.

        Returns
        -------
        string
            The name of the minimization algorithm.

        """
        return self.ui.DAS_optmethod.currentText()
        
    ''' 8.4 SAS details '''
        
    def getK_lin(self):
        """
        Reads the lifetimes input by the user, if a linear model is 
        selected.

        Returns
        -------
        ks_list : list
            The lifetimes input by the user.

        """
        if self.ui.ks_forwards_lin.text() == "":
            ks = []
        else:
            ks = self.ui.ks_forwards_lin.text().split(',')
            for i in range(len(ks)):
                if ks[i] != "":
                    ks[i] = float(ks[i])
        return ks
    
    def getK_lin_bounds(self):
        """
        Reads the bounds for the lifetimes during the calculation.

        Returns
        -------
        list
            A list containing the lower bounds and upper bounds list.

        """
        kslb = self.ui.ks_forwards_lin_low.text().split(',')
        ksub = self.ui.ks_forwards_lin_high.text().split(',')
        for i in range(len(kslb)):
            if kslb[i] != "":
                kslb[i] = float(kslb[i])
        for i in range(len(ksub)):
            if ksub[i] != "":
                ksub[i] = float(ksub[i])
        if any(isinstance(obj,float) for obj in kslb):
            kslb = [None if item == '' else item for item in kslb]
        else:
            kslb = []
            
        if any(isinstance(obj,float) for obj in ksub):
            ksub = [None if item == '' else item for item in ksub]
        else:
            ksub = []
        return [kslb,ksub]

    def getK_eq(self):
        """
        Reads the lifetimes input by the user if a equilibrium model is
        selected.

        Returns
        -------
          list
            A list containing a list of the lifetimes for the forwards 
            reactions and then the backwards reactions.
            
        """
        ksf = self.ui.ks_forwards_eq.text().split(',')
        ksb = self.ui.ks_backwards_eq.text().split(',')
        for i in range(len(ksf)):
            if ksf[i] != "":
                ksf[i] = float(ksf[i])
        for i in range(len(ksb)):
            if ksb[i] != "":
                ksb[i] = float(ksb[i])
        if any(isinstance(obj,float) for obj in ksf):
            ksf = ksf
        else:
            ksf = []
        if any(isinstance(obj,float) for obj in ksb):
            ksb = ksb
        else:
            ksb = []
        return [ksf,ksb]

    def getK_eq_bounds(self):
        """
        Reads lower/upper bounds for the forward reaction and backward
        reactions input by the user and returns them.

        Returns
        -------
        list
            A list containing all lists for all bounds for the equilibrium
            model.
        """
        ksflb = self.ui.ks_forwards_eq_low.text().split(',')
        ksfub = self.ui.ks_forwards_eq_high.text().split(',')
        ksblb = self.ui.ks_backwards_eq_low.text().split(',')
        ksbub = self.ui.ks_backwards_eq_high.text().split(',')
        for i in range(len(ksflb)):
            if ksflb[i] != "":
                ksflb[i] = float(ksflb[i])
        for i in range(len(ksfub)):
            if ksfub[i] != "":
                ksfub[i] = float(ksfub[i])
        for i in range(len(ksblb)):
            if ksblb[i] != "":
                ksblb[i] = float(ksblb[i])        
        for i in range(len(ksbub)):
            if ksbub[i] != "":
                ksbub[i] = float(ksbub[i])        
        if any(isinstance(obj,float) for obj in ksflb):
            ksflb = [None if item == '' else item for item in ksflb]
        else:
            ksflb = []
        if any(isinstance(obj,float) for obj in ksfub):
            ksfub = [None if item == '' else item for item in ksfub]
        else:
            ksfub = []
        if any(isinstance(obj,float) for obj in ksblb):
            ksblb = [None if item == '' else item for item in ksblb]
        else:
            ksblb = []
        if any(isinstance(obj,float) for obj in ksbub):
            ksbub = [None if item == '' else item for item in ksbub]
        else:
            ksbub = []
        return [ksflb,ksfub,ksblb,ksbub]

    def getUserMatrix(self):
        """
        Fetches the custom matrix input by the user and saved by the close 
        popup function.

        Returns
        -------
        np.ndarray
            The custom matrix input by the user.

        """
        return self.cm
        
    def getUserConc(self):
        """
        Reads the concentration vector input by the user and returns it.

        Returns
        -------
        C_0 : list
            The concentration vector set by the user.

        """
        C_0 = self.ui.conc.text().split(',')
        for i in range(len(C_0)):
            if C_0[i] != "":
                C_0[i] = float(C_0[i])
        if any(isinstance(obj,float) for obj in C_0):
            C_0 = C_0
        else:
            C_0 = []
        return C_0
    
    def getModel(self):
        """
        Returns the current selected kinetic model.
        Returns
        -------
        int
            The integer corresponding to a kinetic model.

        """
        return self.ui.SAS_modelSelect.currentIndex()
    
    def getSASOptMethod(self):
        """
        Returns the current selected optimization algorithm.

        Returns
        -------
        string
            The name of the selected optimization algorithm.

        """
        return self.ui.SAS_optmethod.currentText()
    
    def getSASIvpMethod(self):
        """
        Returns the current selected ivp solver algorithm.

        Returns
        -------
        string
            The name of the selected ivp solver algorithm.

        """
        return self.ui.SAS_ivpmethod.currentText()
    
        
        ''' 8.5 SAS Popup '''

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
        self.cm = popup.CM 
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
    
    ''' 8.6 Other PopUps '''
    
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

    ''' 9.0 Cosmetics '''
        
    def changeTheme(self):
        """
        Changes the colour theme of the program to either light or dark.

        Returns
        -------
        None.

        """
        if self.ui.Theme.isChecked() == True:
            lightmode = QPalette()
            lightmode.setColor(lightmode.Window, QColor("white"))
            lightmode.setColor(lightmode.WindowText, Qt.black)
            lightmode.setColor(lightmode.Base, QColor(230,230,230))
            lightmode.setColor(lightmode.AlternateBase, QColor("white"))
            lightmode.setColor(lightmode.ToolTipBase, Qt.white)
            lightmode.setColor(lightmode.ToolTipText, Qt.black)
            lightmode.setColor(lightmode.Text, Qt.black)
            lightmode.setColor(lightmode.Button, QColor(230, 230, 230))
            lightmode.setColor(lightmode.ButtonText, Qt.black)
            lightmode.setColor(lightmode.BrightText, Qt.green)
            lightmode.setColor(lightmode.Link, QColor(42, 130, 218))
            lightmode.setColor(lightmode.Highlight, QColor(42, 130, 218))
            lightmode.setColor(lightmode.HighlightedText, Qt.white)
            app.setPalette(lightmode)
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
            app.setPalette(darkmode)
            
    ''' 10.0 Pickle '''
    
    def savePickle(self):
        """
        Saves the user inputs to reload them for future evaluations.

        Returns
        -------
        None.

        """
        if self.DAS_radio.isChecked():
            model = 0
        elif self.ui.SAS_modelSelect.currentText() == "Custom Model":
            model = "custom"
        else:
            model = self.getModel()+1
            
        C_0 = self.getUserConc()
        ud = sorted(self.getUserDelay())
        uw = sorted(self.getUserWavelength())
        db_low = self.getUserDelayBoundsLow()
        db_high = self.getUserDelayBoundsUp()
        wb_low = self.getUserWavelengthBoundsLow()
        wb_high = self.getUserWavelengthBoundsUp()
        cont = self.getUserContour()
        kseqflb = self.getK_eq_bounds()[0]
        kseqfub = self.getK_eq_bounds()[1]
        kseqblb = self.getK_eq_bounds()[2]
        kseqbub = self.getK_eq_bounds()[3]
        ksflb = self.getK_lin_bounds()[0]
        ksfub = self.getK_lin_bounds()[1]
        
        if model == 0:
            tau_fix = self.getTaus()[0]
            tau_var = self.getTaus()[1]
            self.Controller.pickleData(model=model, d_limits_low=db_low, 
                                       d_limits_high=db_high, l_limits_low=wb_low,
                                       l_limits_high=wb_high, cont=cont, time=ud, 
                                       wave=uw, tau_fix=tau_fix, tau_var=tau_var)
        elif self.ui.SAS_modelSelect.currentText() == "Custom Model":
             tau = self.getUserMatrix()
             self.Controller.pickleData(model=model,C_0=C_0, db_low=db_low, 
                                        db_high=db_high, wb_low=wb_low,
                                        wb_high=wb_high, cont=cont, time=ud, wave=uw, das_tau=tau)
        elif self.ui.SAS_modelSelect.currentIndex() <=1 or self.ui.SAS_modelSelect.currentIndex()>3:
            tau = np.array(self.getK_lin())
            self.Controller.pickleData(model=model,C_0=C_0, d_limits_low=db_low, 
                                       d_limits_high=db_high, l_limits_low=wb_low,
                                       l_limits_high=wb_high, cont=cont, time=ud, wave=uw, 
                                       ksf=list(tau), ksflb=ksflb, ksfub=ksfub)
        else:
            ksfeq = self.getK_eq()[0]
            ksbeq = self.getK_eq()[1]
            self.Controller.pickleData(model=model, C_0=C_0, d_limits_low=db_low, 
                                       d_limits_high=db_high, l_limits_low=wb_low,
                                       l_limits_high=wb_high,
                                       cont=cont, time=ud, wave=uw, 
                                       ksfeq=ksfeq, ksbeq=ksbeq, 
                                       kseqflb=kseqflb, kseqfub=kseqfub, 
                                       kseqblb=kseqblb, kseqbub=kseqbub)
            
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
        for key in self.shelf:
            val = str(self.shelf[key])
            val = val.replace("[","")
            val = val.replace("]","")
            val = val.replace("None","")
            val = val.replace(" ","")
            if key == "time":
                self.ui.delaysinput.setText(val)
            if key == "wave":
                self.ui.wavelengthsinput.setText(val)
            if key == "ksfeq":
                self.ui.ks_forwards_eq.setText(val)
            if key == "ksbeq":
                self.ui.ks_backwards_eq.setText(val)
            if key == "kseqflb":
                self.ui.ks_forwards_eq_low.setText(val)
            if key == "kseqfub":
                self.ui.ks_forwards_eq_high.setText(val)
            if key == "kseqblb":
                self.ui.ks_backwards_eq_low.setText(val)
            if key == "kseqbub":
                self.ui.ks_backwards_eq_high.setText(val)
            if key == "ksf":
                self.ui.ks_forwards_lin.setText(val)
            if key == "ksflb":
                self.ui.ks_forwards_lin_low.setText(val)
            if key == "ksfub":
                self.ui.ks_forwards_lin_high.setText(val)
            if key == "C_0":
                self.ui.conc.setText(val)
            if key == "cont":
                self.ui.contour.setValue(int(val))
            if key == "model":
                if val == "0":
                    self.ui.DAS_radio.setChecked(True)
                elif val == "custom":
                    self.ui.SAS_radio.setChecked(True)
                    self.ui.SAS_modelSelect.setCurrentIndex(10)
                else:
                    self.ui.SAS_radio.setChecked(True)
                    self.ui.SAS_modelSelect.setCurrentIndex(int(val)-1)
            if key == "db_low":
                self.ui.lowdelay.setText(val)
            if key == "db_high":
                self.ui.highdelay.setText(val)
            if key == "wb_low":
                self.ui.lowwave.setText(val)
            if key == "wb_high":
                self.ui.highwave.setText(val)
            if key == "tau_fix":
                self.ui.tau_fix.setText(val)
            if key == "tau_var":
                self.ui.tau_var.setText(val)
            
    def clearPickle(self):
        """
        Clears the set reloaded user inputs.

        Returns
        -------
        None.

        """
        for lineedit in self.findChildren(QLineEdit):
            if lineedit != self.ui.folderpath:
                lineedit.clear()
        for spinbox in self.findChildren(QSpinBox):
            spinbox.setValue(0)
        for combobox in self.findChildren(QComboBox):
            combobox.setCurrentIndex(0)
        if hasattr(self, 'cm') == True:
            self.cm = None
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
