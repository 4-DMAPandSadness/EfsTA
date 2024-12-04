import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QSlider, QApplication, QLabel
from PyQt5.QtCore import Qt

#plt.style.use("/home/hackerman/Documents/Bachelor of Science/EfsTA/AK_Richert.mplstyle")

plt.style.use("seaborn-dark-palette")
'''
Aniamtion startet über Spyder nicht automatisch, erst, wenn man den framerate
slider verschiebt. über command shell funktionierts normal.
'''
class Animation_Controller:
    def __init__(self, data, log, x_label, y_label):
        self.x_points, self.y_points, self.z_points = data
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.n_zpoints = len(self.z_points)
        self.current_frame = 0
        self.init_axes(log, x_label, y_label)
        self.ani = FuncAnimation(self.fig, self.update_animation,
                                 frames=self.n_zpoints,
                                 init_func=self.init_animation, blit=True)
        

    def update_animation(self, frame):
        mainwindow.frame_slider.setValue(frame)
        self.line.set_data(self.x_points, self.y_points.T[frame])
        self.line.set_label(f"Delay: {self.z_points[frame]} ps")
        self.ax.legend()
        return self.line, self.ax.get_legend()

    def init_animation(self):
        self.line.set_data([], [])
        self.ax.legend()
        return self.line, self.ax.get_legend()
    
    def init_axes(self, log, x_label, y_label):
        self.ax.set_xlim(np.min(self.x_points), np.max(self.x_points))
        self.ax.set_ylim (np.min(self.y_points.flatten()), #*1.5 um clippen von Legende an 
                          np.max(self.y_points.flatten())) #*1.5 fixierter position zu verhindern
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        if log:
            self.ax.set_xscale("symlog")
            self.ax.set_title("Spectral Evolution of Absorption")
            self.line.set_label(f"Wavelength: {self.x_points[0]} nm")
        else:
            self.ax.set_title("Temporal Evolution of Absorption")
            self.line.set_label(f"Delay: {self.z_points[0]} ps")

    def save_animation(self, path):
        self.ani.save(path)

    def pause_animation(self):
        self.ani.pause()
        
    def resume_animation(self):
        self.ani.resume()

    def set_frame(self, frame):
        self.current_frame = frame
        self.update_animation(self.current_frame)
        self.ani.frame_seq = iter(range(self.current_frame, self.n_zpoints))

    def set_framerate(self, frame_interval):
        self.ani.event_source.stop()
        self.ani._stop()
        self.ani = FuncAnimation(self.fig, self.update_animation,
                                 frames=range(self.current_frame,
                                              self.n_zpoints),
                                 init_func=self.init_animation, blit=True,
                                 interval=frame_interval)
        self.ani.event_source.start()
        
class Animation_Display(QWidget):
    def __init__(self, animation_controller):
        super(QWidget, self).__init__()
        self.setMinimumSize(640, 480)
        self.control = animation_controller
        self.init_ui()
        
        
    def init_ui(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle("Animation")
        self.pause_button = QPushButton("Pause Animation")
        self.pause_button.clicked.connect(self.on_pause)
        self.layout.addWidget(self.pause_button,2,0,1,1)
        
        self.resume_button = QPushButton("Resume Animation")
        self.resume_button.clicked.connect(self.on_resume)
        self.layout.addWidget(self.resume_button,2,1,1,1)
        
        self.save_button = QPushButton("Save Animation")
        self.save_button.clicked.connect(self.on_save)
        self.layout.addWidget(self.save_button,2,2,1,1)
        
        self.rate_slider = QSlider(Qt.Horizontal)
        self.rate_slider.setRange(33, 500)
        self.rate_slider.setValue(200)
        self.rate_slider.valueChanged.connect(self.change_framerate)
        self.layout.addWidget(self.rate_slider,3,0,1,2)
        
        self.frame_slider = QSlider(Qt.Horizontal)
        self.frame_slider.valueChanged.connect(self.change_frame)
        self.frame_slider.setRange(0, self.control.n_zpoints-1)
        self.frame_slider.setTickPosition(QSlider.NoTicks)
        self.layout.addWidget(self.frame_slider,1,0,1,2)
        
        self.rate_label = QLabel(f"Current Frame Interval: {self.rate_slider.value()} ms.\n"
                                 f"Current Framerate: {round(1000/self.rate_slider.value(),2)} FPS.")
        self.layout.addWidget(self.rate_label,3,2,1,1)
        
        self.frame_label = QLabel(f"Current Frame: {self.frame_slider.value()}.")
        self.layout.addWidget(self.frame_label,1,2,1,1)
        
        self.canvas = FigureCanvas(self.control.fig)
        self.layout.addWidget(self.canvas,0,0,1,3)
        
    def on_save(self, path):
        self.control.save_animation(path)
        
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

wave = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_lambda.txt"
delay = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_delays.txt"
spec = "/home/hackerman/Documents/Bachelor of Science/fsTA Daten/PDI4sg-biph-trityl/PDI4sg_biph_trityl_tol_530_export_taspectra.txt"
     
del_points = np.genfromtxt(delay)
wav_points = np.genfromtxt(wave)
spec_points = np.genfromtxt(spec)

if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setStyle('Fusion')
    ac = Animation_Controller([wav_points, spec_points, del_points], False, "Wavelength / nm", "Abs.")
    #ac = Animation_Controller([del_points, spec_points.T, wav_points], True, "Delay / ps", "Abs.")
    mainwindow = Animation_Display(ac)
    app.setQuitOnLastWindowClosed(True)
    mainwindow.show()
    sys.exit(app.exec_())