from PyQt5 import QtWidgets as QW
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPalette, QColor, QGuiApplication
from datetime import datetime

import matplotlib.pyplot as plt

import PopUps as PU
import ChirpCorrector as CC
import Controller as Cont

import numpy as np
import os as os
import TTIMG
import Settings as SET
import logging

from Importers import RichertOKEImport

class MainWindow(QW.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = loadUi("gui.ui", self)
        self.start_up()
        self.functionality()

    def start_up(self):
        self.ui.UI_stack.setCurrentIndex(0)
        self.default_palette = QGuiApplication.palette()
        self.finalInputs = {}
        self.ui.input_tree.header().setSectionResizeMode(QW.QHeaderView.ResizeToContents)
        self.radios = QW.QButtonGroup(self)
        self.radios.addButton(self.ui.GLA_radio)
        self.radios.addButton(self.ui.GTA_radio_preset_model)
        self.radios.addButton(self.ui.GTA_radio_custom_model)
        self.radios.addButton(self.ui.GTA_radio_custom_matrix)
        self.ui.Analysis_stack.setCurrentIndex(0)
        self.create_theme()

    def on_quit(self):
        app.setPalette(self.default_palette)
        self.save_all_inputs()
        self.save_pickle()

    def functionality(self):
        self.ui.actionTheme.triggered.connect(self.change_theme)
        self.ui.actionOptions.triggered.connect(self.options)
        app.aboutToQuit.connect(self.on_quit)
        self.ui.Exp_TA.clicked.connect(self.init_ta)
        self.ui.Exp_trEPR.clicked.connect(self.init_epr)
        self.ui.GVD_skip.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(3))
        self.ui.GVD_correct.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(2))
        self.ui.GVD_back.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(0))
        self.ui.Chirp_Browse_Sample.clicked.connect(lambda: self.get_filepath("button", self.ui.Chirp_Sample_Dir))
        self.ui.Chirp_Browse_Solvent.clicked.connect(lambda: self.get_filepath("button", self.ui.Chirp_Solvent_Dir))
        self.ui.Chirp_Browse_Chirp.clicked.connect(lambda: self.get_filepath("button", self.ui.Chirp_Chirp_Dir))
        self.ui.Chirp_Sample_Dir.editingFinished.connect(lambda: self.get_filepath("text", self.ui.Chirp_Sample_Dir))
        self.ui.Chirp_Solvent_Dir.editingFinished.connect(lambda: self.get_filepath("text", self.ui.Chirp_Solvent_Dir))
        self.ui.Chirp_Chirp_Dir.editingFinished.connect(lambda: self.get_filepath("text", self.ui.Chirp_Chirp_Dir))
        self.ui.Chirp_Done.clicked.connect(self.check_chirp_files_if_empty)
        self.ui.Chirp_Scatter.clicked.connect(lambda: self.ui.Chirp_Exclude_Wave.setEnabled(self.ui.Chirp_Scatter.isChecked()))
        self.ui.Chirp_Back.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(1))
        self.ui.Chirp_plotRaw.clicked.connect(self.plot_raw_gvd)
        self.ui.Data_directory.editingFinished.connect(lambda: self.get_directory("text", self.ui.Data_directory))
        self.ui.Data_backToChirp.clicked.connect(lambda: self.ui.UI_stack.setCurrentIndex(2))
        self.ui.Analysis_stack.currentChanged.connect(self.present_inputs)
        self.ui.Data_browse.clicked.connect(lambda: self.get_directory("button", self.ui.Data_directory))
        self.ui.input_confirm.clicked.connect(self.check_all_final)
        self.ui.GTA_input_custom_model_saved_equations.currentIndexChanged.connect(lambda: self.set_custom_model(self.ui.GTA_input_custom_model_saved_equations.currentIndex()))
        self.ui.Data_clear_cache.clicked.connect(self.clear_pickle)
        self.ui.GTA_open_table.clicked.connect(self.check_custom_matrix_size_if_empty)
        self.ui.GTA_custom_model_save.clicked.connect(self.save_custom_model)
        self.ui.GTA_custom_model_del.clicked.connect(self.delete_custom_model)
        self.ui.Plotting_raw.clicked.connect(self.plotting_raw)
        self.ui.GTA_input_preset_model_tau.editingFinished.connect(lambda: self.summon_radio_buttons("preset"))
        self.ui.GTA_input_custom_model_tau.editingFinished.connect(lambda: self.summon_radio_buttons("custom"))
        self.ui.GLA_input_tau.editingFinished.connect(lambda: self.summon_radio_buttons("gla"))

    def init_ta(self):
        self.ui.plot_type.addItems(["fsTA", "nsTA"])
        self.ui.plot_xAxis.setText("$\\lambda$ / nm")
        self.ui.plot_yAxis.setText("delay / ps")
        self.ui.plot_zAxis.setText("$\\Delta A$")
        self.ui.UI_stack.setCurrentIndex(1)
        self.ui.plot_type.currentIndexChanged.connect(lambda: self.set_axis_ta(self.ui.plot_type.currentIndex()))

    def init_epr(self):
        self.ui.plot_type.addItems(["μs trEPR", "ms trEPR"])
        self.ui.plot_xAxis.setText("$B_0$ / mT")
        self.ui.plot_yAxis.setText("time / $\\mu$s")
        self.ui.plot_zAxis.setText("d$\\chi$'' / d$B_0$")
        self.ui.UI_stack.setCurrentIndex(3)
        self.ui.plot_type.currentIndexChanged.connect(lambda: self.set_axis_epr(self.ui.plot_type.currentIndex()))

