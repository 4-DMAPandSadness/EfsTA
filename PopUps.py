from PyQt5 import QtWidgets as QW
from PyQt5.QtCore import Qt
import numpy as np
import TTIMG

class TableWindow(QW.QWidget):
    def __init__(self, size):
        super(QW.QWidget, self).__init__()
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
        self.resize(self.size * 50 + 55, self.size * 50 + 80)
        self.setWindowModality(Qt.ApplicationModal)
        self.matrix_Table.setToolTip(
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Here you have to input the values for your custom kinetic matrix. How this matrix should look like and how to get there from the transition equation will be explained through the following example:</p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/Tooltips/images/tooltips/reaction example wt.png\" /></p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">In this photochemical process there are three different species with different lifetimes τ<span style=\" font-style:italic; vertical-align:sub;\">i</span><span style=\" font-style:italic;\">. </span></p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">There is an equilibrium between species <span style=\" color:#0000ff;\">A</span> &amp; <span style=\" color:#0000ff;\">B</span>, species <span style=\" color:#0000ff;\">A</span> decays into two species, <span style=\" color:#0000ff;\">B</span> &amp; <span style=\" color:#0000ff;\">C</span> and finally species <span style=\" color:#0000ff;\">C</span> decays back to the ground state.</p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The resulting 3x3 kinetic matrix for this example would look like this:</p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/Tooltips/images/tooltips/matrix example.png\" /></p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The position highlighted in red describes the decay of species <span style=\" color:#0000ff;\">A</span>. </p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The transition equation shows that species <span style=\" color:#0000ff;\">A</span> decays with τ<span style=\" vertical-align:sub;\">1</span> to species <span style=\" color:#0000ff;\">B</span> and with τ<span style=\" vertical-align:sub;\">5</span> to species <span style=\" color:#0000ff;\">C</span>, therefore the negative sum of the two lifetimes describes the decay of species <span style=\" color:#0000ff;\">A</span>.</p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The position highlighted in blue shows the dependence of species <span style=\" color:#0000ff;\">B</span> from species <span style=\" color:#0000ff;\">C</span>. Since there is no decay from species <span style=\" color:#0000ff;\">C</span> back to species <span style=\" color:#0000ff;\">B</span> the value is 0.</p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; text-decoration: underline;\">Input:</span></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">-31 |    3 | 0 </p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">   1 | -83 | 0 </p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> 30 |  80 | -4000 </p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Note:</span></p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This program transforms the lifetimes automatically into the corresponding rate constants for the calculation, so the input in each field in this table should be the guessed lifetime τ.</p>\n"
            "<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The values along the main diagonal must always be negative! All other values must be positive!<br /></p></body></html>"
        )

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
                if self.matrix_Table.item(i, j) is None:
                    K[i][j] = 0
                else:
                    K[i][j] = float(self.matrix_Table.item(i, j).text())
        self.custom_Matrix = K


class TextWindow(QW.QWidget):
    def __init__(self, model, Controller, Message):
        super(QW.QWidget, self).__init__()
        self.model = model
        self.Controller = Controller
        self.Message = Message
        self.initUI()

    def initUI(self):
        self.text_browser = QW.QTextBrowser()
        self.layout = QW.QGridLayout()
        self.layout.addWidget(self.text_browser, 0, 0, 1, 2)
        self.setLayout(self.layout)
        if self.Message is None:
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
