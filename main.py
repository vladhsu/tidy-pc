from PySide6.QtWidgets import QApplication
import sys
from widget import Widget

# Load the QSS file
def load_stylesheet(file_path):
    with open(file_path, "r") as file:
        return file.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load and set the stylesheet
    stylesheet = load_stylesheet("style.qss")
    app.setStyleSheet(stylesheet)

    widget = Widget()
    widget.show()

    sys.exit(app.exec())
