
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QSizePolicy


class ExpandableQuestion(QWidget):
    """可展开的问答组件，支持自定义答案区域"""

    def __init__(self, question: str, answer_widget: QWidget, parent=None):
        super().__init__(parent)
        self.answer_visible = False  # 记录是否展开
        # self.setFixedWidth(500)  # 控制整体宽度

        # 1️⃣ 竖向布局（包含问题按钮 + 答案区域）
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # 2️⃣ 问题按钮
        self.question_button = QPushButton(question)
        self.question_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                font-size: 16px;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        self.question_button.clicked.connect(self.toggle_answer)
        self.layout.addWidget(self.question_button)

        # 3️⃣ 回答区域（初始隐藏）
        self.answer_area = QFrame()
        self.answer_area.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 10px;
        """)
        self.answer_area.setFixedHeight(0)  # 初始隐藏

        # ⬇️ 允许传入 **任意 QWidget 作为答案区域**
        self.answer_widget = answer_widget
        # self.answer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        answer_layout = QVBoxLayout(self.answer_area)
        answer_layout.addWidget(self.answer_widget)
        self.layout.addWidget(self.answer_area)

        # 4️⃣ 动画
        self.animation = QPropertyAnimation(self.answer_area, b"maximumHeight")
        self.animation.setDuration(500)

    def toggle_answer(self):
        """展开或收起答案"""
        if self.answer_visible:
            self.animation.setStartValue(self.answer_area.maximumHeight())
            self.animation.setEndValue(0)
            self.answer_visible = False
        else:
            # **💡 更新内容大小，确保 `QWidget` 计算高度正确**
            self.answer_widget.adjustSize()
            content_height = self.answer_widget.height() + 20  # 额外加点 padding
            self.animation.setStartValue(0)
            self.animation.setEndValue(content_height)
            self.answer_visible = True

        self.animation.start()
