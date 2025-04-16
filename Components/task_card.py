from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QTextEdit, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class CardWidget(QWidget):
    def __init__(self, title: str, content_widget: QWidget):
        super().__init__()

        # 创建卡片框架
        self.frame = QFrame(self)
        layout = QVBoxLayout(self.frame)
        self.frame.setObjectName('task')

        # 标题
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName('task_name')
        self.title_label.setMinimumHeight(35)
        self.title_label.setMaximumHeight(35)

        # 布局
        content_widget.setObjectName('task_area')
        layout.addWidget(self.title_label)
        layout.addWidget(content_widget)

        # 样式
        self.setStyleSheet("""
            #task {
                border: 2px solid #dcdcdc;
                border-radius: 5px;
                background-color: white;
            }
            #task_name {
                font-size: 16px;
                padding: 3px;
                border: 1px solid #dcdcdc;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            #task_area{
                background-color: white;
                border: 1px solid #dcdcdc;
                border-buttom-left-radius: 5px;
                border-buttom-right-radius: 5px;
            }
        """)

        # 总体布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.frame)

if __name__ == '__main__':

    app = QApplication([])

    # 创建一个文本框作为内容区域
    content = QTextEdit("这里是内容区域")
    content.setMinimumHeight(100)

    # 创建卡片
    card = CardWidget("标题文本", content)
    card.show()

    app.exec()