###################################Utility#####################################

    def read_single_value(self, UI_element):
        text = UI_element.text()
        if text:
            value = float(text)
        else:
            value = None
        return value

    def read_list(self, UI_element):
        text = UI_element.text()
        if text:
            values = text.split(',')
            for ind, val in enumerate(values):
                if val:
                    values[ind] = float(val)
                else:
                    val.remove("")
        else:
            values = []
        return values

    def get_directory(self, input_type, UI_element):
        if input_type == "button":
            directory = QW.QFileDialog.getExistingDirectory(self, 'Select Folder')
            UI_element.setText(directory)
        elif input_type == "text":
            directory = UI_element.text()
        self.read_data(directory)

    def get_filepath(self, input_type, UI_element):
        if input_type == "button":
            directory = QW.QFileDialog.getOpenFileName(self, 'Select File')
            UI_element.setText(directory[0])
        elif input_type == "text":
            directory = UI_element.text()

    def corr_chirp(self, sample_dir, solvent_dir, chirp_dir, rmBG, OKE):
        options = {"Scatter": self.ui.Chirp_Scatter.isChecked(),
                   "Manually": self.ui.Chirp_Manually.isChecked(),
                   "rmBG": rmBG,
                   "OKE": OKE
                   }
        x = {"Sample_Dir": sample_dir,
             "Solvent_Dir": solvent_dir,
             "Chirp_Dir": chirp_dir,
             "Wave_Range": self.read_list(self.ui.Chirp_Wave_Range),
             "Scale": self.read_single_value(self.ui.Chirp_Scale),
             "Exc_Wave": self.read_single_value(self.ui.Chirp_Exclude_Wave),
             "Header": self.ui.Chirp_Header.value(),
             "Options": options
             }
        CCorr = CC.ChirpCorrector(x, self)
        CCorr.correctData()

    def plot_raw_gvd(self):
        sample_dir = self.ui.Chirp_Sample_Dir.text()
        if sample_dir:
            data = RichertOKEImport.get_data(sample_dir, header=self.ui.Chirp_Header.value())
            wave, time, spec = RichertOKEImport.split_data(data)

            self.fig, self.ax = plt.subplots()
            X, Y = np.meshgrid(wave, time)
            self.ax.contourf(X, Y, spec.T, cmap="seismic")
            self.ax.set_yscale('symlog')
            self.ax.set_title("Raw Data")
            self.popup = PU.Plot_Display(self.fig, None)
            self.popup.show()

