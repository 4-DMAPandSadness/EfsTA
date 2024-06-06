import PyQt5.QtWidgets as QW
from PyQt5.QtCore import QSettings, pyqtSignal, QObject

class SettingsManager(QObject):
    """Create a settings manager for the SuperChess application."""

    widget_mappers = {
        'QCheckBox': ('checkState', 'setCheckState'),
        'QLineEdit': ('text', 'setText'),
        'QSpinBox': ('value', 'setValue'),
        'QRadioButton': ('isChecked', 'setChecked'),
    }

    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyApp", "settings")

    def update_widgets_from_settings(self, _map):
        for name, widget in _map.items():
            cls = widget.__class__.__name__
            getter, setter = self.widget_mappers.get(cls, (None, None))
            value = self.settings.value(name)
            print("load:", getter, setter, value)
            if setter and value is not None:
                fn = getattr(widget, setter)
                fn(value)  # Set the widget.

    def update_settings_from_widgets(self, _map):
        for name, widget in _map.items():
            cls = widget.__class__.__name__
            getter, setter = self.widget_mappers.get(cls, (None, None))
            print("save:", getter, setter)
            if getter:
                fn = getattr(widget, getter)
                value = fn()
                print("-- value:", value)
                if value is not None:
                    self.settings.setValue(name, value) # Set the settings.

        # Notify watcher of changed settings.
        self.settings_changed.emit()


# Define this in another module, import to use.

class SettingsDialog(QW.QDialog):
    """Create a settings dialog to edit all the settings of the application."""

    def __init__(self):
        super().__init__()

        """Create groups of radio buttons as settings elements."""
        self.stylesheet = QW.QLineEdit(placeholderText="Matplotlib stylesheet")
        self.stylesheet.setClearButtonEnabled(True)
        self.stylesheetlabel = QW.QLabel(text="Stylesheet:")
        
        self.delbound = QW.QLineEdit(text="")
        
        self.wavebound = QW.QLineEdit(text="")
        
        self.corrbound = QW.QLineEdit(text="")
        
        self.taulow = QW.QLineEdit(text="")

        _buttons = QW.QDialogButtonBox.StandardButton
        self.button_box = QW.QDialogButtonBox(_buttons.Ok | _buttons.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        grid_layout = QW.QGridLayout()
        grid_layout.addWidget(self.stylesheetlabel, 0,0)
        grid_layout.addWidget(self.stylesheet, 0,1)
        #grid_layout.addWidget(self.button_box, 1,0)
        self.setLayout(grid_layout)

        self.map = {
            'Stylesheet': self.stylesheet,
        }

        self.load_settings()
        self.accepted.connect(self.save_settings)

    # def load_settings(self):
    #     """ Reload the settings from the settings store """
    #     settings_manager.update_widgets_from_settings(self.map)


    # def save_settings(self):
    #     """ Triggered when the dialog is accepted; copys settings values to the settings manager """
    #     settings_manager.update_settings_from_widgets(self.map)


# class MainWindow(QW.QWidget):

#     def __init__(self):
#         super().__init__()

#         self.button = QW.QPushButton("Press for settings")
#         self.label = QW.QLabel()

#         self.button.pressed.connect(self.edit_settings)

#         settings_manager.settings_changed.connect(self.update_label)
#         self.update_label()

#         layout = QW.QVBoxLayout()
#         layout.addWidget(self.button)
#         layout.addWidget(self.label)
#         self.setLayout(layout)

#     def edit_settings(self):
#         dlg = SettingsDialog()
#         dlg.exec()

#     def update_label(self):
#         data = {
#             'stylesheet': settings_manager.settings.value('stylesheet'),
#         }

#         self.label.setText(str(data))


# app = QW.QApplication([])

# w = MainWindow()
# w.show()

# app.exec()