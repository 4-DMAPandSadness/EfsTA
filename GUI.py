from PyQt5 import QtWidgets as QW
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPalette, QColor, QGuiApplication

class Main_Window(QW.QMainWindow):
    def __init__(self):
        super(Main_Window, self).__init__()
        self.setObjectName("EfsTA")
        self.create_elements()
        self.add_to_layout_x()

    def central_widget(self):
        pass

    def create_layouts(self):
        self.GVD_layout = QtWidgets.QGridLayout(self.GVD)
        self.GVD_layout.setObjectName("GVD_layout")

        self.grid_layout_7 = QW.QGridLayout(self.centralwidget)
        self.grid_layout_7.setObjectName("gridLayout_7")

        self.gridLayout_22 = QtWidgets.QGridLayout(self.Chirp)
        self.gridLayout_22.setObjectName("gridLayout_22")

        self.gridLayout_23 = QtWidgets.QGridLayout(self.Chirp_options)
        self.gridLayout_23.setObjectName("gridLayout_23")

        self.gridLayout_18 = QtWidgets.QGridLayout(self.Analysis)
        self.gridLayout_18.setObjectName("gridLayout_18")

        self.gridLayout_4 = QtWidgets.QGridLayout(self.Introduction)
        self.gridLayout_4.setObjectName("gridLayout_4")

        self.gridLayout = QtWidgets.QGridLayout(self.Data)
        self.gridLayout.setObjectName("gridLayout")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.Data_Modification)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.gridLayout_14 = QtWidgets.QGridLayout(self.Input_Confirmation)
        self.gridLayout_14.setObjectName("gridLayout_14")

        self.gridLayout_5 = QtWidgets.QGridLayout(self.Plotting_Details)
        self.gridLayout_5.setObjectName("gridLayout_5")

        self.gridLayout_6 = QtWidgets.QGridLayout(self.Plottting_Choices)
        self.gridLayout_6.setObjectName("gridLayout_6")

        self.gridLayout_3 = QtWidgets.QGridLayout(self.Plotting)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.gridLayout_28 = QtWidgets.QGridLayout(self.GTA_Custom_Lifetime_Matrix)
        self.gridLayout_28.setObjectName("gridLayout_28")

        self.gridLayout_15 = QtWidgets.QGridLayout(self.GTA_Optional_Inputs)
        self.gridLayout_15.setObjectName("gridLayout_15")

        self.gridLayout_9 = QtWidgets.QGridLayout(self.GTA_Model_Input)
        self.gridLayout_9.setObjectName("gridLayout_9")

        self.gridLayout_21 = QtWidgets.QGridLayout(self.GTA_algorith)
        self.gridLayout_21.setObjectName("gridLayout_21")

        self.gridLayout_16 = QtWidgets.QGridLayout(self.GTA_Custom_Model)
        self.gridLayout_16.setObjectName("gridLayout_16")

        self.gridLayout_10 = QtWidgets.QGridLayout(self.GTA_Custom_Matrix)
        self.gridLayout_10.setObjectName("gridLayout_10")

        self.gridLayout_11 = QtWidgets.QGridLayout(self.GTA)
        self.gridLayout_11.setObjectName("gridLayout_11")

        self.gridLayout_12 = QtWidgets.QGridLayout(self.GLA_Tau_Input)
        self.gridLayout_12.setObjectName("gridLayout_12")

        self.gridLayout_13 = QtWidgets.QGridLayout(self.GLA_Algorithm)
        self.gridLayout_13.setObjectName("gridLayout_13")

        self.gridLayout_17 = QtWidgets.QGridLayout(self.GLA_Select)
        self.gridLayout_17.setObjectName("gridLayout_17")

        self.gridLayout_8 = QtWidgets.QGridLayout(self.GLA)
        self.gridLayout_8.setObjectName("gridLayout_8")



    def create_elements(self):
        self.central_widget = QW.QWidget(Main_Window)
        self.central_widget.setObjectName("centralwidget")

        self.ui_stack = QW.QStackedWidget(self.centralwidget)
        self.ui_stack.setEnabled(True)
        self.ui_stack.setObjectName("ui_stack")

        self.experiment = QW.QWidget()
        self.experiment.setObjectName("experiment")

        self.Exp_TA = QW.QPushButton(self.Experiment)
        self.Exp_TA.setObjectName("Exp_TA")

        self.Exp_Introduction = QW.QTextBrowser(self.Experiment)
        self.Exp_Introduction.setObjectName("Exp_Introduction")

        self.Exp_trEPR = QW.QPushButton(self.Experiment)
        self.Exp_trEPR.setObjectName("Exp_trEPR")

        self.UI_stack.addWidget(self.Experiment)

        self.GVD = QW.QWidget()
        self.GVD.setObjectName("GVD")

    def add_to_layout_x(self):




        self.gridLayout_19 = QW.QGridLayout(self.Experiment)
        self.gridLayout_19.setObjectName("gridLayout_19")


        self.gridLayout_19.addWidget(self.Exp_TA, 1, 0, 1, 1)


        self.gridLayout_19.addWidget(self.Exp_Introduction, 0, 0, 1, 3)



        self.gridLayout_19.addWidget(self.Exp_trEPR, 1, 2, 1, 1)