#####################################Check#####################################

    def check_chirp_files_if_empty(self):
        sample_dir = self.ui.Chirp_Sample_Dir.text()
        solvent_dir = self.ui.Chirp_Solvent_Dir.text()
        chirp_dir = self.ui.Chirp_Chirp_Dir.text()
        rmBG, OKE = True, True
        if sample_dir == "":
            self.open_popup_error("Please provide a sample file.")
            return
        if solvent_dir == "":
            rmBG = False
            self.open_popup_error("Warning! No background provided. "
                                  "Correction will proceede without "
                                  "background subtraction.")
        if chirp_dir == "":
            OKE = False
            self.open_popup_error("Warning! No chirp/OKE measurment provided. "
                                  "Correction quality will be lower.")
            self.ui.Chirp_Manually.setChecked(False)
        self.corr_chirp(sample_dir, solvent_dir, chirp_dir, rmBG, OKE)

    def check_directory_if_empty(self):
        if self.ui.Data_directory.text() == "":
            self.open_popup_error("Please select a folder directory.")
            return True

    def check_axis_if_empty(self):
        if (self.ui.plot_xAxis.text() or self.ui.plot_yAxis.text() or self.ui.plot_zAxis.text()) == "":
            self.open_popup_error("Please input guessed lifetimes.")
            return True

    def check_gla_tau_if_empty(self):
        if self.ui.GLA_input_tau.text() == "":
            self.open_popup_error("Please input guessed lifetimes.")
            return True

    def check_bounds_if_match(self):
        if self.ui.GTA_input_tau_lb.text():
            if (self.ui.GTA_input_tau_lb.text().count(",") !=
                    self.ui.GTA_input_preset_model_tau.text().count(",")):
                self.open_popup_error("Please provide a bound for each lifetime.")
                return False
        if self.ui.GTA_input_tau_ub.text():
            if (self.ui.GTA_input_tau_ub.text().count(",") !=
                    self.ui.GTA_input_preset_model_tau.text().count(",")):
                self.open_popup_error("Please provide a bound for each lifetime.")
                return False

    def check_preset_model_tau_if_empty(self):
        if self.ui.GTA_input_preset_model_tau.text() == "":
            self.open_popup_error("Please input guessed lifetimes.")
            return True

    def check_custom_model_if_empty(self):
        if self.ui.GTA_input_custom_model_equation.text() == "":
            self.open_popup_error("Please input a transition equation.")
            return True
        elif self.ui.GTA_input_custom_model_tau.text() == "":
            self.open_popup_error("Please input guessed lifetimes.")
            return True

    def check_custom_matrix_size_if_empty(self):
        if self.ui.GTA_input_rows_and_columns.value():
            self.ui.GTA_radio_custom_matrix.setChecked(True)
            self.open_popup_matrix_input(self.ui.GTA_input_rows_and_columns.value())
        else:
            self.open_popup_error("Please input a table size.")
            return True

    def check_custom_matrix_if_empty(self):
        if hasattr(self, 'custom_Matrix') is False:
            self.open_popup_error("Please input a kinetic matrix.")
            return True

    def check_method_if_selected(self):
        if(self.ui.GLA_radio.isChecked() is False and
               self.ui.GTA_radio_preset_model.isChecked() is False and
               self.ui.GTA_radio_custom_model.isChecked() is False and
               self.ui.GTA_radio_custom_matrix.isChecked() is False):
            self.open_popup_error("Please select an analysis method.")
            return False

    def check_wavelength_slices_if_empty(self):
        if self.ui.plot_input_wavelength_slices.text() == "":
            self.ui.plot_wavelength_slices.setChecked(False)

    def check_delay_slices_if_empty(self):
        if self.ui.plot_input_delay_slices.text() == "":
            self.ui.plot_delay_slices.setChecked(False)

    def check_all_final(self):
        self.check_wavelength_slices_if_empty()
        self.check_delay_slices_if_empty()
        self.check_axis_if_empty()
        if self.check_directory_if_empty() is True:
            return
        if (self.check_method_if_selected() is False):
            return
        if self.check_bounds_if_match() is False:
            return
        if (self.ui.GLA_radio.isChecked() is True and
                self.check_gla_tau_if_empty() is True):
            return
        elif (self.ui.GTA_radio_preset_model.isChecked() is True and
                self.check_preset_model_tau_if_empty() is True):
            return
        elif (self.ui.GTA_radio_custom_model.isChecked() is True and
                self.check_custom_model_if_empty() is True):
            return
        elif (self.ui.GTA_radio_custom_matrix.isChecked() is True and
                self.checkCustomMatrixIfEmpty() is True):
            return
        else:
            self.start_analysis()
###############################################################################

    def read_data(self, directory):
        if directory:
            self.finalInputs['Directory'] = directory
            self.Controller = Cont.Controller(directory)
            path = self.Controller.path + "/"
            if hasattr(self.Controller, "name"):
                name = self.Controller.name
                txt = name + "_input_backup"
                pickle = path + txt + ".dir"
                if os.path.isfile(pickle):
                    self.set_pickle()
            else:
                self.open_popup_error('Please make sure the selected folder ' +
                                  'contains *.txt files ending with: \n' +
                                  '"taspectra.txt", "delays.txt" and' +
                                  '"lambda.txt" for TA or \n' +
                                  '"eprspectra.txt", "time.txt" and' +
                                  '"field.txt" for trEPR.')
        else:
            self.open_popup_error("Please select a folder directory.")

    def get_multiplier(self):
        if (self.ui.Data_input_multiplier.text() == "" or
                int(self.ui.Data_input_multiplier.text()) <= 0):
            mul = 1
        else:
            mul = int(self.ui.Data_input_multiplier.text())
        return mul



    def get_axis(self):
        self.Controller.labels = [self.ui.plot_xAxis.text(),
                                  self.ui.plot_yAxis.text(),
                                  self.ui.plot_zAxis.text()]

    def set_axis_ta(self, ind):
        if ind == 0:
            self.ui.plot_xAxis.setText("$\\lambda$ / nm")
            self.ui.plot_yAxis.setText("delay / ps")
            self.ui.plot_zAxis.setText("$\\Delta A$")
        if ind == 1:
            self.ui.plot_xAxis.setText("$\\lambda$ / nm")
            self.ui.plot_yAxis.setText("delay / ns")
            self.ui.plot_zAxis.setText("$\\Delta A$")

    def set_axis_epr(self, ind):
        if ind == 0:
            self.ui.plot_xAxis.setText("$B_0$ / mT")
            self.ui.plot_yAxis.setText("time / $\\mu$s")
            self.ui.plot_zAxis.setText("d$\\chi$'' / d$B_0$")
        if ind == 1:
            self.ui.plot_xAxis.setText("$B_0$ / mT")
            self.ui.plot_yAxis.setText("time / ms")
            self.ui.plot_zAxis.setText("d$\\chi$'' / d$B_0$")

#####################################GLA#######################################



    def start_gla(self, db, wb, model,  opt_method, ivp_method):
        self.Controller.genModel(db, wb, model, opt_method, ivp_method)
        self.tau_fit = self.Controller.calcDAS(self.prepare_parameter("gla"), db, wb, self.ui.GLA_algorithm_optimize.currentText())
        self.open_popup_results(0, self.Controller)

