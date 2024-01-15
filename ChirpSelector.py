import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import SpanSelector
from matplotlib.widgets import Button


class ChirpSelector():
    def __init__(self, wave, time, spec, corrector):
        """
        Initializes the ChirpSelector object, which allows for the visual
        selection of the wavelength range, where the chirp is located.

        Parameters
        ----------
        wave : np.array
            The wavelength data of the OKE measurement.
        time : np.array
            The delay data of the OKE measurement.
        spec : np.ndarray
            The absorption data of the OKE measurement.
        corrector : ChirpCorrector
            The ChripCorrector object created by the ChirpCorrector.py module,
            which handles the correction of the chirped data.

        Returns
        -------
        None.

        """
        self.corr = corrector
        self.wave = wave
        self.time = time
        self.spec = spec
        self.bounds = []
        self.axes = []
        self.all_lv = []
        self.initFigure()

    def initFigure(self):
        """
        Initilizes the matplotlib figure.

        Returns
        -------
        None.

        """
        self.fig = plt.figure(figsize=(6, 5.5), layout="constrained")
        self.gs = self.fig.add_gridspec(4, 4)
        self.axa = self.fig.add_subplot(self.gs[1, 0])
        self.axb = self.fig.add_subplot(self.gs[1, 1])
        self.axc = self.fig.add_subplot(self.gs[1, 2])
        self.axd = self.fig.add_subplot(self.gs[1, 3])
        button_width = 0.15
        button_height = 0.05
        button_padding = 0.01
        total_width = 4 * button_width + (4 - 1) * button_padding
        start_x = 0.5 - total_width / 2
        ax_Show_x = start_x + 0 * (button_width + button_padding)
        ax_Undo_x = start_x + 1 * (button_width + button_padding)
        ax_Res_x = start_x + 2 * (button_width + button_padding)
        ax_Cont_x = start_x + 3 * (button_width + button_padding)
        button_y = 0.5 - button_height / 2
        self.ax_Show = Button(self.axa, 'Show')
        self.ax_Undo = Button(self.axb, 'Undo')
        self.ax_Res = Button(self.axc, 'Reset', color='red')
        self.ax_Cont = Button(self.axd, 'Continue', color='green')
        self.ax_Show.on_clicked(self.show)
        self.ax_Undo.on_clicked(self.undo)
        self.ax_Res.on_clicked(self.reset)
        self.ax_Cont.on_clicked(self.cont)
        self.ax_Show.ax.set_position([ax_Show_x, button_y, button_width, button_height])
        self.ax_Undo.ax.set_position([ax_Undo_x, button_y, button_width, button_height])
        self.ax_Res.ax.set_position([ax_Res_x, button_y, button_width, button_height])
        self.ax_Cont.ax.set_position([ax_Cont_x, button_y, button_width, button_height])
        X, Y = np.meshgrid(self.wave, self.time)
        ax_full = self.fig.add_subplot(self.gs[0, :])
        ax_full.contourf(X, Y, self.spec, cmap="seismic")
        ax_full.set_title("OKE Measurement")
        self.span = SpanSelector(
            ax_full,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True
        )
        ax_text = self.fig.add_subplot(self.gs[2, :])
        ax_text.spines['top'].set_visible(False)
        ax_text.spines['right'].set_visible(False)
        ax_text.spines['bottom'].set_visible(False)
        ax_text.spines['left'].set_visible(False)
        ax_text.xaxis.set_ticks([])
        ax_text.yaxis.set_ticks([])
        text = "Please select the data range to use for the chirp fitting. \n You can select one or more areas with your mouse by left-clicking on the figure, holding and draging your mouse. \n Click 'Show' to show all selected areas, 'Undo' remove the last selected area, \n 'Reset' to remove all selected areas and 'Continue' once you are finished to start the fitting process."
        ax_text.text(0.5, 0.5, text, ha='center', va='center', fontsize=12)

    def onselect(self, xmin, xmax):
        """
        Save the selected span of the SpanSelector, if the selected span is
        bigger than 1. The span will be saved in the bounds list, which is then
        used by the undo, reset and show function.

        Parameters
        ----------
        xmin : float
            The lower x-axis bound of the selected span.
        xmax : float
            The upper x-axis bound of the selected span.

        Returns
        -------
        None.

        """
        if xmax - xmin > 1:
            self.bounds.append([xmin, xmax])

    def undo(self, event):
        """
        Removes the latest selected span form the selection.

        Parameters
        ----------
        event : button click event
            The event triggered by clicken the "Undo"-Button.

        Returns
        -------
        None.

        """
        if len(self.bounds) != 0:
            ax = self.axes.pop()
            self.fig.delaxes(ax)
            self.bounds.pop()
            self.all_lv.pop()
            if hasattr(self, "plotgrid"):
                for i in range(self.plotgrid.nrows - 1):
                    self.plotgrid[0, i].remove()
            self.fig.canvas.draw_idle()

    def reset(self, event):
        """
        Removes ALL selected spans form the selection.

        Parameters
        ----------
        event : button click event
            The event triggered by clicken the "Reset"-Button.

        Returns
        -------
        None.

        """
        if len(self.bounds) != 0:
            self.bounds = []
            self.all_lv = []
        if self.axes:
            while self.axes:
                ax = self.axes.pop()
                self.fig.delaxes(ax)
            self.fig.canvas.draw_idle()

    def show(self, event):
        """
        Shows all currently selected spans.

        Parameters
        ----------
        event : button click event
            The event triggered by clicken the "Show"-Button.

        Returns
        -------
        None.

        """
        if self.axes:
            while self.axes:
                ax = self.axes.pop()
                self.fig.delaxes(ax)
            self.fig.canvas.draw_idle()
        if self.bounds:
            self.plotgrid = self.gs[3, :].subgridspec(1, len(self.bounds))
        for ind, pair in enumerate(self.bounds):
            lv = (self.wave >= pair[0]) & (self.wave <= pair[1])
            self.all_lv.append(lv)
            region_x = self.wave[lv]
            region_y = self.spec[:, lv]
            if len(region_y[1]) >= 2:
                ax = self.fig.add_subplot(self.plotgrid[0, ind])
                X, Y = np.meshgrid(region_x, self.time)
                ax.contourf(X, Y, region_y, cmap="seismic")
                ax.set_xlim(region_x[0], region_x[-1])
                ax.set_ylim(self.time[0], self.time[-1])
                ax.get_yaxis().set_visible(False)
                self.axes.append(ax)
        self.fig.canvas.draw_idle()

    def cont(self, event):
        """
        Truncates the orignal data, so that only the selected spans are used in
        the fitting of the chirp. Starts the fitting process in the
        ChirpCorrector object and closes the selection figure.

        Parameters
        ----------
        event : button click event
            The event triggered by clicken the "Continue"-Button.

        Returns
        -------
        None.

        """
        if self.axes:
            full_lv = np.array(self.all_lv).any(axis=0)
            self.sel_wave = self.wave[full_lv]
            self.sel_spec = self.spec[:, full_lv]
            self.corr.prepareFitting(self.sel_wave, self.time, self.sel_spec)
            plt.close(self.fig)
