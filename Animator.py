import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Animation_Controller:
    def __init__(self, data, log, x_label, y_label, window):
        self.window = window
        self.x_points, self.y_points, self.z_points = data
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], lw=2)
        self.n_zpoints = len(self.z_points)
        self.current_frame = 0
        self.init_axes(log, x_label, y_label)

    def startup(self):
        self.ani = FuncAnimation(self.fig, self.update_animation,
                                 frames=self.n_zpoints,
                                 init_func=self.init_animation, blit=True)

    def update_animation(self, frame):
        self.window.frame_slider.setValue(frame)
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
                                  frames=self.n_zpoints,
                                  init_func=self.init_animation, blit=True,
                                  interval=frame_interval)
        self.ani.frame_seq = iter(range(self.current_frame, self.n_zpoints))
        self.ani.event_source.start()