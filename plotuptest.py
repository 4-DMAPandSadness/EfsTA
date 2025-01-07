import numpy as np
import PopUps as pu
import Plotter as pt
import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout

class Main(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        wave = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_lambda.txt"
        delay = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_delays.txt"
        spec = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_taspectra.txt"
        del_points = np.genfromtxt(delay)
        wav_points = np.genfromtxt(wave)
        spec_points = np.genfromtxt(spec)

        # wave = [400,500,600]
        # time = [30,600, 2300]
        # path = "/home/hackerman/temp"
        # name = "test"
        # labels = ["a / b", "c / d", "e / f"]
        # self.plot = pt.Plotter("seaborn-dark-palette", wav_points, del_points, spec_points, path, name)
        # self.fig = self.plot.plot_heat(wave, time, None, None, spec_points, 20, 1, labels, add = "")


        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.btn = QPushButton("test")
        self.btn.clicked.connect(lambda: self.test([wav_points, spec_points, del_points], False, "Wavelength / nm", "$\\Delta$Abs. / a.u."))
        self.layout.addWidget(self.btn)

    def test(self, data, log, x, y):
        self.popup = pu.Animation_Display(data, log, x, y)
        self.popup.show()

if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setStyle('Fusion')
    mainwindow = Main()
    mainwindow.show()
    sys.exit(app.exec_())