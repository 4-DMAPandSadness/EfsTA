from PyQt5 import QtWidgets as QW
from PyQt5.QtCore import Qt
import numpy as np
import TTIMG
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Animator import Animation_Controller

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


class Plot_Display(QW.QDialog):
    def __init__(self, fig, text):
        super(QW.QDialog, self).__init__()
        self.setMinimumSize(640, 480)
        self.fig = fig
        self.layout = QW.QVBoxLayout()
        self.setLayout(self.layout)
        if text:
            self.text = QW.QTextBrowser()
            self.text.setText(text)
            self.layout.addWidget(self.text)
            self.done = QW.QPushButton("Done")
            self.layout.addWidget(self.done)
            self.done.clicked.connect(self.no_func)

        self.canvas = FigureCanvas(fig)
        self.canvas.draw_idle()
        self.layout.addWidget(self.canvas)

    def no_func(self):
        self.line

class Multi_Plot_Display(QW.QDialog):
    def __init__(self, figs):
        super(QW.QDialog, self).__init__()
        self.setMinimumSize(640, 480)
        self.layout = QW.QGridLayout()
        self.setLayout(self.layout)
        self.delslide = QW.QSlider(Qt.Orientation.Vertical)
        self.delslide.setMinimum(0)
        self.delslide.setMaximum(1000)
        self.layout.addWidget(self.delslide,0,1)
        self.waveslide = QW.QSlider(Qt.Orientation.Horizontal)
        self.waveslide.setMinimum(480)
        self.waveslide.setMaximum(800)
        self.layout.addWidget(self.waveslide,1,0)
        self.canvas0 = FigureCanvas(figs[0])
        self.canvas1 = FigureCanvas(figs[1])
        self.canvas2 = FigureCanvas(figs[2])
        self.canvas0.draw_idle()
        self.canvas1.draw_idle()
        self.canvas2.draw_idle()
        self.layout.addWidget(self.canvas0,0,0)
        self.layout.addWidget(self.canvas1,2,0)
        self.layout.addWidget(self.canvas2,0,2)
        self.line = figs[3]
        self.line2 = figs[4]
        self.line3 = figs[5]
        self.line4 = figs[6]
        self.delslide.valueChanged.connect(lambda: self.no_func(self.delslide.value()))
        self.waveslide.valueChanged.connect(lambda: self.no_func2(self.waveslide.value()))

        self.layout2 = QW.QVBoxLayout()
        self.delslide_view = QW.QLineEdit()
        self.delslide_view.setReadOnly(True)
        self.delslide_view.setPlaceholderText("Displays the Delay")
        self.waveslide_view = QW.QLineEdit()
        self.waveslide_view.setReadOnly(True)
        self.waveslide_view.setPlaceholderText("Displays the Wavelength")
        self.layout2.addWidget(self.waveslide_view)
        self.layout2.addWidget(self.delslide_view)
        self.layout.addLayout(self.layout2,2,2)

    def no_func(self,sliderval):
        self.delslide_view.setText(f"Delay Index: {sliderval}")
        self.line.set_ydata([sliderval,sliderval])
        self.canvas0.draw()

    def no_func2(self,sliderval):
        self.waveslide_view.setText(f"Wave Index: {sliderval}")
        self.line2.set_xdata([sliderval,sliderval])
        self.canvas0.draw()


class Animation_Display(QW.QWidget):
    def __init__(self, data, log, x, y):
        super(QW.QWidget, self).__init__()
        self.path = "/home/hackerman/Desktop"
        self.setMinimumSize(640, 480)
        self.control = Animation_Controller(data, log, x, y, self)
        self.init_ui()
        self.control.startup()

    def init_ui(self):
        self.layout = QW.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Animation")
        self.pause_button = QW.QPushButton("Pause Animation")
        self.pause_button.clicked.connect(self.on_pause)
        self.layout.addWidget(self.pause_button,2,0,1,1)

        self.resume_button = QW.QPushButton("Resume Animation")
        self.resume_button.clicked.connect(self.on_resume)
        self.layout.addWidget(self.resume_button,2,1,1,1)

        self.save_button = QW.QPushButton("Save Animation")
        self.save_button.clicked.connect(self.on_save)
        self.layout.addWidget(self.save_button,2,2,1,1)

        self.rate_slider = QW.QSlider(Qt.Horizontal)
        self.rate_slider.setRange(33, 500)
        self.rate_slider.setValue(200)
        self.rate_slider.valueChanged.connect(self.change_framerate)
        self.layout.addWidget(self.rate_slider,3,0,1,2)

        self.frame_slider = QW.QSlider(Qt.Horizontal)
        self.frame_slider.valueChanged.connect(self.change_frame)
        self.frame_slider.setRange(0, self.control.n_zpoints-1)
        self.frame_slider.setTickPosition(QW.QSlider.NoTicks)
        self.layout.addWidget(self.frame_slider,1,0,1,2)

        self.rate_label = QW.QLabel(f"Current Frame Interval: {self.rate_slider.value()} ms.\n"
                                 f"Current Framerate: {round(1000/self.rate_slider.value(),2)} FPS.")
        self.layout.addWidget(self.rate_label,3,2,1,1)

        self.frame_label = QW.QLabel(f"Current Frame: {self.frame_slider.value()}.")
        self.layout.addWidget(self.frame_label,1,2,1,1)

        self.canvas = FigureCanvas(self.control.fig)
        self.layout.addWidget(self.canvas,0,0,1,3)

        self.control.init_animation()

    def on_save(self):
        self.control.save_animation(self.path+"/test.mp4")

    def on_pause(self):
        self.control.pause_animation()

    def on_resume(self):
        self.control.resume_animation()

    def change_framerate(self):
        new_framerate = self.rate_slider.value()
        self.control.set_framerate(new_framerate)
        self.rate_label.setText(f"Current Frame Interval: {new_framerate} ms.\n"
                                f"Current Framerate: {round(1000/new_framerate,2)} FPS.")

    def change_frame(self):
        new_frame = self.frame_slider.value()
        self.control.set_frame(new_frame)
        self.frame_label.setText(f"Current Frame: {new_frame}.")

# class Group_Velocity_Dispersion(QW.Dialog):
#     def __init__(self):
#         super(QW.QDialog, self).__init__()
#         self.setMinimumSize(640, 480)