#####################################GTA#######################################



    def get_tau_bounds(self):
        tau_lb = self.read_list(self.ui.GTA_input_tau_lb)
        tau_ub = self.read_list(self.ui.GTA_input_tau_ub)
        if any(isinstance(obj, float) for obj in tau_lb):
            tau_lb = [None if item == '' else item for item in tau_lb]
        else:
            tau_lb = []
        if any(isinstance(obj, float) for obj in tau_ub):
            tau_ub = [None if item == '' else item for item in tau_ub]
        else:
            tau_ub = []
        return [tau_lb, tau_ub]

    def get_concentration(self):
        c0 = self.read_list(self.ui.GTA_input_concentration)
        if any(isinstance(obj, float) for obj in c0):
            c0 = c0
        else:
            c0 = []
        return c0

    def start_gta(self, db, wb, model, K):
        optim = self.ui.GTA_algorithm_optimize.currentText()
        ivps = self.ui.GTA_algorithm_initial_value_problem.currentText()
        self.Controller.genModel(db, wb, model, optim, ivps)
        c = self.get_concentration()
        tb = self.get_tau_bounds()
        K = np.array(K)
        if model == "custom matrix":
            self.tau_fit = self.Controller.calcSAS(K, [], c, db, wb, [], [], optim, ivps)
        elif model == "custom model":
            self.tau_fit = self.Controller.calcSAS(K,
                                                   self.prepare_parameter("custom"),
                                                   c, db, wb, [], [], optim, ivps)
        else:
            self.tau_fit = self.Controller.calcSAS(K, self.prepare_parameter("preset"),
                                                   c, db, wb, tb[0], tb[1], optim, ivps)
        self.open_popup_results(model, self.Controller)

    def save_custom_model(self):
        if self.ui.GTA_input_custom_model_equation.text() == "":
            pass
        elif self.ui.GTA_input_custom_model_saved_equations.findText(self.ui.GTA_input_custom_model_equation.text()) != -1:
            pass
        else:
            self.ui.GTA_input_custom_model_saved_equations.addItem(self.ui.GTA_input_custom_model_equation.text())

    def delete_custom_model(self):
        if self.ui.GTA_input_custom_model_saved_equations.currentText() == "":
            pass
        else:
            self.ui.GTA_input_custom_model_saved_equations.removeItem(self.ui.GTA_input_custom_model_saved_equations.currentIndex())

    def set_custom_model(self, ind):
        self.ui.GTA_input_custom_model_saved_equations.setCurrentIndex(ind)
        model = self.ui.GTA_input_custom_model_saved_equations.currentText()
        self.ui.GTA_input_custom_model_equation.setText(model)

    def get_custom_model(self):
        eq = self.ui.GTA_input_custom_model_equation.text()
        tau = self.read_list(self.ui.GTA_input_custom_model_tau)
        eq = eq.replace("->", "")
        eq_split = eq.split(";")
        separated_species = []
        for string in eq_split:
            temp = list(string)
            separated_species.append(temp)
        paired_species = []
        for list_ in separated_species:
            for i in range(len(list_) - 1):
                paired_species.append([list_[i], list_[i + 1]])
        for list_ in paired_species:
            for i in range(len(list_)):
                if list_[i] == "v":
                    list_[i] = -1
                else:
                    list_[i] = ord(list_[i])%32-1
        all_numbers = np.array(paired_species).flatten()
        if -1 in all_numbers:
            species = len(np.unique(all_numbers)) - 1
        else:
            species = len(np.unique(all_numbers))
        M = np.zeros((species, species))
        tau_index = 0
        for list_ in paired_species:
            if list_[1] == -1:
                M[list_[0]][list_[0]] += tau[tau_index]
            else:
                if list_[0] < list_[1]:
                    M[list_[0]][list_[0]] += tau[tau_index]
                    M[list_[1]][list_[0]] += tau[tau_index]
                elif list_[0] > list_[1]:
                    M[list_[0]][list_[0]] += tau[tau_index]
                    M[list_[1]][list_[0]] += tau[tau_index]
                else:
                    M[list_[0]][list_[0]] += tau[tau_index]
            tau_index += 1
        N = np.ones((species, species))
        np.fill_diagonal(N, -1)
        M = M * N
        if M[-1][-1] == -0:
            M[-1][-1] *= -1
        return M



    def close_matrix_popup(self, popup):
        self.custom_Matrix = popup.custom_Matrix
        popup.close()

