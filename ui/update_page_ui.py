
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from qfluentwidgets import PrimaryPushButton, TextBrowser, InfoBar, InfoBarPosition

def get_version(version):

    result = {
        "version" : version,
        "url" : None,
        "code" : False,
        "error_reason" : None
    }
    try:
        url = "https://api.github.com/repos/WLMY714/98assistant/releases/latest"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            result["version"] = data['tag_name']
            result["url"] = data['assets'][0]['browser_download_url']
            result["code"] = True

        return result
    except Exception as e:
        result["error_reason"] = '网络错误，请检查网络，或是否开启代理'
        return result

class UpdateThread(QThread):
    task_finished = Signal(dict)

    def __init__(self, version: str):
        super().__init__()
        self.version = version

    def run(self):
        task_result = get_version(self.version)
        self.task_finished.emit(task_result)

class UpdatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("UpdatePage")
        self.setStyleSheet("""
            #UpdatePage {
                border: 1px solid rgb(229, 229, 229);
                background-color: rgb(249, 249, 249);
                border-radius : 10px;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.thread_list = []

        self.version = "version1.3"
        self.textbox = None

        # 主布局：上下添加伸缩空间实现居中
        self.main_layout = QVBoxLayout(self)

        self.main_layout.addStretch(1)  # 顶部占位撑开

        # 中间布局，用来装按钮和文本框
        self.center_layout = QVBoxLayout()
        self.center_layout.setAlignment(Qt.AlignHCenter)

        self.check_btn = PrimaryPushButton(text='检查更新')
        self.check_btn.setFixedWidth(400)
        self.check_btn.clicked.connect(self.check_update)

        self.center_layout.addWidget(self.check_btn)

        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addStretch(1)  # 底部占位撑开

    def fail_meaages(self, message):
        InfoBar.warning(
            title='失败',
            content=message,
            orient=Qt.Horizontal,
            isClosable=False,  # disable close button
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def success_message(self, message):
        InfoBar.success(
            title='成功',
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def show_textbox(self, version, url):
        if not self.textbox:
            self.textbox = TextBrowser()
            self.textbox.setMarkdown(f"🎉最新版本：{version}\n\n"
                                     f"🎀下载链接：{url}\n\n"
                                     f"✨更新记录：https://github.com/WLMY714/98assistant/releases\n\n"
                                     ".\n\n"
                                     "🍳更新方法（必看）：\n\n"
                                     "1、下载软件：复制下载链接到浏览器下载、解压\n\n"
                                     "2、继承数据：您的数据保存在安装目录下的_internal/Resource文件夹中，将现在使用版本的Resource文件夹覆盖新版本的Resource文件夹，就可以继承您的数据")
            self.textbox.setFixedWidth(400)
            self.center_layout.addWidget(self.textbox)

    def show_textbox2(self, version, url):
        if not self.textbox:
            self.textbox = TextBrowser()
            self.textbox.setMarkdown(f"🎉最新版本：{version}（当前已是最新版本）\n\n"
                                     f"🎀下载链接：{url}\n\n"
                                     f"✨更新记录：https://github.com/WLMY714/98assistant/releases\n\n")
            self.textbox.setFixedWidth(400)
            self.center_layout.addWidget(self.textbox)

    def finish_task(self, task_result):
        if not task_result['code']:
            self.fail_meaages(task_result['error_reason'])
        elif self.version == task_result['version']:
            self.success_message('已是最新版本')
            self.show_textbox2(version=task_result['version'], url=task_result['url'])
        elif self.version != task_result['version']:
            self.success_message('有新的版本')
            self.show_textbox(version=task_result['version'], url=task_result['url'])
        self.check_btn.setEnabled(True)
        self.check_btn.setText('检查更新')

    def check_update(self):
        self.check_btn.setEnabled(False)
        self.check_btn.setText('检查更新中……')

        thread = UpdateThread(self.version)
        thread.task_finished.connect(self.finish_task)
        self.thread_list.append(thread)
        thread.start()

