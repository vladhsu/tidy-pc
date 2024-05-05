# Import necessary modules from PySide6
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Import necessary functions from foldercleaner module
from foldercleaner import organiseFiles, loadConfiguration

# Define the main Widget class
class Widget(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("TidyPC")

        # Set the window size
        self.resize(900, 200)

        # Create a label and line edit for user to input the path
        label = QLabel("Insert the path to the desired folder here: ")
        self.lineEdit = QLineEdit()

        # Set the font size for the label and line edit
        font = QFont()
        font.setPointSize(14)
        self.lineEdit.setFont(font)
        label.setFont(font)

        # Create a button to organise the folder
        organiseFolder = QPushButton("Organise")
        organiseFolder.clicked.connect(self.organise_folder)  # Connect the button to the organise_folder function

        # Create a button to clear the path
        clearPath = QPushButton("Clear")
        clearPath.clicked.connect(self.clear_path)  # Connect the button to the clear_path function

        # Create horizontal layouts for the label + line edit and the buttons
        hLayout1 = QHBoxLayout()
        hLayout1.addWidget(label)
        hLayout1.addWidget(self.lineEdit)
        
        hLayout2 = QHBoxLayout()
        hLayout2.addWidget(organiseFolder)
        hLayout2.addWidget(clearPath)

        # Create a vertical layout and add the horizontal layouts to it
        vLayout = QVBoxLayout()
        vLayout.setSpacing(10)
        vLayout.addLayout(hLayout1)
        vLayout.addLayout(hLayout2)

        # Set the layout for the widget
        self.setLayout(vLayout)

    # Define the function to organise the folder
    def organise_folder(self):
        path = self.lineEdit.text()  # Get the path from the line edit
        config = loadConfiguration("config.json")  # Load the configuration
        try:
            organiseFiles(path, config)  # Try to organise the files
            QMessageBox.information(self, "Success", "Folder organised successfully!")  # Show a success message
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))  # Show the error message if something goes wrong

    # Define the function to clear the path
    def clear_path(self):
        self.lineEdit.clear()  # Clear the line edit
