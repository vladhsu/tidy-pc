from PySide6.QtWidgets import QTreeView, QVBoxLayout, QPushButton, QWidget, QFileDialog
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileSystemModel

class DirectoryTree(QWidget):
    def __init__(self, directory=''):
        super().__init__()

        self.setWindowTitle("Directory Tree")
        self.resize(800, 600)

        self.model = QFileSystemModel()
        self.model.setRootPath('')

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.clicked.connect(self.open_file)

        self.button = QPushButton("Choose Directory")
        self.button.clicked.connect(self.choose_directory)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.tree)

        self.setLayout(layout)

        if directory:
            self.set_directory(directory)

    def choose_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose Directory")
        self.set_directory(directory)

    def set_directory(self, directory):
        if directory:
            self.model.setRootPath(directory)
            self.tree.setRootIndex(self.model.index(directory))

    def open_file(self, index):
        file_path = self.model.filePath(index)
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