#####################################PREPARE PARAMETERS########################

    def summon_radio_buttons(self, layout_origin):
        if layout_origin == "preset":
            layout = self.ui.GTA_preset_model_fix_layout
            taus = self.ui.GTA_preset_model_selection.currentIndex()
            self.ui.GTA_radio_preset_model.setChecked(True)
        elif layout_origin == "custom":
            layout = self.ui.GTA_custom_model_fix_layout
            taus = self.read_list(self.ui.GTA_input_custom_model_tau)
            self.ui.GTA_radio_custom_model.setChecked(True)
        elif layout_origin == "gla":
            layout = self.ui.GLA_fix_layout
            taus = self.read_list(self.ui.GLA_input_tau)
            self.ui.GLA_radio.setChecked(True)
        for i in reversed(range(layout.count())):
            widgetToRemove = layout.itemAt(i).widget()
            widgetToRemove.deleteLater()
        for tau in taus:
            layout.addWidget(QW.QRadioButton(str(tau), autoExclusive=False))

    def prepare_parameter(self, method):
        if method == "preset":
            layout = self.ui.GTA_preset_model_fix_layout
            taus = self.read_list(self.ui.GTA_input_preset_model_tau)
        elif method == "custom":
            layout = self.ui.GTA_custom_model_fix_layout
            taus = self.getGTACustomModelTaus()
        elif method == "gla":
            layout = self.ui.GLA_fix_layout
            taus = self.read_list(self.ui.GLA_input_tau)
        widgets = (layout.itemAt(i).widget() for i in range(layout.count()))
        if layout.count() == 0:
            prepParam = [(t, True) for t in taus]
        else:
            prepParam = []
        for widget in widgets:
            if isinstance(widget, QW.QRadioButton):
                prepParam.append((float(widget.text()), not widget.isChecked()))
        return prepParam

#####################################PLOT######################################
    def get_user_contour(self):
        if self.ui.plot_input_contour.value() == 0:
            cont = 20
        else:
            cont = self.ui.plot_input_contour.value()
        return cont

    def plotting_raw(self):
        if hasattr(self, "Controller") is False:
            self.open_popup_error("Please select a directory first.")
        else:
            if hasattr(self.Controller, "name") is False:
                self.open_popup_error("Please select a valid directory first.")
            else:
                self.get_axis()
                ds = sorted(self.read_list(self.ui.plot_input_delay_slices))
                ws = sorted(self.read_list(self.ui.plot_input_wavelength_slices))
                db = [self.read_single_value(self.ui.Data_delay_input_lb),
                      self.read_single_value(self.ui.Data_delay_input_ub)]
                wb = [self.read_single_value(self.ui.Data_wavelength_input_lb),
                      self.read_single_value(self.ui.Data_wavelength_input_ub)]
                self.ui.plot_concentrations.setChecked(False)
                self.ui.plot_das_sas.setChecked(False)
                self.ui.plot_residuals.setChecked(False)
                self.plotting(ds, ws, 0, True)

    def plotting(self, ds, ws, model, raw):
        vmin = self.read_single_value(self.ui.plot_input_vmin)
        vmax = self.read_single_value(self.ui.plot_input_vmax)
        cont = self.get_user_contour()
        mul = self.get_multiplier()
        plot_params = {"ws": ws,
                       "ds": ds,
                       "vmin": vmin,
                       "vmax": vmax,
                       "cont": cont,
                       "mul": mul
                        }
        if raw is True:
            if self.ui.plot_wavelength_slices.isChecked() is True:
                self.raw_ws = self.Controller.plotSolo(ws, ds, vmin, vmax, None, cont, "WS", mul)
            if self.ui.plot_delay_slices.isChecked() is True:
                self.raw_ds = self.Controller.plotSolo(ws, ds, vmin, vmax, None, cont, "DS", mul)
            if self.ui.plot_heatmap.isChecked() is True:
                self.raw_h = self.Controller.plotSolo(ws, ds, vmin, vmax, None, cont, "H", mul)
            if self.ui.plot_three_in_one.isChecked() is True:
                self.raw_3in1 = self.Controller.plot3inOne(ws, ds, vmin, vmax, cont, mul)
            if self.ui.plot_threed_contour.isChecked() is True:
                self.raw_3d =self.Controller.plot3D(vmin, vmax, mul)
        if raw is False:
            if self.ui.plot_wavelength_slices.isChecked() is True:
                self.Controller.plotSolo(ws, ds, vmin, vmax, model, cont, "WS", mul)
            if self.ui.plot_delay_slices.isChecked() is True:
                self.Controller.plotSolo(ws, ds, vmin, vmax, model, cont, "DS", mul)
            if self.ui.plot_heatmap.isChecked() is True:
                self.Controller.plotSolo(ws, ds, vmin, vmax, model, cont, "H", mul)
            if self.ui.plot_three_in_one.isChecked() is True:
                self.Controller.plot3inOne(ws, ds, vmin, vmax, model, cont, mul)
            if self.ui.plot_threed_contour.isChecked() is True:
                self.Controller.plot3D(vmin, vmax, model, mul)
            if self.ui.plot_residuals.isChecked() is True:
                self.Controller.plot2Dresiduals(vmin, vmax, model, cont, mul)
            if self.ui.plot_das_sas.isChecked() is True:
                self.Controller.plotDAS(model, self.tau_fit, mul)
            if self.ui.plot_concentrations.isChecked() is True:
                self.Controller.plotKinetics(model)

