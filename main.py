import sys
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from ui.main_window import MainWindow
from Utils.path_resolver import resource_path

if __name__ == "__main__":
    app = QApplication([])
    splash = QSplashScreen(QPixmap(resource_path('./Resource/image/logo.png')))
    splash.show()

    main_window = MainWindow()
    main_window.show()

    splash.finish(main_window)
    app.exec()
