
import os
import sys
import json
import shutil

from dateutil.relativedelta import relativedelta
from datetime import datetime
from time import sleep

from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QLabel
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QPixmap, QColor
from qfluentwidgets import (ScrollArea, TextBrowser, LineEdit, CalendarPicker, ComboBox, PushButton, PrimaryPushButton,
                            MessageBoxBase, SubtitleLabel, CaptionLabel, InfoBar, InfoBarPosition, FlowLayout,
                            StateToolTip)

from Components.task_card import CardWidget
from Components.folder_card import FolderIconWidget
from Components.tool_card import ToolCardWidget
from Api.api import Darkroom
from Utils.path_resolver import resource_path

class ToolThread(QThread):
    task_finished = Signal(dict)

    def __init__(self, taskname, cookie, domin):
        super().__init__()
        self.taskname = taskname
        self.cookie = cookie
        self.domin = domin

    def run(self):
        if self.taskname == 'darkroom':
            folder = 'tool_小黑屋_'+ datetime.now().strftime('%Y%m%d_%H%M%S')
            path = resource_path('./Resource/cache/file') + '/' + folder
            os.makedirs(path, exist_ok=True)
            result = {
                'task_message': '❌小黑屋记录获取失败',
                'path': path,
                'name': folder,
                'icon': resource_path('./Resource/image/file.png'),
                'is_new': True
            }
            try:
                Darkroom.start_get_darkroom(domin=self.domin, cookie=self.cookie, folder=path)
                result['task_message'] = '✅小黑屋记录获取完成'
                self.task_finished.emit(result)
            except Exception as e:
                self.task_finished.emit(result)

        elif self.taskname == 'ranking':
            pass

# class CustomMessageBox(MessageBoxBase):
#     """ Custom message box """
#     def __init__(self, title='', message='', error='', parent=None):
#         super().__init__(parent)
#         self.titleLabel = SubtitleLabel(title, self)
#         self.urlLineEdit = LineEdit(self)
#
#         self.urlLineEdit.setPlaceholderText(message)
#         self.urlLineEdit.setClearButtonEnabled(True)
#
#         self.warningLabel = CaptionLabel(error)
#         self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))
#
#         # add widget to view layout
#         self.viewLayout.addWidget(self.titleLabel)
#         self.viewLayout.addWidget(self.urlLineEdit)
#         self.viewLayout.addWidget(self.warningLabel)
#         self.warningLabel.hide()
#
#         # change the text of button
#         self.yesButton.setText('添加')
#         self.cancelButton.setText('取消')
#         self.widget.setMinimumWidth(350)
#
#
#     def validate(self):
#         """ Rewrite the virtual method """
#         isValid = False
#         valid_code = ['1', '2', '3', 'lbsl98t', 'yut98t', 'r3698t', 'lbsl98t-l', 'yut98t-l']
#         if self.urlLineEdit.text() in valid_code :
#             isValid = True
#         self.warningLabel.setHidden(isValid)
#         self.urlLineEdit.setError(not isValid)
#         return isValid

class ToolPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("ToolPage")
        self.setStyleSheet("""
            #ToolPage {
                border: 1px solid rgb(229, 229, 229);
                background-color: rgb(249, 249, 249);
                border-radius : 10px;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 让 QWidget 使用样式背景
        self.setMinimumWidth(600)

        self.cookie = ''
        self.domin = ''
        self.thread_list = []
        self.task_doing = None

        main_layout = QVBoxLayout(self)

        tool_widget = QWidget()
        self.tool_layout = FlowLayout(tool_widget)
        # self.tool_layout.addStretch()
        tool_scroll = ScrollArea()
        tool_scroll.setWidgetResizable(True)
        tool_scroll.setWidget(tool_widget)
        tool_scroll.setObjectName('toolScroll')
        tool_scroll.setStyleSheet("""
                            #toolScroll {
                                border: 1px solid #D1D1D1;
                                background: #F8F8F8;
                            }
                            QScrollBar:vertical {
                                width: 8px;
                                background: transparent;
                            }
                            QScrollBar::handle:vertical {
                                background: #C0C0C0;
                            }
                            QScrollBar::handle:vertical:hover {
                                background: #A0A0A0;
                            }
                        """)
        tool_card = CardWidget(title='工具箱', content_widget=tool_scroll)
        main_layout.addWidget(tool_card)

        history_widget = QWidget()
        self.history_layout = FlowLayout(history_widget)
        history_widget.setMinimumHeight(100)
        history_scroll = ScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setWidget(history_widget)
        history_scroll.setObjectName('historyScroll')
        history_scroll.setStyleSheet("""
            #historyScroll {
                border: 1px solid #D1D1D1;
                background: #F8F8F8;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
        """)
        history_card = CardWidget(title='任务记录', content_widget=history_scroll)
        main_layout.addWidget(history_card)
        main_layout.setStretch(0, 6)
        main_layout.setStretch(1, 4)

        # 油猴脚本
        tampermonkey_layout = QVBoxLayout()
        tampermonkey_name = PushButton(text='✨98油猴脚本✨')
        tampermonkey_layout.addWidget(tampermonkey_name)
        self.tampermonkey_btn = PrimaryPushButton(text='点击获取')
        self.tampermonkey_btn.clicked.connect(self.copy_tampermonkey)
        tampermonkey_layout.addWidget(self.tampermonkey_btn)
        tampermonkey_label = '去除论坛彩色广告自用版，提供丰富功能列表（安装后没反应检查是否开启开发者模式）'
        tampermonkey_card = ToolCardWidget(
            icon_path=resource_path('./Resource/image/tampermonkey.png'),
            control_layout=tampermonkey_layout,
            description=tampermonkey_label,
            parent=self
        )
        self.tool_layout.addWidget(tampermonkey_card)

        # 小黑屋记录
        darkroom_layout = QVBoxLayout()
        darkroom_name = PushButton(text='✨小黑屋记录✨')
        darkroom_layout.addWidget(darkroom_name)
        self.darkroom_btn = PrimaryPushButton(text='点击获取')
        self.darkroom_btn.clicked.connect(lambda : self.start_task('darkroom'))
        darkroom_layout.addWidget(self.darkroom_btn)
        darkroom_label = '获取论坛内小黑屋最近100条详情记录（需要在【基础设置】界面添加至少一个账号）'
        darkroom_card = ToolCardWidget(
            icon_path=resource_path('./Resource/image/darkroom.png'),
            control_layout=darkroom_layout,
            description=darkroom_label,
            parent=self
        )
        self.tool_layout.addWidget(darkroom_card)

        # 实时热门
        ranking_layout = QVBoxLayout()
        ranking_name = PushButton(text='✨实时热度排行✨')
        ranking_layout.addWidget(ranking_name)
        self.ranking_btn = PrimaryPushButton(text='开发中……')
        # self.ranking_btn.clicked.connect(lambda : self.start_task('ranking'))
        self.ranking_btn.setEnabled(False)
        ranking_layout.addWidget(self.ranking_btn)
        ranking_label = '获取论坛24h内，原创区、综合区帖子热度排行榜、热度增速，实时获取（需要至少一个账号）'
        ranking_card = ToolCardWidget(
            icon_path=resource_path('./Resource/image/ranking.png'),
            control_layout=ranking_layout,
            description=ranking_label,
            parent=self
        )
        self.tool_layout.addWidget(ranking_card)

        # 灌水检测
        kill_layout = QVBoxLayout()
        kill_name = PushButton(text='✨用户灌水检测✨')
        kill_layout.addWidget(kill_name)
        self.kill_btn = PrimaryPushButton(text='开发中……')
        self.kill_btn.setEnabled(False)
        kill_layout.addWidget(self.kill_btn)
        kill_label = '统计某用户复制标题、灌水评论次数（需要在【基础设置】界面添加至少一个账号）'
        kill_card = ToolCardWidget(
            icon_path=resource_path('./Resource/image/kill.png'),
            control_layout=kill_layout,
            description=kill_label,
            parent=self
        )
        self.tool_layout.addWidget(kill_card)


        self.init_widget()

    def task_doing_function(self, taskname='', content='✅数据获取成功'):
        if self.task_doing:
            self.task_doing.setContent(content)
            self.task_doing.setTitle('任务完成')
            self.task_doing.setState(True)
            self.task_doing = None
        else:
            self.task_doing = StateToolTip('任务进行中', f'正在获取 {taskname}…', self)
            width = self.width()
            self.task_doing.move(width-300, 20)
            self.task_doing.show()

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

    def warnning_meaages(self, message):
        InfoBar.warning(
            title='失败',
            content=message,
            orient=Qt.Horizontal,
            isClosable=False,  # disable close button
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def btn_state(self, state):
        self.tampermonkey_btn.setEnabled(state)
        self.darkroom_btn.setEnabled(state)

    def add_folder(self, file_info):
        card = FolderIconWidget(file_info["path"], file_info["name"], file_info["icon"], is_new=file_info["is_new"],
                                parent=self)
        self.history_layout.insertWidget(0, card)

    def copy_tampermonkey(self):
        self.btn_state(False)
        self.task_doing_function(taskname='油猴脚本')

        # 确保目标文件夹存在
        target_folder = resource_path('./Resource/cache/file') + '/tool_油猴脚本'
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # 构造完整路径
        source_path = resource_path('./Resource/text') + '/98堂油猴脚本-1.2.user.js'
        target_path = target_folder  + '/98堂油猴脚本-1.2.user.js'

        # 检查是否存在
        if os.path.exists(target_path):
            self.task_doing_function(content='✅油猴脚本获取完成！')
            self.btn_state(True)
            self.add_folder({
                "path": target_folder,
                "name": 'tool_油猴脚本',
                "icon": resource_path('./Resource/image/file.png'),
                "is_new": True
            })
            return

        # 执行复制
        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            self.task_doing_function(content='✅油猴脚本获取完成！')
            self.add_folder({
                "path": target_folder,
                "name": 'tool_油猴脚本',
                "icon": resource_path('./Resource/image/file.png'),
                "is_new": True
            })
        else:
            self.task_doing_function(content='💔油猴脚本获取失败，源文件被删除')
        self.btn_state(True)

    def init_widget(self):
        folder = resource_path('./Resource/cache/file')
        file_list = [name for name in os.listdir(folder)
                     if os.path.isdir(os.path.join(folder, name)) and 'tool_' in name]

        for file in file_list:
            path = os.path.join(folder, file)
            file_info = {'path': path, 'name': file, 'icon': resource_path('./Resource/image/file.png'), 'is_new': False}
            self.add_folder(file_info)

    def finish_task(self, result):
        self.add_folder(result)
        self.task_doing_function(content=result['task_message'])
        self.btn_state(True)

    def start_task(self, taskname):
        self.btn_state(False)
        with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        if len(obj['data']['users']) < 1 :
            self.warnning_meaages('请在【基础设置】界面添加至少一个账号')
            self.btn_state(True)
            return
        if len(obj['data']['domin']) < 1 or obj['data']['domin'][-1] =='':
            self.warnning_meaages('请在【基础设置】界面添加至少一个域名')
            self.btn_state(True)
            return

        self.cookie = obj['data']['users'][0]['cookie']
        self.domin = obj['data']['domin'][-1]
        if taskname == 'darkroom':
            self.task_doing_function(taskname='小黑屋记录')
        elif taskname == 'ranking':
            self.task_doing_function(taskname='ranking')

        thread = ToolThread(taskname, self.cookie, self.domin)
        thread.task_finished.connect(self.finish_task)
        self.thread_list.append(thread)
        thread.start()

