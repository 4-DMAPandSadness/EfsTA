import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import Controller as Cont
import numpy as np
import os as os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    
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
        self.setWindowTitle("EfsTA")
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
            if (self.ui.del_wave.isChecked() == False and
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
        ud = self.getUserDelay()
        ud.sort()
        uw = self.getUserWavelength()
        uw.sort()
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
                self.plottingSAS(self.Controller, ud, uw, db, wb, model,np.array(self.getK_eq()))
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
            if self.ui.del_wave.isChecked() == True:
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
            
            if self.ui.del_wave.isChecked() == True:
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
                plot = Controller.plot1Dresiduals(0, self.getMultiplier())
                plot2 = Controller.plot2Dresiduals(None,None,0,self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
                self.openPlotViewer(plot2)
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
            if self.ui.del_wave.isChecked() == True:
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
            if self.ui.del_wave.isChecked() == True:
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
                plot = self.Controller.plot1Dresiduals(model, self.getMultiplier())
                plot2 = self.Controller.plot2Dresiduals(None, None, model, self.getUserContour(), self.getMultiplier())
                self.openPlotViewer(plot)
                self.openPlotViewer(plot2)
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
            user_delays = [4, 67, 130]
        else:
            delaysinput = self.ui.delaysinput.text()
            string_split = delaysinput.split(',')
            map_object = map(float, string_split)
            user_delays = list(map_object)
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
            user_lambdas = [360, 560, 700]
        else:
            wavelengthsinput = self.ui.wavelengthsinput.text()
            string_split = wavelengthsinput.split(',')
            map_object = map(float, string_split)
            user_lambdas = list(map_object)
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
            delay_lb = 0.3
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
            delay_ub = 3000
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
            lambda_lb = 355
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
        if self.ui.tau_fix.text() == "" and self.ui.tau_var.text() != "":
            taus_var = self.ui.tau_var.text()
            string_split = taus_var.split(',')
            map_object = map(float, string_split)
            taus_var_list = list(map_object)
            return [[], taus_var_list]
        elif self.ui.tau_fix.text() != "" and self.ui.tau_var.text() != "":
            taus_var1 = self.ui.tau_var.text()
            string_split = taus_var1.split(',')
            map_object = map(float, string_split)
            taus_var1_list = list(map_object)     
            taus_fix = self.ui.tau_fix.text()
            string_split = taus_fix.split(',')
            map_object = map(float, string_split)
            taus_fix_list = list(map_object)
            return [taus_fix_list, taus_var1_list]
        elif self.ui.tau_fix.text() != "" and self.ui.tau_var.text() == "":
            taus_fix = self.ui.tau_fix.text()
            string_split = taus_fix.split(',')
            map_object = map(float, string_split)
            taus_fix_list = list(map_object)
            return [taus_fix_list, []]
        
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
            ks_list = None
        else:
            ks = self.ui.ks_forwards_lin.text()
            string_split = ks.split(',')
            map_object = map(float, string_split)
            ks_list = list(map_object)
        return ks_list
    
    def getK_lin_bounds(self):
        """
        Reads the bounds for the lifetimes during the calculation.

        Returns
        -------
        list
            A list containing the lower bounds and upper bounds list.

        """
        if self.ui.ks_forwards_lin_low.text() == "":
            kslb_list = None
        else:
            kslb = self.ui.ks_forwards_lin_low.text()
            string_split = kslb.split(',')
            map_object = map(float, string_split)
            kslb_list = list(map_object)
        if self.ui.ks_forwards_lin_high.text() == "":
            ksub_list = None
        else:
            ksub = self.ui.ks_forwards_lin_high.text()
            string_split = ksub.split(',')
            map_object = map(float, string_split)
            ksub_list = list(map_object)
        return [kslb_list,ksub_list]
    
    def getK_eq(self):
        """
        Reads the lifetimes input by the user if a equilibrium model is
        selected.

        Returns
        -------
        ks_list : list
            A list containing the lifetimes for the forwards reactions and then
            the backwards reactions.

        """
        ks1 = self.ui.ks_forwards_eq.text()
        string_split = ks1.split(',')
        map_object = map(float, string_split)
        ks_list = list(map_object)
        ks2 = self.ui.ks_backwards_eq.text()
        string_split = ks2.split(',')
        map_object = map(float, string_split)
        ks2_list = list(map_object)
        for i in range(len(ks2_list)):
             ks_list.append(ks2_list[i])
        return ks_list

    def getK_eq_pickle(self):
        """
        Reads the lifetimes for the equibrium reactions input by the user
        to pickle them.

        Returns
        -------
        list
            A list containing the list for the lifetimes for the forwards 
            reactions and then a list for the backwards reactions.

        """
        if self.ui.ks_forwards_eq.text() == "":
            ks1_list = None
        else:
            ks1 = self.ui.ks_forwards_eq.text()
            string_split = ks1.split(',')
            map_object = map(float, string_split)
            ks1_list = list(map_object)
        if self.ui.ks_backwards_eq.text() == "":
            ks2_list = None
        else:
            ks2 = self.ui.ks_backwards_eq.text()
            string_split = ks2.split(',')
            map_object = map(float, string_split)
            ks2_list = list(map_object)
        return [ks1_list,ks2_list]

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
        if self.ui.ks_forwards_eq_low.text() == "":
            ksflb_list = None
        else:
            ksflb = self.ui.ks_forwards_eq_low.text()
            string_split = ksflb.split(',')
            map_object = map(float, string_split)
            ksflb_list = list(map_object)
        if self.ui.ks_forwards_eq_high.text() == "":
            ksfub_list = None
        else:
            ksfub = self.ui.ks_forwards_eq_high.text()
            string_split = ksfub.split(',')
            map_object = map(float, string_split)
            ksfub_list = list(map_object)
        if self.ui.ks_backwards_eq_low.text() == "":
            ksblb_list = None
        else:
            ksblb = self.ui.ks_backwards_eq_low.text()
            string_split = ksblb.split(',')
            map_object = map(float, string_split)
            ksblb_list = list(map_object)
        if self.ui.ks_backwards_eq_high.text() == "":
            ksbub_list = None
        else:
            ksbub = self.ui.ks_backwards_eq_high.text()
            string_split = ksbub.split(',')
            map_object = map(float, string_split)
            ksbub_list = list(map_object)
        return [ksflb_list,ksfub_list,ksblb_list,ksbub_list]

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
        if self.ui.conc.text() == "":
            return []
        else:
            ctemp = self.ui.conc.text()
            string_split = ctemp.split(',')
            map_object = map(float, string_split)
            C_0 = list(map_object)
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
            
        ud = self.getUserDelay()
        ud.sort()
        uw = self.getUserWavelength()
        uw.sort()
        db = [self.getUserDelayBoundsLow(), self.getUserDelayBoundsUp()]
        wb = [self.getUserWavelengthBoundsLow(), self.getUserWavelengthBoundsUp()]
        cont = self.getUserContour()
        kseqflb = self.getK_eq_bounds()[0]
        kseqfub = self.getK_eq_bounds()[1]
        kseqblb = self.getK_eq_bounds()[2]
        kseqbub = self.getK_eq_bounds()[3]
        ksflb = self.getK_lin_bounds()[0]
        ksfub = self.getK_lin_bounds()[1]
        if model == 0:
            tau = self.getTaus()
            self.Controller.pickleData(model=model, d_limits=db, l_limits=wb, cont=cont, time=ud, wave=uw, das_tau=tau)
        elif self.ui.SAS_modelSelect.currentText() == "Custom Model":
             tau = self.getUserMatrix()
             self.Controller.pickleData(model=model, d_limits=db, l_limits=wb, cont=cont, time=ud, wave=uw, das_tau=tau)
        elif self.ui.SAS_modelSelect.currentIndex() <=1 or self.ui.SAS_modelSelect.currentIndex()>3:
            tau = np.array(self.getK_lin())
            self.Controller.pickleData(model=model, d_limits=db, l_limits=wb, cont=cont, time=ud, wave=uw, ksfl=list(tau), ksflb=ksflb, ksfub=ksfub)
        else:
            ksfeq = self.getK_eq_pickle()[0]
            ksbeq = self.getK_eq_pickle()[1]
            self.Controller.pickleData(model=model, d_limits=db, l_limits=wb, cont=cont, time=ud, wave=uw, ksfeq=ksfeq, ksbeq=ksbeq, kseqflb=kseqflb, kseqfub=kseqfub, kseqblb=kseqblb, kseqbub=kseqbub)
            
    def getPickle(self, *keys):
        """
        Reloads the saved user inputs.

        Parameters
        ----------
        *keys : TYPE
            DESCRIPTION.

        Returns
        -------
        values : list
            A list containing all saved values.

        """
        if hasattr(self, 'Controller') == False:
            self.Controller = Cont.Controller(self.getFolderPath())
        values = []
        shelf = self.Controller.getPickle()
        for key in keys:
            try:
                values.append(shelf[key])
            except:
                values.append(None)       
        return values
    
    def setPickle(self):
        """
        Sets the reloaded user inputs in the GUI.

        Returns
        -------
        None.

        """
        if self.getPickle("time")[0] != None:
            delay = str(self.getPickle("time")[0])
            delay = delay.replace("[","")
            delay = delay.replace("]","")
            self.ui.delaysinput.setText(delay)            
        if self.getPickle("wave")[0] != None:
            wave = str(self.getPickle("wave")[0])
            wave = wave.replace("[","")
            wave = wave.replace("]","")
            self.ui.wavelengthsinput.setText(wave)            
        if self.getPickle("d_limits")[0] != None:
            lowd = str(self.getPickle("d_limits")[0][0])
            lowd = lowd.replace("[","")
            lowd = lowd.replace("]","")
            self.ui.lowdelay.setText(lowd)
        if self.getPickle("d_limits")[0] != None:
            upd = str(self.getPickle("d_limits")[0][1])
            upd = upd.replace("[","")
            upd = upd.replace("]","")
            self.ui.updelay.setText(upd)
        if self.getPickle("l_limits")[0] != None:
            loww = str(self.getPickle("l_limits")[0][0])
            loww = loww.replace("[","")
            loww = loww.replace("]","")
            self.ui.lowwave.setText(loww)
        if self.getPickle("l_limits")[0] != None:
            upw = str(self.getPickle("l_limits")[0][1])
            upw = upw.replace("[","")
            upw = upw.replace("]","")
            self.ui.upwave.setText(upw)
        if self.getPickle("das_tau")[0] != None:
            tau_fix = str(self.getPickle("das_tau")[0][0])
            tau_fix = tau_fix.replace("[","")
            tau_fix = tau_fix.replace("]","")
            self.ui.tau_fix.setText(tau_fix)
        if self.getPickle("das_tau")[0] != None:
            tau_var = str(self.getPickle("das_tau")[0][1])
            tau_var = tau_var.replace("[","")
            tau_var = tau_var.replace("]","")
            self.ui.tau_var.setText(tau_var)
        if self.getPickle("ksfeq")[0] != None:
            ksfeq = str(self.getPickle("ksfeq")[0])
            ksfeq = ksfeq.replace("[","")
            ksfeq = ksfeq.replace("]","")
            self.ui.ks_forwards_eq.setText(ksfeq)
        if self.getPickle("ksbeq")[0] != None:
            ksbeq = str(self.getPickle("ksbeq")[0])
            ksbeq = ksbeq.replace("[","")
            ksbeq = ksbeq.replace("]","")
            self.ui.ks_backwards_eq.setText(ksbeq)    
        if self.getPickle("kseqflb")[0] != None:
            kseqflb = str(self.getPickle("kseqflb")[0])
            kseqflb = kseqflb.replace("[","")
            kseqflb = kseqflb.replace("]","")
            self.ui.ks_backwards_eq_low.setText(kseqflb)
        if self.getPickle("kseqfub")[0] != None:
            kseqfub = str(self.getPickle("kseqfub")[0])
            kseqfub = kseqfub.replace("[","")
            kseqfub = kseqfub.replace("]","")
            self.ui.ks_backwards_eq_high.setText(kseqfub)
        if self.getPickle("kseqblb")[0] != None:
            kseqblb = str(self.getPickle("kseqblb")[0])
            kseqblb = kseqblb.replace("[","")
            kseqblb = kseqblb.replace("]","")
            self.ui.ks_backwards_eq_low.setText(kseqblb)
        if self.getPickle("kseqbub")[0] != None:
            kseqbub = str(self.getPickle("kseqbub")[0])
            kseqbub = kseqbub.replace("[","")
            kseqbub = kseqbub.replace("]","")
            self.ui.ks_backwards_eq_high.setText(kseqbub)            
        if self.getPickle("ksfl")[0] != None:
            ksfl = str(self.getPickle("ksfl")[0])
            ksfl = ksfl.replace("[","")
            ksfl = ksfl.replace("]","")
            self.ui.ks_forwards_lin.setText(ksfl)   
        if self.getPickle("ksflb")[0] != None:
            ksflb = str(self.getPickle("ksflb")[0])
            ksflb = ksflb.replace("[","")
            ksflb = ksflb.replace("]","")
            self.ui.ks_forwards_lin_low.setText(ksflb)
        if self.getPickle("ksfub")[0] != None:
            ksfub = str(self.getPickle("ksfub")[0])
            ksfub = ksfub.replace("[","")
            ksfub = ksfub.replace("]","")
            self.ui.ks_forwards_lin_high.setText(ksfub)

        if self.getPickle("C_0")[0] != None:
            C_0 = str(self.getPickle("C_0")[0])
            C_0 = C_0.replace("[","")
            C_0 = C_0.replace("]","")
            self.ui.conc.setText(C_0)
                
        if self.getPickle("cont")[0] != None:
            self.ui.contour.setValue(self.getPickle("cont")[0])
            
    def clearPickle(self):
        """
        Clears the set reloaded user inputs.

        Returns
        -------
        None.

        """
        self.ui.delaysinput.setText("")
        self.ui.wavelengthsinput.setText("")
        self.ui.lowdelay.setText("")
        self.ui.updelay.setText("")
        self.ui.lowwave.setText("")
        self.ui.upwave.setText("")
        self.ui.contour.setValue(0)
        self.ui.multiplier.setText("")
        self.ui.tau_var.setText("")
        self.ui.tau_fix.setText("")
        self.ui.ks_forwards_eq.setText("")
        self.ui.ks_forwards_eq_high.setText("")
        self.ui.ks_forwards_eq_low.setText("")
        self.ui.ks_backwards_eq.setText("")
        self.ui.ks_backwards_eq_high.setText("")
        self.ui.ks_backwards_eq_low.setText("")
        self.ui.ks_forwards_lin.setText("")
        self.ui.ks_forwards_lin_high.setText("")
        self.ui.ks_forwards_lin_low.setText("")
        self.ui.conc.setText("")
        if hasattr(self, 'cm') == True:
            self.cm = None
        self.ui.rows_and_columns.setValue(0)
        self.ui.SAS_modelSelect.setCurrentIndex(0)
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
