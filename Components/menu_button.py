from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon


class rMenuButton(QPushButton):
    def __init__(self, text, index):
        super().__init__(text)
        self.setFixedHeight(40)

        self.setIcon(QIcon(f"./Resource/image/menu_btn{index}.png"))

    def set_selectedStyle(self, isSelected):
        """切换按钮选中状态"""
        if isSelected:
            self.setStyleSheet(self.selectedStyle)
        else:
            self.setStyleSheet(self.defaultStyle)