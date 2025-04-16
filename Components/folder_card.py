import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize
from Utils.path_resolver import resource_path


class FolderIconWidget(QWidget):
    def __init__(self, folder_path: str, folder_name: str, icon_path: str, is_new: bool, parent=None):
        super().__init__(parent)
        self.folder_path = os.path.abspath(folder_path)
        self.folder_name = folder_name

        self.setFixedSize(120, 120)
        if is_new:
            self.setStyleSheet("""
                FolderIconWidget {
                    border: 1px solid #f0faff;
                    border-radius: 10px;
                    background-color: #cbe8f6;
                }
                FolderIconWidget:hover {
                    background-color: #cbe8f6;
                    border: 1px solid #85c1e9;
                }
            """)
        else :
            self.setStyleSheet("""
                FolderIconWidget {
                    border: 1px solid #d0d0d0;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }
                FolderIconWidget:hover {
                    background-color: #cbe8f6;
                    border: 1px solid #85c1e9;
                }
            """)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setToolTip(self.folder_name)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        # 图标按钮
        self.icon_button = QPushButton()
        self.icon_button.setIcon(QIcon(icon_path))
        self.icon_button.setIconSize(QSize(80, 80))
        self.icon_button.setFlat(True)
        self.icon_button.setCursor(Qt.PointingHandCursor)
        self.icon_button.clicked.connect(self.open_folder)
        self.icon_button.setStyleSheet("QPushButton { border: none; }")

        # 标签
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignLeft)
        self.name_label.setMaximumWidth(140)
        self.name_label.setStyleSheet("font-size: 13px;")
        self.name_label.setWordWrap(False)
        self.name_label.setFixedHeight(30)

        # 设置省略文本 + tooltip
        metrics = self.name_label.fontMetrics()
        elided_text = metrics.elidedText(folder_name, Qt.ElideRight, 130)
        self.name_label.setText(elided_text)
        self.name_label.setToolTip(folder_name)

        layout.addWidget(self.icon_button)
        layout.addWidget(self.name_label)

    def open_folder(self):
        self.setStyleSheet("""
                        FolderIconWidget {
                            border: 1px solid #d0d0d0;
                            border-radius: 10px;
                            background-color: #f9f9f9;
                        }
                        FolderIconWidget:hover {
                            background-color: #cbe8f6;
                            border: 1px solid #85c1e9;
                        }
                    """)
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        if sys.platform.startswith("win"):
            os.startfile(self.folder_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", self.folder_path])
        else:
            subprocess.Popen(["xdg-open", self.folder_path])


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folder Icon Demo")
        self.resize(600, 200)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 示例文件夹
        folders = [
            ("./downloads", "下载", resource_path("./Resource/image/file.png")),
            ("./very_long_named_folder_example", "这是一个名字很长的文件夹示例用来测试显示效果", resource_path("./Resource/image/file.png")),
            ("./logs", "日志", resource_path("./Resource/image/file.png"))
        ]

        for path, name, icon in folders:
            widget = FolderIconWidget(path, name, icon)
            layout.addWidget(widget)


if __name__ == "__main__":
    app = QApplication([])

    window = DemoWindow()
    window.show()

    app.exec()
