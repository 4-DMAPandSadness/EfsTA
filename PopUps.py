from PyQt5 import QtWidgets as QW
from PyQt5.QtCore import Qt
import numpy as np

class TableWindow(QW.QWidget):
    def __init__(self,size):
        super(QW.QWidget,self).__init__()
        self.size = size
        
        self.initUI(size)
        
        
    def initUI(self, size):
        self.setWindowTitle('Custom Kinetic Matrix Input')

        self.matrix_Table = QW.QTableWidget(self)
        self.matrix_Table.setRowCount(size)
        self.matrix_Table.setColumnCount(size)

        self.matrix_Table.horizontalHeader().setDefaultSectionSize(50)

        self.matrix_Table.verticalHeader().setDefaultSectionSize(50)

        self.save = QW.QPushButton('Save', self)
        self.save.clicked.connect(self.readTable)

        self.layout = QW.QGridLayout()
        self.layout.addWidget(self.matrix_Table, 0, 0, 1, 2)
        self.layout.addWidget(self.save, 1, 0, 1, 2)

        self.setLayout(self.layout)

        self.resize(self.size*50 + 55, self.size * 50 + 80)
        
        self.setWindowModality(Qt.ApplicationModal)

    def readTable(self):
        """
        Reads the kinetic matrix input by the user and saves the matrix in a
        numpy array as an attribute of the TableWindow object.

        Returns
        -------
        None.

        """
        K = np.zeros((self.size, self.size))
        for i in range(self.size):
            for j in range(self.size):
                if self.matrix_Table.item(i,j) == None:
                    K[i][j] = 0
                else:
                    K[i][j] = float(self.matrix_Table.item(i,j).text())
        self.custom_Matrix = K

class TextWindow(QW.QWidget):
    
    def __init__(self, model, Controller, Message):
        super(QW.QWidget,self).__init__()
        self.model = model
        self.Controller = Controller
        self.Message = Message
        self.initUI() 
        
    def initUI(self):
        
        self.text_browser = QW.QTextBrowser()
        

        self.layout = QW.QGridLayout()
        self.layout.addWidget(self.text_browser, 0, 0, 1, 2)

        self.setLayout(self.layout)
        
        if self.Message == None:
            self.displayResults()
        else:
            self.displayError()

        self.resize(self.text_browser.size())
        
    def displayResults(self):
        """
        Fills the QTextEdit object with the corresponding data.

        Parameters
        ----------
        model : int/string
            Describes the desired model. 0 for the GLA. For GTA it can be a
            number 1-8, "custom model" or "custom matrix".
        Controller : Controller
            An Object of the Controller class.
        Returns
        -------
        None.

        """
        self.text_browser.clear()
        text = self.Controller.getResults(self.model)
        self.text_browser.append(text)
        
    def displayError(self):
        """
        Fills the QTextEdit object with the corresponding data.

        Parameters
        ----------
        Message: string
            Error message.
        Returns
        -------
        None.

        """
        self.text_browser.clear()
        self.text_browser.append(self.Message)
        self.setWindowModality(Qt.ApplicationModal)