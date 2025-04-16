from PySide6.QtWidgets import QLabel, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect
from ui import setting_page_ui, sign_page_ui, score_page_ui, vedio_page_ui, tool_page_ui, update_page_ui
# from qfluentwidgets import Label

class MbtnController:
    def __init__(self, window):
        self.stack = window.stack
        self.buttons = window.menu_buttons
        self.selectMenuButtonIndex = window.selectMenuButtonIndex
        # self.pages = []

        # 创建 5 个页面
        menu_names = ["基础设置", "账号签到", "帖子评分", "新作预告", "常用工具", "检查更新"]

        function_page_style = """
                font-size: 20px;
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 5px;
            """

        # 基础设置界面
        setting_page = setting_page_ui.SettingPage()
        self.stack.addWidget(setting_page)

        # 账号签到界面
        sign_page = QLabel(f"这里是账号签到页面")
        sign_page.setStyleSheet(function_page_style)
        sign_page.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(sign_page)

        # 帖子评分界面
        score_page = QLabel(f"这里是帖子评分页面")
        score_page.setStyleSheet(function_page_style)
        score_page.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(score_page)

        # 新作预告界面
        vedio_page = QLabel(f"这里是新作预告页面")
        vedio_page.setStyleSheet(function_page_style)
        vedio_page.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(vedio_page)

        # 常用工具界面
        tool_page = QLabel(f"这里是常用工具页面")
        tool_page.setStyleSheet(function_page_style)
        tool_page.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(tool_page)

        # 检查更新界面
        update_page = QLabel(f"这里是检查更新页面")
        update_page.setStyleSheet(function_page_style)
        update_page.setAlignment(Qt.AlignCenter)
        self.stack.addWidget(update_page)

    def change_page(self, index):
        """ 切换到指定页面 """
        if index != self.selectMenuButtonIndex:
            # 更改页面、取消上个按钮样式、选中按钮样式、更改当前索引
            self.stack.setCurrentIndex(index)
            self.buttons[self.selectMenuButtonIndex].set_selectedStyle(False)
            self.buttons[index].set_selectedStyle(True)
            self.selectMenuButtonIndex = index
        else :
            self.buttons[index].set_selectedStyle(True)