#####################################CONFIRM###################################



    def start_analysis(self):
        self.get_axis()
        self.save_pickle()
        ds = sorted(self.read_list(self.ui.plot_input_delay_slices))
        ws = sorted(self.read_list(self.ui.plot_input_wavelength_slices))
        db = [self.read_single_value(self.ui.Data_delay_input_lb),
              self.read_single_value(self.ui.Data_delay_input_ub)]
        wb = [self.read_single_value(self.ui.Data_wavelength_input_lb),
              self.read_single_value(self.ui.Data_wavelength_input_ub)]
        if self.GLA_radio.isChecked() is True:
            self.start_gla(db, wb)
            self.plotting_fit(ds, ws, 0, False)
        elif self.GTA_radio_preset_model.isChecked() is True:
            model = self.ui.GTA_preset_model_selection.currentIndex() + 1
            K = self.getGTAPresetModelTaus()
            self.start_gta(db, wb, model, K)
            self.plotting_fit(ds, ws, model, False)
        elif self.GTA_radio_custom_model.isChecked() is True:
            model = "custom model"
            K = self.get_custom_model()
            self.start_gta(db, wb, model, K)
            self.plotting_fit(ds, ws, model, False)
        elif self.GTA_radio_custom_matrix.isChecked() is True:
            model = "custom matrix"
            K = self.custom_Matrix
            self.start_gta(db, wb, model, K)
            self.plotting_fit(ds, ws, model, False)

#####################################POPUP#####################################

    def open_popup_matrix_input(self, size):
        popup = PU.TableWindow(size)
        popup.show()
        popup.save.clicked.connect(lambda: self.close_matrix_popup(popup))

    def open_popup_results(self, model, Controller):
        self.resultView = PU.TextWindow(model, Controller, None)
        self.resultView.show()

    def open_popup_error(self, msg):
        if hasattr(self, "popup"):
            self.popup.text_browser.append(f"\n{msg}")
        else:
            self.popup = PU.TextWindow(None, None, msg)
            self.popup.show()

    def present_inputs(self, ind):
        if ind == 5:
            self.save_all_inputs()
            iterator = QW.QTreeWidgetItemIterator(self.ui.input_tree)
            while iterator.value():
                item = iterator.value()
                if item.text(0) in self.finalInputs:
                    item.setText(1, self.finalInputs[item.text(0)])
                if item.text(0) == 'Data':
                    item.setExpanded(True)
                if item.text(0) == 'Plotting':
                    item.setExpanded(True)
                if item.text(0) == 'Algorithms':
                    algorithm_pointer = item
                if item.text(0) == 'GLA':
                    GLA_pointer = item
                    if self.ui.GLA_radio.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setHidden(True)
                if item.text(0) == 'GTA':
                    GTA_pointer = item
                    if GLA_pointer.isHidden() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setHidden(True)
                if item.text(0) == 'Preset Model':
                    if self.ui.GTA_radio_preset_model.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setExpanded(False)
                        item.setHidden(True)
                elif item.text(0) == 'Custom Model':
                    if self.ui.GTA_radio_custom_model.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setExpanded(False)
                        item.setHidden(True)
                elif item.text(0) == 'Custom Matrix':
                    if self.ui.GTA_radio_custom_matrix.isChecked() is True:
                        item.setExpanded(True)
                        item.setHidden(False)
                    else:
                        item.setExpanded(False)
                        item.setHidden(True)
                iterator += 1
            if self.radios.checkedId() == -1:
                GLA_pointer.setHidden(True)
                GTA_pointer.setHidden(True)
            algorithm_pointer.setExpanded(True)

#####################################INTRO#####################################

    def create_theme(self):
        darkmode = QPalette()
        darkmode.setColor(darkmode.Window, QColor(53, 53, 53))
        darkmode.setColor(darkmode.WindowText, QColor(255,255,255))
        darkmode.setColor(darkmode.Base, QColor(25, 25, 25))
        darkmode.setColor(darkmode.AlternateBase, QColor(53, 53, 53))
        darkmode.setColor(darkmode.ToolTipBase, QColor(0,0,0))
        darkmode.setColor(darkmode.ToolTipText, QColor(255,255,255))
        darkmode.setColor(darkmode.Text, QColor(255,255,255))
        darkmode.setColor(darkmode.Button, QColor(53, 53, 53))
        darkmode.setColor(darkmode.ButtonText, QColor(255,255,255))
        darkmode.setColor(darkmode.BrightText, QColor(0,255,0))
        darkmode.setColor(darkmode.Link, QColor(42, 130, 218))
        darkmode.setColor(darkmode.Highlight, QColor(42, 130, 218))
        darkmode.setColor(darkmode.HighlightedText, QColor(0,0,0))
        self.darkmode = [darkmode, "active"]
        app.setPalette(self.darkmode[0])

    def change_theme(self):
        if self.darkmode[1] == "active":
            app.setPalette(self.default_palette)
            self.darkmode[1] = "inactive"
        else:
            app.setPalette(self.darkmode[0])
            self.darkmode[1] = "active"

    def options(self):
        self.settings_manager = SET.SettingsManager()

