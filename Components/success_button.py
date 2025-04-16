from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from qfluentwidgets import InfoBar, InfoBarPosition


class SuccessButton(QPushButton):
    def __init__(self, text="Success", parent=None):
        super().__init__(text, parent)
        self.clicked.connect(self.showSuccessMessage)

    def showSuccessMessage(self):
        InfoBar.success(
            title='成功',
            content="账号已添加",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.parent()
        )
