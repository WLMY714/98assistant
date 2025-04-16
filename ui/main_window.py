import sys
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel

from qfluentwidgets import NavigationInterface, NavigationItemPosition, MessageBox, NavigationAvatarWidget
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import StandardTitleBar, FramelessWindow
from ui import setting_page_ui, sign_page_ui, score_page_ui, vedio_page_ui, tool_page_ui, help_page_ui
from pathlib import Path

from Utils.path_resolver import resource_path

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class MainWindow(FramelessWindow):

    def __init__(self):
        super().__init__()

        self.setTitleBar(StandardTitleBar(self))

        # 页面主布局
        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(self)
        self.stackWidget = QStackedWidget(self)

        # 右侧stack界面
        self.settingInterface = setting_page_ui.SettingPage()
        self.signInterface = sign_page_ui.SignPage()
        self.scoreInterface = score_page_ui.ScorePage()
        self.vedioInterface = vedio_page_ui.VedioPage()
        self.toolInterface = tool_page_ui.ToolPage()
        self.updateInterface = Widget('检查更新（待开发……）', self)
        self.helpInterface = help_page_ui.HelpPage()

        # 初始化布局
        self.initLayout()

        # 按钮绑定界面
        self.initNavigation()

        # 初始化窗口
        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):

        self.navigationInterface.setExpandWidth(140)
        self.addSubInterface(self.settingInterface, FIF.SETTING, '基础设置')
        self.addSubInterface(self.signInterface, FIF.LABEL, '账号签到')
        self.addSubInterface(self.scoreInterface, FIF.EXPRESSIVE_INPUT_ENTRY, '帖子评分')
        self.addSubInterface(self.vedioInterface, FIF.MOVIE, '新作预告')
        self.addSubInterface(self.toolInterface, FIF.APPLICATION, '常用工具')
        self.addSubInterface(self.helpInterface, FIF.HELP, '常见问题')
        self.addSubInterface(self.updateInterface, FIF.UPDATE, '检查更新')

        # 信息弹窗
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('WLMY', resource_path('Resource/image/me.png')),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.settingInterface.objectName())  # 确保导航栏同步选中
        self.stackWidget.setCurrentIndex(0)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(resource_path('Resource/image/logo.png')))
        self.setWindowTitle('98助手客户端UI 1.2')
        self.setQss()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, parent=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None
        )

    def setQss(self):
        with open(resource_path('./Resource/other/light.qss'), encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '如果这个项目帮助到了您，可以点一个免费的star⭐\n个人开发不易，您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://sehuatang.net/home.php?mod=space&uid=455944"))