#####################################PICKLE####################################

    def save_all_inputs(self):
        self.finalInputs.clear()
        self.finalInputs['Lower Delay/Time Bound'] = self.ui.Data_delay_input_lb.text()
        self.finalInputs['Upper Delay/Time Bound'] = self.ui.Data_delay_input_ub.text()
        self.finalInputs['Lower Wavelength/Field Bound'] = self.ui.Data_wavelength_input_lb.text()
        self.finalInputs['Upper Wavelength/Field Bound'] = self.ui.Data_wavelength_input_ub.text()
        self.finalInputs['Data Multiplier'] = self.ui.Data_input_multiplier.text()
        self.finalInputs['Directory'] = self.ui.Data_directory.text()
        self.finalInputs['Lower Tau Bounds'] = self.ui.GTA_input_tau_lb.text()
        self.finalInputs['Upper Tau Bounds'] = self.ui.GTA_input_tau_ub.text()
        self.finalInputs['x-Axis'] = self.ui.plot_xAxis.text()
        self.finalInputs['y-Axis'] = self.ui.plot_yAxis.text()
        self.finalInputs['z-Axis'] = self.ui.plot_zAxis.text()
        if self.ui.GLA_radio.isChecked() is True:
            self.finalInputs['GLA'] = ""
            self.finalInputs['Optimizer'] = self.ui.GLA_algorithm_optimize.currentText()
            self.finalInputs['Taus'] = str(self.prepare_parameter("gla")).replace("True", "Vary").replace("False", "Fix")
            self.finalInputs['Tau Cache'] = str([tau[0] for tau in self.prepare_parameter("gla")])
            self.finalInputs['Buttons'] = self.prepare_parameter("gla")
        if self.ui.GTA_radio_preset_model.isChecked() is True:
            self.finalInputs['Preset Model'] = ""
            self.finalInputs['Concentrations'] = self.ui.GTA_input_concentration.text()
            self.finalInputs['Model'] = self.ui.GTA_preset_model_selection.currentText()
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Taus'] = str(self.prepare_parameter("preset")).replace("True", "Vary").replace("False", "Fix")
            self.finalInputs['Tau Cache'] = str([tau[0] for tau in self.prepare_parameter("preset")])
            self.finalInputs['Buttons'] = self.prepare_parameter("preset")
            self.finalInputs['Preset Model Index'] = self.ui.GTA_preset_model_selection.currentIndex() + 1
        if self.ui.GTA_radio_custom_model.isChecked() is True:
            self.finalInputs['Custom Model'] = ""
            self.finalInputs['Concentrations'] = self.ui.GTA_input_concentration.text()
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Model'] = self.ui.GTA_input_custom_model_equation.text()
            self.finalInputs['Taus'] = str(self.prepare_parameter("custom")).replace("True", "Vary").replace("False", "Fix")
            self.finalInputs['Tau Cache'] = str([tau[0] for tau in self.prepare_parameter("custom")])
            self.finalInputs['Buttons'] = self.prepare_parameter("custom")
            self.finalInputs['Saved Models'] = [self.ui.GTA_input_custom_model_saved_equations.itemText(i) for i in range(self.ui.GTA_input_custom_model_saved_equations.count())]
        if self.ui.GTA_radio_custom_matrix.isChecked() is True:
            self.finalInputs['Custom Matrix'] = ""
            self.finalInputs['Optimizer'] = self.ui.GTA_algorithm_optimize.currentText()
            self.finalInputs['Initial Value Problem Solver'] = self.ui.GTA_algorithm_initial_value_problem.currentText()
            self.finalInputs['Concentrations'] = self.ui.GTA_input_concentration.text()
            if hasattr(self, "custom_Matrix"):
                self.finalInputs['Matrix'] = str(self.custom_Matrix)
            else:
                self.finalInputs['Matrix'] = "Missing Input."
        self.finalInputs['Selected Plots'] = ""
        if self.ui.plot_das_sas.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', DAS/SAS'
        if self.ui.plot_delay_slices.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Delay/Time Slices'
        if self.ui.plot_heatmap.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Heatmap'
        if self.ui.plot_wavelength_slices.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Wavelength/Field Slices'
        if self.ui.plot_concentrations.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Concentrations'
        if self.ui.plot_residuals.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Residuals'
        if self.ui.plot_three_in_one.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', Three In One'
        if self.ui.plot_threed_contour.isChecked() is True:
            self.finalInputs['Selected Plots'] += ', 3D Contour'
        self.finalInputs['Vmin'] = self.ui.plot_input_vmin.text()
        self.finalInputs['Vmax'] = self.ui.plot_input_vmax.text()
        self.finalInputs['Contour Lines'] = str(self.get_user_contour())
        self.finalInputs['Delay/Time Slices'] = self.ui.plot_input_delay_slices.text()
        self.finalInputs['Wavelength/Field Slices'] = self.ui.plot_input_wavelength_slices.text()
        self.finalInputs['Selected Plots'] = self.finalInputs['Selected Plots'][2:]

    def save_pickle(self):
        if hasattr(self, 'Controller') is True:
            self.Controller.pickleData(self.finalInputs)

    def get_pickle(self):
        if hasattr(self, 'Controller') is False:
            self.Controller = Cont.Controller(self.getFolderPath())
        self.shelf = self.Controller.get_pickle()

    def set_pickle(self):
        self.get_pickle()
        if "Custom Model" in self.shelf:
            models = self.shelf["Saved Models"]
            for i in range(len(models)):
                self.ui.GTA_input_custom_model_saved_equations.addItem(models[i])
        if "Custom Matrix" in self.shelf:
            self.custom_Matrix = self.shelf["Matrix"]
        if "Buttons" in self.shelf:
            buttons = self.shelf["Buttons"]
        for key in self.shelf:
            val = str(self.shelf[key])
            val = val.replace("[", "")
            val = val.replace("]", "")
            val = val.replace("None", "")
            val = val.replace(" ", "")
            if key == "Data Multiplier":
                self.ui.Data_input_multiplier.setText(val)
            if key == "Lower Delay/Time Bound":
                self.ui.Data_delay_input_lb.setText(val)
            if key == "Upper Delay/Time Bound":
                self.ui.Data_delay_input_ub.setText(val)
            if key == "Lower Wavelength/Field Bound":
                self.ui.Data_wavelength_input_lb.setText(val)
            if key == "Upper Wavelength/Field Bound":
                self.ui.Data_wavelength_input_ub.setText(val)
            if key == "Lower Tau Bounds":
                self.ui.GTA_input_tau_lb.setText(val)
            if key == "Upper Tau Bounds":
                self.ui.GTA_input_tau_ub.setText(val)
            if key == "GLA":
                self.ui.GLA_radio.setChecked(True)
            if key == "Preset Model":
                self.ui.GTA_radio_preset_model.setChecked(True)
            if key == "Custom Model":
                self.ui.GTA_radio_custom_model.setChecked(True)
            if key == "Custom Matrix":
                self.ui.GTA_radio_custom_matrix.setChecked(True)
            if self.ui.GLA_radio.isChecked() is True:
                if key == "Tau Cache":
                    self.ui.GLA_input_tau.setText(val)
                if key == "Buttons":
                    for button in buttons:
                        radio = QW.QRadioButton(str(button[0]), autoExclusive=False)
                        radio.setChecked(not bool(button[1]))
                        self.ui.GLA_fix_layout.addWidget(radio)
            if self.ui.GTA_radio_preset_model.isChecked() is True:
                if key == "Preset Model Index":
                    self.ui.GTA_preset_model_selection.setCurrentIndex(int(val) - 1)
                if key == "Tau Cache":
                    self.ui.GTA_input_preset_model_tau.setText(val)
                if key == "Buttons":
                    for button in buttons:
                        radio = QW.QRadioButton(str(button[0]), autoExclusive=False)
                        radio.setChecked(not bool(button[1]))
                        self.ui.GTA_preset_model_fix_layout.addWidget(radio)
            if self.ui.GTA_radio_custom_model.isChecked() is True:
                if key == "Model":
                    self.ui.GTA_input_custom_model_equation.setText(val)
                if key == "Tau Cache":
                    self.ui.GTA_input_custom_model_tau.setText(val)
                if key == "Buttons":
                    for button in buttons:
                        radio = QW.QRadioButton(str(button[0]), autoExclusive=False)
                        radio.setChecked(not bool(button[1]))
                        self.ui.GTA_custom_model_fix_layout.addWidget(radio)
            if key == "Concentrations":
                self.ui.GTA_input_concentration.setText(val)
            if key == "Delay/Time Slices":
                self.ui.plot_input_delay_slices.setText(val)
            if key == "Wavelength/Field Slices":
                self.ui.plot_input_wavelength_slices.setText(val)
            if key == "Contour Lines":
                self.ui.plot_input_contour.setValue(int(val))
            if key == "Vmin":
                self.ui.plot_input_vmin.setText(val)
            if key == "Vmax":
                self.ui.plot_input_vmax.setText(val)

    def clear_pickle(self):
        for lineedit in self.findChildren(QW.QLineEdit):
            if lineedit != self.ui.Data_directory:
                lineedit.clear()
        for spinbox in self.findChildren(QW.QSpinBox):
            spinbox.setValue(0)
        for combobox in self.findChildren(QW.QComboBox):
            combobox.setCurrentIndex(0)
        if hasattr(self, 'cm') is True:
            self.cm = None
