# -*- coding: utf-8 -*-
"""
GUI classes and methods.
"""
import os
import logging
from logging.handlers import QueueHandler
import multiprocessing
from PyQt5.QtWidgets import QPushButton, \
    QMainWindow, QDialog, QFileDialog, QMessageBox, QLabel, QHBoxLayout, \
    QWidget, QComboBox, QGridLayout, QCheckBox, QVBoxLayout, QLineEdit
from PyQt5.QtCore import QDir
import pandas as pd
import erya_resource as eryaR

class MainWindow(QMainWindow):
    """
    Main window class
    """

    def __init__(self, log_queue: QueueHandler, log_process: multiprocessing.Process,
                 logger: logging.Logger):
        """
        MainWindow class constructor.

        Parameters
        ----------
        log_queue : logging.QueueHandler()
            Shared logging queue that will be passed to subprocesses.
        log_process : multiprocessing.Process
            Logging process required to ensure proper closing before app exiting.

        Returns
        -------
        None.

        """
        #Parent class constructor
        super().__init__()

        #Window characteristics
        self.setWindowTitle("ERYA Tool®")
        self.setMinimumSize(200, 200)
        #Multiprocessing queue to communicate with secondary processes
        self.comm_queue = multiprocessing.Queue()

        #Additional windows
        self.resource_window = None

        #Logging object that will be used by class methods
        self.log_queue = log_queue
        self.log_process = log_process
        self.logger = logger
        
        #Layout
        centralwidget = QWidget(self)
        self.setCentralWidget(centralwidget)
        window_layout = QVBoxLayout(centralwidget)
        self.columns_layout = QHBoxLayout()
        window_layout.addLayout(self.columns_layout)
        self.general_layout = QGridLayout()
        self.columns_layout.addLayout(self.general_layout)
        self.tools_layout = QVBoxLayout()
        self.columns_layout.addLayout(self.tools_layout)
        self.utilities_layout = QHBoxLayout()
        window_layout.addLayout(self.utilities_layout)
        
        #Buttons
        self.fill_general_layout()
        self.fill_tools_layout()
        self.fill_utilities_layout()
        
    def fill_general_layout(self):
        self.name_label = QLabel("Project Name", self)
        self.name_qline = QLineEdit("", self)
        self.code_label = QLabel("Project Code", self)
        self.code_qline = QLineEdit("", self)
        self.lat_label = QLabel("Latitude", self)
        self.lat_qline = QLineEdit("", self)
        self.lon_label = QLabel("Longitude", self)
        self.lon_qline = QLineEdit("", self)
        self.alt_label = QLabel("Altitude", self)
        self.alt_qline = QLineEdit("", self)
        
        self.general_layout.addWidget(self.name_label,0,0)
        self.general_layout.addWidget(self.name_qline,0,1)
        self.general_layout.addWidget(self.code_label,1,0)
        self.general_layout.addWidget(self.code_qline,1,1)
        self.general_layout.addWidget(self.lat_label,2,0)
        self.general_layout.addWidget(self.lat_qline,2,1)
        self.general_layout.addWidget(self.lon_label,3,0)
        self.general_layout.addWidget(self.lon_qline,3,1)
        self.general_layout.addWidget(self.alt_label,4,0)
        self.general_layout.addWidget(self.alt_qline,4,1)
        
    def fill_tools_layout(self):
        self.resource_button = QPushButton("Resource Analysis", self)
        self.resource_button.clicked.connect(self.resource_button_clicked)
        
        self.string_button = QPushButton("String length calc", self)
        self.site_button = QPushButton("Site description", self)
        self.plant_button = QPushButton("Plant equipment", self)
        self.yield_button = QPushButton("Yield analysis", self)
        
        self.tools_layout.addWidget(self.resource_button)
        self.tools_layout.addWidget(self.string_button)
        self.tools_layout.addWidget(self.site_button)
        self.tools_layout.addWidget(self.plant_button)
        self.tools_layout.addWidget(self.yield_button)
    
    def fill_utilities_layout(self):
        self.reset_button = QPushButton("Reset inputs")
        self.utilities_layout.addWidget(self.reset_button)
        self.reset_button.clicked.connect(self.reset_button_clicked)
        
    def resource_button_clicked(self):
        try:
            if (self.resource_window is None) and (self.check_resource_inputs() is True):
                self.make_inputs_non_editable()
                self.resource_window = ResourceWindow(self.logger, {"latitude": self.lat_qline.text(),
                    "longitude": self.lon_qline.text(),"altitude": self.alt_qline.text()})
                self.resource_window.show()
            elif (self.resource_window is not None) and (self.check_resource_inputs() is True):
                self.resource_window.show()
        except (TypeError, OSError):
            self.log_queue.put("Error when creating resource window")
            error_window("Error when creating resource window",
                "The program was unable to start the resource window")
    
    def check_resource_inputs(self):
        if (self.name_qline.text() == ""):
            error_window("Input not found", "Please fill project name")
            return False
        if(self.code_qline.text() == ""):
            error_window("Input not found", "Please fill project code")
            return False
        if(self.lat_qline.text() == ""):
            error_window("Input not found", "Please fill latitude field")
            return False
        if(float(self.lat_qline.text()) > 90) or (float(self.lat_qline.text()) < -90):
            error_window("Incorrect input format", "Latitude must be inside (-90,90) interval")
            return False
        if(self.lon_qline.text() == ""):
            error_window("Input not found", "Please fill longitude field")
            return False
        if(float(self.lon_qline.text()) > 180) or (float(self.lon_qline.text()) < -180):
            error_window("Incorrect input format", "Longitude must be inside (-180,180) interval")
            return False
        if(self.alt_qline.text() == ""):
            error_window("Input not found", "Please fill altitude field")
            return False
        if(float(self.alt_qline.text()) > 3000) or (float(self.alt_qline.text()) < 0):
            error_window("Incorrect input format", "Altitude must be inside (0,3000) masl interval")
            return False
        return True
    
    def make_inputs_non_editable(self):
        self.name_qline.setReadOnly(True)
        self.code_qline.setReadOnly(True)
        self.lat_qline.setReadOnly(True)
        self.lon_qline.setReadOnly(True)
        self.alt_qline.setReadOnly(True)
    
    def reset_button_clicked(self):
        self.name_qline.setReadOnly(False)
        self.code_qline.setReadOnly(False)
        self.lat_qline.setReadOnly(False)
        self.lon_qline.setReadOnly(False)
        self.alt_qline.setReadOnly(False)
        if self.resource_window is not None:
            self.resource_window.deleteLater()
            self.resource_window = None
    

    def closeEvent(self,event):
        """
        Event to be triggered when X button is pressed.

        Parameters
        ----------
        event : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        #Ensures logging processes are properly closed
        self.log_queue.put(None)
        self.log_process.join(5)
        logging.shutdown()

        #Closes the window
        self.close()

class ResourceWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, logger: logging.Logger, project_geo: dict):
        super().__init__()
        self.setWindowTitle("Resource estimation")
        self.logger = logger
        self.lat = float(project_geo["latitude"])
        self.lon = float(project_geo["longitude"])
        self.alt = float(project_geo["altitude"])
        self.databases = ["Solargis - Monthly Averages", "Solargis - TMY",
            "Solargis - Historic", "Meteonorm - TMY", "PVGIS - TMY", "NASA - TMY",
            "NREL - Historic", "SolarAnywhere - TMY", "SiAR - Monthly Averages",
            "Other"]
        self.number_of_databases = 10
        widget_types = ["QC", "QL", "QPB", "QCB1", "QCB2"]
        dataframe_list = [number for number in range(self.number_of_databases)]
        self.widgets = {new_list: [] for new_list in widget_types}
        self.dataframes = {new_df: pd.DataFrame for new_df in  dataframe_list}

        #Init layouts
        self.outer_layout = QVBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.horizontal_layout = QHBoxLayout()
        self.grid_layout = QGridLayout()
        #Layout structure
        self.setLayout(self.outer_layout)
        self.left_layout.addLayout(self.grid_layout)
        self.left_layout.addLayout(self.horizontal_layout)
        self.outer_layout.addLayout(self.left_layout)
        self.outer_layout.addLayout(self.right_layout)
        #Layout configuration
        self.configure_grid_layout()
        self.configure_horizontal_layout()

    def load_button_clicked(self):
        if self.sender() is self.widgets["QPB"][0]:
            self.obtain_data_per_button(0)
        elif self.sender() is self.widgets["QPB"][1]:
            self.obtain_data_per_button(1)
        elif self.sender() is self.widgets["QPB"][2]:
            self.obtain_data_per_button(2)
        elif self.sender() is self.widgets["QPB"][3]:
            self.obtain_data_per_button(3)
        elif self.sender() is self.widgets["QPB"][4]:
            self.obtain_data_per_button(4)
        elif self.sender() is self.widgets["QPB"][5]:
            self.obtain_data_per_button(5)
        elif self.sender() is self.widgets["QPB"][6]:
            self.obtain_data_per_button(6)
        elif self.sender() is self.widgets["QPB"][7]:
            self.obtain_data_per_button(7)
        elif self.sender() is self.widgets["QPB"][8]:
            self.obtain_data_per_button(8)
        elif self.sender() is self.widgets["QPB"][9]:
            self.obtain_data_per_button(9)

    def obtain_data_per_button(self, i: int):
        try:
            if self.widgets["QC"][i].currentText() == "PVGIS - TMY":
                self.dataframes[i] = eryaR.read_solar_data_file(
                    "NoFile", self.widgets["QC"][i].currentText(), self.logger,
                    self.lat, self.lon)
                self.widgets["QL"][i].setText("Loaded")
                self.widgets["QCB1"][i].setChecked(True)
                self.widgets["QCB2"][i].setChecked(True)
            else:
                self.dataframes[i] = eryaR.read_solar_data_file(
                    file_dialog(os.getcwd(),is_folder=False),
                    self.widgets["QC"][i].currentText(), self.logger)
                self.widgets["QL"][i].setText("Loaded")
                self.widgets["QCB1"][i].setChecked(True)
                self.widgets["QCB2"][i].setChecked(True)
        except TypeError:
            error_window("Error",
                "Incorrect format file. Please check file contents")
            self.dataframes[i]  = None
            self.widgets["QL"][i].setText("Format error")
            self.widgets["QCB1"][i].setChecked(False)
            self.widgets["QCB2"][i].setChecked(False)
        except FileNotFoundError:
            error_window("Error",
                "The program was unable to select or load the data file")
            self.dataframes[i]  = None
            self.widgets["QL"][i].setText("File error")
            self.widgets["QCB1"][i].setChecked(False)
            self.widgets["QCB2"][i].setChecked(False)
        except ConnectionError:
            error_window("Error",
                "The program was unable to connect to external API")
            self.dataframes[i]  = None
            self.widgets["QL"][i].setText("Connection error")
            self.widgets["QCB1"][i].setChecked(False)
            self.widgets["QCB2"][i].setChecked(False)
        except OSError:
            error_window("Error",
                "Incorrect format file. Please check file contents")
            self.dataframes[i]  = None
            self.widgets["QL"][i].setText("OS Error")
            self.widgets["QCB1"][i].setChecked(False)
            self.widgets["QCB2"][i].setChecked(False)
        except pd.errors.EmptyDataError:
            pass

    def configure_grid_layout(self):
        for i in range (self.number_of_databases):
            self.widgets["QC"].append(QComboBox(self))
            self.widgets["QC"][-1].addItems(self.databases)
            self.widgets["QPB"].append(QPushButton("Load", self))
            self.widgets["QL"].append(QLabel("Inactive", self))
            self.widgets["QCB1"].append(QCheckBox("Include"))
            self.widgets["QCB2"].append(QCheckBox("Print"))
            self.grid_layout.addWidget(self.widgets["QC"][-1], i, 0)
            self.grid_layout.addWidget(self.widgets["QPB"][-1], i, 1)
            self.grid_layout.addWidget(self.widgets["QL"][-1], i, 2)
            self.grid_layout.addWidget(self.widgets["QCB1"][-1], i, 3)
            self.grid_layout.addWidget(self.widgets["QCB2"][-1], i, 4)
            self.widgets["QPB"][-1].clicked.connect(self.load_button_clicked)

    def configure_horizontal_layout(self):
        self.reset_button = QPushButton("Reset")
        self.horizontal_layout.addWidget(self.reset_button)
        self.reset_button = QPushButton("Calculate")
        self.horizontal_layout.addWidget(self.reset_button)
        self.reset_button = QPushButton("Refresh graphics")
        self.horizontal_layout.addWidget(self.reset_button)

def file_dialog(starting_directory: str, for_open: bool=True, fmt: str='', is_folder:bool=False):
    """
    Customized file dialog function.

    Parameters
    ----------
    starting_directory : str
        Directory where the dialog will start.
    for_open : bool, optional
        Defines if the file is to open or save. The default is True.
    fmt : str, optional
        If you must look for a particular file format. The default is ''.
    is_folder : TYPE, optional
        Indicates if looking for file or folder. The default is False.

    Returns
    -------
    str
        Folder of file path selected.

    """
    dialog = QFileDialog()

    #Does not show hidden directories
    dialog.setFilter(dialog.filter() | QDir().Hidden)
    dialog.setDirectory(str(starting_directory))

    # Files / folders
    if is_folder:
        dialog.setFileMode(QFileDialog.DirectoryOnly)
    else:
        dialog.setFileMode(QFileDialog.AnyFile)

    # Opening or saving
    if for_open:
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
    else:
        dialog.setAcceptMode(QFileDialog.AcceptSave)

    # Set a particular format
    if fmt != '' and is_folder is False:
        dialog.setDefaultSuffix(fmt)
        dialog.setNameFilters([f'{fmt} (*.{fmt})'])
    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]  # returns a list
        return path
    return ''

def error_window(title: str, text: str):
    """
    Error window to communicate errors to the user.
    Parameters
    ----------
    title : str
        Window title.
    text : str
        Error text.

    Returns
    -------
    None.

    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("Error")
    msg.setInformativeText(text)
    msg.setWindowTitle(title)
    msg.exec_()
