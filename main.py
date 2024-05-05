from PySide6.QtWidgets import QApplication
from widget import Widget

app = QApplication()

with open("style.qss", "r") as file:
    style = file.read()
    app.setStyleSheet(style)

widget = Widget()
widget.show()

app.exec()