from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from qfluentwidgets import HyperlinkButton, PrimaryPushButton


class WebLinkButton(QWidget):
    def __init__(self, text: str, url: str, use_hyperlink: bool = True):
        """
        创建一个网页跳转按钮

        :param text: 按钮上的文本
        :param url: 要跳转的网页链接
        :param use_hyperlink: 是否使用 HyperlinkButton（默认 True）
        """
        super().__init__()
        self.url = url
        layout = QVBoxLayout(self)

        if use_hyperlink:
            # 使用超链接按钮
            self.button = HyperlinkButton(text, url, self)
        else:
            # 使用普通按钮
            self.button = PrimaryPushButton(text, self)
            self.button.clicked.connect(self.open_webpage)

        layout.addWidget(self.button)

    def open_webpage(self):
        """ 用默认浏览器打开网页 """
        QDesktopServices.openUrl(QUrl(self.url))


# 测试代码
if __name__ == "__main__":
    app = QApplication([])

    # 创建窗口
    window = QWidget()
    layout = QVBoxLayout(window)

    # 使用超链接按钮
    link_button = WebLinkButton("点击访问 PyQt-Fluent-Widgets 官网", "https://qfluentwidgets.com")

    # 使用普通按钮
    normal_button = WebLinkButton("点击打开百度", "https://www.baidu.com", use_hyperlink=False)

    layout.addWidget(link_button)
    layout.addWidget(normal_button)

    window.show()
    app.exec()
