from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QFileDialog, QInputDialog, QScrollArea, QDialog, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os
from directory_tree import DirectoryTree
from foldercleaner import organiseFiles, loadConfiguration, deleteDuplicatesFolder, get_file_type_statistics

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Files")
        self.resize(700, 500)

        #Searchbar
        self.searchTerm = QLineEdit()
        self.searchTerm.setPlaceholderText("Enter search term...")

        #Search button
        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.search_files)

        #Result table
        self.resultTable = QTableWidget()
        self.resultTable.setColumnCount(2)
        self.resultTable.setHorizontalHeaderLabels(["File Name", "File Path"])
        self.resultTable.resize(200, 200)

        layout = QVBoxLayout()
        layout.addWidget(self.searchTerm)
        layout.addWidget(self.searchButton)
        layout.addWidget(self.resultTable)

        self.setLayout(layout)
    #Searching for files
    def search_files(self):
        term = self.searchTerm.text()
        if not term:
            QMessageBox.warning(self, "Input Error", "Please enter a search term.")
            return

        root_path = self.parent().lineEdit.text()
        results = []

        for root, dirs, files in os.walk(root_path):
            for file in files:
                if term.lower() in file.lower():
                    results.append((file, os.path.join(root, file)))

        self.resultTable.setRowCount(len(results))
        for row, (file_name, file_path) in enumerate(results):
            self.resultTable.setItem(row, 0, QTableWidgetItem(file_name))
            self.resultTable.setItem(row, 1, QTableWidgetItem(file_path))

class Widget(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("TidyPC")

        # Set the window size
        self.resize(1200, 300)

        # Create a label and line edit for user to input the path
        label = QLabel("Insert the path to the desired folder here: ")
        self.lineEdit = QLineEdit()

        # Set the font size for the label and line edit
        font = QFont()
        font.setPointSize(14)
        self.lineEdit.setFont(font)
        label.setFont(font)

        # Create a button to delete the duplicates
        deleteDuplicates = QPushButton("Delete Duplicates")
        deleteDuplicates.clicked.connect(self.delete_duplicates)
        
        # Create a button to organise the folder
        organiseFolder = QPushButton("Organise")
        organiseFolder.clicked.connect(self.organise_folder)

        # Create a button to clear the path
        clearPath = QPushButton("Clear")
        clearPath.clicked.connect(self.clear_path)

        # Create a button to browse for the source folder
        browseButton = QPushButton("Browse")
        browseButton.clicked.connect(self.browse)
        
        # Create a button to show the directory tree
        showDirectoryTree = QPushButton("Show Directory Tree")
        showDirectoryTree.clicked.connect(self.show_directory_tree)
        
        # Create a button to search files
        searchFiles = QPushButton("Search Files")
        searchFiles.clicked.connect(self.open_search_dialog)
        
        self.statisticsLabel = QLabel()
        self.statisticsLabel.setWordWrap(True)
        self.lineEdit.returnPressed.connect(self.update_file_statistics)
        
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.statisticsLabel)

        # Create horizontal layouts for the label + line edit and the buttons
        hLayout1 = QHBoxLayout()
        hLayout1.addWidget(label)
        hLayout1.addWidget(self.lineEdit)
        hLayout1.addWidget(browseButton)
        
        hLayout2 = QHBoxLayout()
        hLayout2.addWidget(organiseFolder)
        hLayout2.addWidget(clearPath)
        hLayout2.addWidget(deleteDuplicates)
        hLayout2.addWidget(showDirectoryTree)
        hLayout2.addWidget(searchFiles)

        # Create a vertical layout and add the horizontal layouts to it
        vLayout = QVBoxLayout()
        vLayout.setSpacing(10)
        vLayout.addLayout(hLayout1)
        vLayout.addLayout(hLayout2)
        vLayout.addWidget(scrollArea)

        # Set the layout for the widget
        self.setLayout(vLayout)

    def organise_folder(self):
        path = self.lineEdit.text()
        config = loadConfiguration("config.json")
        try:
            organiseFiles(self, path, config)
            QMessageBox.information(self, "Success", "Folder organised successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        self.update_file_statistics()

    def clear_path(self):
        self.lineEdit.clear()

    def delete_duplicates(self):
        path = self.lineEdit.text()
        if deleteDuplicatesFolder(path):
            QMessageBox.information(self, "Success", "Duplicates folder deleted.")
        else:
            QMessageBox.information(self, "Error", "Failed to delete the Duplicates folder.")
    
    def browse(self):
        folderPath = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folderPath:
            self.lineEdit.setText(folderPath)
            self.update_file_statistics()

    def show_directory_tree(self):
        self.directory_tree = DirectoryTree()
        self.directory_tree.set_directory(self.lineEdit.text())
        self.directory_tree.show()

    def update_file_statistics(self, top_n=10):
        path = self.lineEdit.text()
        file_type_statistics = get_file_type_statistics(path)
        file_type_statistics = dict(sorted(file_type_statistics.items(), key=lambda item: item[1], reverse=True)[:top_n])
        stats_msg = ", ".join(f"{file_type if file_type else 'none'} : {count}" for file_type, count in file_type_statistics.items())
        stats_msg = f"Statistics:\n{stats_msg}"
        self.statisticsLabel.setText(stats_msg)

    def open_search_dialog(self):
        self.search_dialog = SearchDialog(self)
        self.search_dialog.exec()