def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    report_dir = "crashreports"
    if not os.path.exists(f"{os.getcwd()}/{report_dir}"):
        os.mkdir(report_dir)
    global file
    file = f"{os.getcwd()}/{report_dir}/CRASH_{datetime.now().strftime('%Y%m%dT%H%M%S')}.log"
    handler = logging.FileHandler(file, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def exception_hook(exc_type, exc_value, exc_traceback):
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    msg = QW.QMessageBox()
    msg.setIcon(QW.QMessageBox.Critical)
    msg.setWindowTitle("Error")
    msg.setText(f"An unexpected error occured and the program will terminate.\nThe crash report can be found here:\n{file}")
    msg.setDetailedText(f"Error type: {exc_type.__name__}\n{exc_value}")
    msg.exec_()
    sys.exit(1)

class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():
            self.logger.log(self.level, message)

    def flush(self):
        pass

if __name__ == '__main__':
    import sys
    logger = setup_logger()
    logging.info("Program started.")
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
    sys.excepthook = exception_hook
    if not QW.QApplication.instance():
        app = QW.QApplication(sys.argv)
    else:
        app = QW.QApplication.instance()
    app.setStyle('Fusion')
    mainwindow = MainWindow()
    app.setQuitOnLastWindowClosed(True)
    mainwindow.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical("Critical error while closing the program!", exc_info=e)
