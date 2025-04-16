import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize
from qfluentwidgets import PrimaryPushButton, PickerBase, PushButton

from Utils.path_resolver import resource_path

class ToolCardWidget(QFrame):
    def __init__(self, icon_path: str, control_layout: QVBoxLayout, description: str, parent=None):
        super().__init__(parent)

        self.setFixedSize(320, 160)
        self.setObjectName("ToolCardWidget")
        self.setStyleSheet("""
            ToolCardWidget {
                border: 1px solid #d0d0d0;
                border-radius: 12px;
                background-color: #ffffff;
            }
            ToolCardWidget:hover {
                border: 1px solid #85c1e9;
                background-color: #f0faff;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)

        main_layout = QVBoxLayout(self)

        up_layout = QHBoxLayout()
        # 图标
        icon_btn = QPushButton()
        icon_btn.setIcon(QIcon(icon_path))
        icon_btn.setIconSize(QSize(100, 100))
        icon_btn.setFixedSize(100, 100)
        icon_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                background-color: #fafafa;
            }
        """)
        icon_btn.setCursor(Qt.PointingHandCursor)
        up_layout.addWidget(icon_btn)

        # 控件 layout (传入的)
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        up_layout.addWidget(control_widget)

        # 描述 label
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #555; font-size: 13px;")

        main_layout.addLayout(up_layout)
        main_layout.addWidget(desc_label)

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("工具卡片演示")
        self.resize(600, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 工具控件 layout（例如有两个按钮）
        tool_layout = QVBoxLayout()
        tool_layout.setContentsMargins(0, 0, 0, 0)
        btn1 = PushButton(text="执行")
        btn2 = PushButton(text="设置")
        tool_layout.addWidget(btn1)
        # tool_layout.addWidget(btn2)

        # 创建卡片
        card = ToolCardWidget(
            icon_path=resource_path("./Resource/image/tampermonkey.png"),
            control_layout=tool_layout,
            description="这是一个功能强大的工具卡片，支持快速设置并执行相关操作。"
        )

        layout.addWidget(card)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DemoWindow()
    win.show()
    sys.exit(app.exec())


