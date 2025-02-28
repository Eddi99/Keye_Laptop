from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
import sys

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meine PyQt GUI")
        self.setGeometry(100, 100, 300, 200)

        button = QPushButton("Klick mich!", self)
        button.clicked.connect(self.show_message)
        button.move(100, 80)

    def show_message(self):
        QMessageBox.information(self, "Info", "Hallo, Welt!")

app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec())
