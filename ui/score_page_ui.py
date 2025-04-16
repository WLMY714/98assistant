import random
import json
import time
import re

from time import sleep
from lxml import etree
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QPushButton
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from qfluentwidgets import (ScrollArea, FlowLayout, PushButton, PrimaryPushButton, HyperlinkButton, InfoBar,
                            InfoBarPosition, MessageBoxBase, SubtitleLabel, LineEdit, CaptionLabel)

from Components.task_card import CardWidget
from Components.user_check import IconToggleCheckboxCard
from Api import api, xpath
from Utils.path_resolver import resource_path


def score(info):

    sleep(info["sleep"])
    result = {
        "code": False,
        "error_reason": "未知错误，点此检查",
        "nameA": info["name"],
        "nameB": info["pyer"],
        "title": "获取失败",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": "https://www.sehuatang.net"
    }
    url = ""
    try:
        if info["pytype"] == 'post' and 'tid=' in info["pyer"]:
            url = f'{info["domin"]}/forum.php?mod=viewthread&{info["pyer"]}'
        elif info["pytype"] == 'post' and 'tid=' not in info["pyer"]:
            url = f'{info["domin"]}/forum.php?mod=viewthread&tid={info["pyer"]}'
        elif info["pytype"] == 'user':
            url = api.Rate.find_a_post(domin=info["domin"], cookie=info["cookie"], username=info["pyer"])
        if 'view=me&from=space' in url:
            result["error_reason"] = "用户主页 [主题第一页] 没有可评分的帖子"
            result["url"] = url
            return result
        content = api.GetContent.get_content(url=url, cookie=info["cookie"])
        if not content.code:
            result["error_reason"] = "链接有误，点此检查"
            result["url"] = url
            return result

        content_tree = etree.HTML(content.content)
        pid = str(content_tree.xpath(api.xpath.XpathOfPost.pid)[0]).split('_')[1]
        title = content_tree.xpath(api.xpath.XpathOfPost.title)
        match = re.search(r'tid=(\d+)', url)
        tid = match.group(1) if match else None
        msg = api.Rate.rate(tid=tid, pid=pid, cookie=info["cookie"], domin=info["domin"])

        result["code"] = msg.code
        result["error_reason"] = msg.message
        result["title"] = title
        result["url"] = url

        return result
    except Exception as e:
        result["error_reason"] = "链接有误，点此检查"
        result["url"] = url
        return result

class ScoreThread(QThread):
    task_finished = Signal(dict)

    def __init__(self, task_data: dict):
        super().__init__()
        self.task_data = task_data

    def run(self):
        try:
            task_result = score(self.task_data)
            self.task_finished.emit(task_result)
        except Exception as e:
            # print('score_run: ', e)
            pass

class CustomMessageBox(MessageBoxBase):
    """ Custom message box """
    def __init__(self, info, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(f'{info["title"]}', self)
        self.urlLineEdit = LineEdit(self)

        self.urlLineEdit.setPlaceholderText(f'{info["tips"]}')
        self.urlLineEdit.setClearButtonEnabled(True)

        self.warningLabel = CaptionLabel("输入内容为空")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # change the text of button
        self.yesButton.setText('添加')
        self.cancelButton.setText('取消')
        self.widget.setMinimumWidth(350)


    def validate(self):
        """ Rewrite the virtual method """
        isValid = self.urlLineEdit.text() != ""
        self.warningLabel.setHidden(isValid)
        self.urlLineEdit.setError(not isValid)
        return isValid

class ScorePage(QWidget):
    def __init__(self):
        super().__init__()

        self.task_number = 0
        self.pypost_list = []
        self.pyaccount_list = []
        self.user_list = []
        self.score_task_threads = []
        self.domin = "https://sehuatang.net"

        self.setObjectName("ScorePage")
        self.setStyleSheet("""
            #ScorePage {
                border: 1px solid rgb(229, 229, 229);
                background-color: rgb(249, 249, 249);
                border-radius : 10px;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 让 QWidget 使用样式背景
        self.setMinimumWidth(600)

        # 主布局
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # 信息布局
        info_layout = QVBoxLayout()
        main_layout.addLayout(info_layout)

        # 信息布局-清空记录
        self.task_clear_button = PushButton(text='\n\n\n\n清\n空\n记\n录\n\n\n\n', parent=self)
        main_layout.addWidget(self.task_clear_button)

        # 信息布局-评分账号
        self.info_account_widget = QWidget()
        self.info_account_layout = FlowLayout(self.info_account_widget)
        self.info_account_widget.setLayout(self.info_account_layout)
        info_account_scroll = ScrollArea()
        info_account_scroll.setWidgetResizable(True)
        info_account_scroll.setWidget(self.info_account_widget)
        info_account_card = CardWidget('评分账号', info_account_scroll)

        info_layout.addWidget(info_account_card)

        # 信息布局-给帖子评分
        score_post_widget = QWidget()
        score_post_layout = QVBoxLayout(score_post_widget)
        score_post_widget.setLayout(score_post_layout)

        # 信息布局-给帖子评分-评分按钮
        self.post_btn_layout = QHBoxLayout()
        self.score_post_add_btn = PrimaryPushButton(text='添加帖子', parent=score_post_widget)
        self.score_post_add_btn.clicked.connect(lambda: self.showDialog({"title": "输入帖子tid", "tips": "如：tid=1769408"}))
        self.score_post_btn = PrimaryPushButton(text='开始评分', parent=score_post_widget)
        self.score_post_btn.clicked.connect(self.score_to_post)
        self.score_post_clear_btn = PushButton(text='清空列表', parent=score_post_widget)
        self.post_btn_layout.addWidget(self.score_post_add_btn)
        self.post_btn_layout.addWidget(self.score_post_btn)
        self.post_btn_layout.addWidget(self.score_post_clear_btn)
        score_post_layout.addLayout(self.post_btn_layout)

        # 信息布局-给帖子评分-显示区域
        self.score_post_show = QWidget()
        self.score_post_show_layout = FlowLayout(self.score_post_show)
        self.score_post_show.setLayout(self.score_post_show_layout)
        self.score_post_clear_btn.clicked.connect(lambda: self.clear_widget(self.score_post_show_layout, '帖子队列已清空'))
        score_post_show_scroll = ScrollArea()
        score_post_show_scroll.setWidgetResizable(True)
        score_post_show_scroll.setWidget(self.score_post_show)
        score_post_show_scroll.setObjectName("scorePostShowScroll")
        score_post_show_scroll.setStyleSheet("""
            #scorePostShowScroll {
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
        score_post_layout.addWidget(score_post_show_scroll)

        # 信息布局-给帖子评分-卡片
        score_post_card = CardWidget('给帖子评分', score_post_widget)
        info_layout.addWidget(score_post_card)

        # 信息布局-给账号评分
        score_account_widget = QWidget()
        score_account_layout = QVBoxLayout(score_account_widget)
        score_account_widget.setLayout(score_account_layout)

        # 信息布局-给账号评分-评分按钮
        self.account_btn_layout = QHBoxLayout()
        self.score_account_add_btn = PrimaryPushButton(text='添加账号', parent=score_account_widget)
        self.score_account_add_btn.clicked.connect(lambda : self.showDialog({"title" : "输入用户名", "tips" : "如：嗷大喵"}))
        self.score_account_btn = PrimaryPushButton(text='开始评分', parent=score_account_widget)
        self.score_account_btn.clicked.connect(self.score_to_account)
        self.score_account_clear_btn = PushButton(text='清空列表', parent=score_account_widget)
        self.account_btn_layout.addWidget(self.score_account_add_btn)
        self.account_btn_layout.addWidget(self.score_account_btn)
        self.account_btn_layout.addWidget(self.score_account_clear_btn)
        score_account_layout.addLayout(self.account_btn_layout)

        # 信息布局-给账号布局-显示区域
        self.score_account_show = QWidget()
        self.score_account_show_layout = FlowLayout(self.score_account_show)
        self.score_account_show.setLayout(self.score_account_show_layout)
        self.score_account_clear_btn.clicked.connect(lambda: self.clear_widget(self.score_account_show_layout, '账号队列已清空'))
        score_account_show_scroll = ScrollArea()
        score_account_show_scroll.setWidgetResizable(True)
        score_account_show_scroll.setWidget(self.score_account_show)
        score_account_show_scroll.setObjectName("scoreAccountShowScroll")
        score_account_show_scroll.setStyleSheet("""
                    #scoreAccountShowScroll {
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
        score_account_layout.addWidget(score_account_show_scroll)

        # 信息布局-给账号评分-卡片
        score_account_card = CardWidget('给账号评分', score_account_widget)
        info_layout.addWidget(score_account_card)

        # 信息布局空间分配
        info_layout.setStretch(0, 2)
        info_layout.setStretch(1, 3)
        info_layout.setStretch(2, 3)

        # 任务结果布局
        self.task_result_widget = QWidget()
        self.task_result_layout = QVBoxLayout(self.task_result_widget)
        self.task_result_widget.setLayout(self.task_result_layout)
        self.task_result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        task_result_scroll = ScrollArea()
        task_result_scroll.setWidgetResizable(True)
        task_result_scroll.setWidget(self.task_result_widget)
        task_result_card = CardWidget('评分记录', task_result_scroll)

        self.init_result()
        self.task_clear_button.clicked.connect(
            lambda: self.clear_widget(self.task_result_layout, '评分记录已清空'))
        main_layout.addWidget(task_result_card)
        main_layout.setStretch(0, 12)
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 12)

        self.init()

    def clear_success(self, message):
        InfoBar.success(
            title='成功',
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def no_member_warnning(self, message):
        InfoBar.warning(
            title='评分失败',
            content=message,
            orient=Qt.Horizontal,
            isClosable=False,  # disable close button
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def btn_Enable_false(self):
        self.task_clear_button.setEnabled(False)
        self.score_account_add_btn.setEnabled(False)
        self.score_account_btn.setEnabled(False)
        self.score_account_clear_btn.setEnabled(False)
        self.score_post_add_btn.setEnabled(False)
        self.score_post_btn.setEnabled(False)
        self.score_post_clear_btn.setEnabled(False)

    def btn_Enable_true(self):
        self.task_clear_button.setEnabled(True)
        self.score_account_add_btn.setEnabled(True)
        self.score_account_btn.setEnabled(True)
        self.score_account_clear_btn.setEnabled(True)
        self.score_post_add_btn.setEnabled(True)
        self.score_post_btn.setEnabled(True)
        self.score_post_clear_btn.setEnabled(True)

    def add_result(self, accounts, pylist):

        for u in accounts:
            for py in pylist:
                text = f'[排队中……] {u["name"]} 给 {py} 评分中…\n[评分帖子] 正在获取…\n[评分时间] 评分间隔1~3分钟，请勿关闭程序…'
                btn = HyperlinkButton(text=text, url=self.domin, parent=self.task_result_widget)
                btn.setStyleSheet("""
                            HyperlinkButton {
                                color: #1f1f1f; /* 字体颜色 */
                                font-size: 13px;
                                text-align: left;
                                padding: 6px 12px;
                                border: 2px solid #99d9ea; /* 明确设置边框 */
                                border-radius: 3px; /* 圆角 */
                                background-color: #c4ffd3; /* 设为白色背景，确保边框可见 */
                            }
                            HyperlinkButton:hover {
                                background-color: #E8F0FE; /* 悬停时背景变色 */
                            }
                            HyperlinkButton:pressed {
                                background-color: #E0F5F0;
                            }
                        """)
                self.task_result_layout.insertWidget(0, btn)

    def finish_score(self, score_info):
        """找到对应任务的按钮，并更新文本"""
        # print(score_info, '\n')
        self.task_number -= 1
        for i in range(self.task_result_layout.count()):
            item = self.task_result_layout.itemAt(i)
            if item and (button := item.widget()):
                if score_info["nameA"] in button.text() and score_info["nameB"] in button.text():  # 任务匹配
                    button.deleteLater()
                    new_Text = ""
                    if score_info["code"]:
                        new_Text = f'[评分成功] {score_info["nameA"]} 评分给 {score_info["nameB"]}\n[评分帖子] {score_info["title"]}\n[评分时间] {score_info["time"]}'
                    else:
                        new_Text = f'[评分失败] {score_info["nameA"]} 评分给 {score_info["nameB"]}\n[评分帖子] {score_info["title"]}\n[失败原因] {score_info["error_reason"]}'

                    new_button = HyperlinkButton(text=new_Text, url=score_info["url"], parent=self.task_result_widget)
                    if score_info["code"]:
                        new_button.setStyleSheet("""
                            HyperlinkButton {
                                color: #1f1f1f; /* 字体颜色 */
                                font-size: 13px;
                                text-align: left;
                                padding: 6px 12px;
                                border: 2px solid #99d9ea; /* 明确设置边框 */
                                border-radius: 3px; /* 圆角 */
                                background-color: white; /* 设为白色背景，确保边框可见 */
                            }
                            HyperlinkButton:hover {
                                background-color: #E8F0FE; /* 悬停时背景变色 */
                            }
                            HyperlinkButton:pressed {
                                background-color: #E0F5F0;
                            }
                        """)
                    else:
                        new_button.setStyleSheet("""
                            HyperlinkButton {
                                color: #e74032; /* 字体颜色 */
                                font-size: 13px;
                                text-align: left;
                                padding: 6px 12px;
                                border: 2px solid #99d9ea; /* 明确设置边框 */
                                border-radius: 3px; /* 圆角 */
                                background-color: white; /* 设为白色背景，确保边框可见 */
                            }
                            HyperlinkButton:hover {
                                background-color: #E8F0FE; /* 悬停时背景变色 */
                            }
                            HyperlinkButton:pressed {
                                background-color: #E0F5F0;
                            }
                        """)
                    self.task_result_layout.insertWidget(i, new_button)

                    with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
                        obj = json.load(f)
                    obj["data"]["score_result"].append(score_info)
                    with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                        json.dump(obj, f, ensure_ascii=False, indent=4)

                    break
        if self.task_number == 0:
            self.btn_Enable_true()

    def score_to_post(self):
        self.btn_Enable_false()
        accounts = []
        pyposts = []
        sleep_num = 10
        for i in range(self.info_account_layout.count()):
            item = self.info_account_layout.itemAt(i)
            if (widget := item.widget()) and isinstance(widget, IconToggleCheckboxCard) and (widget.isChecked()):
                for u in self.user_list:
                    if u["name"] == widget.label.text():
                        u["sleep"] = sleep_num
                        u["domin"] = self.domin
                        accounts.append(u)
                        sleep_num += random.randint(50, 80)
        for i in range(self.score_post_show_layout.count()):
            item = self.score_post_show_layout.itemAt(i)
            if (widget := item.widget()) and isinstance(widget, IconToggleCheckboxCard) and (widget.isChecked()):
                pyposts.append(widget.label.text())

        if len(accounts) == 0:
            self.no_member_warnning('未选中评分账号')
            self.btn_Enable_true()
            return
        elif len(pyposts) == 0:
            self.no_member_warnning('未选中被评分帖子tid')
            self.btn_Enable_true()
            return
        self.add_result(accounts, pyposts)
        
        try:
            self.task_number = len(accounts) * len(pyposts)
            for u in accounts:
                for py in pyposts:
                    u["pyer"] = py
                    u["pytype"] = 'post'
                    thread = ScoreThread(u)

                    thread.task_finished.connect(self.finish_score)
                    self.score_task_threads.append(thread)
                    thread.start()
        except Exception as e:
            # print('score_start', e)
            pass

    def score_to_account(self):
        self.btn_Enable_false()
        accounts = []
        pyaccounts = []
        sleep_num = 10
        for i in range(self.info_account_layout.count()):
            item = self.info_account_layout.itemAt(i)
            if (widget := item.widget()) and isinstance(widget, IconToggleCheckboxCard) and (widget.isChecked()):
                for u in self.user_list:
                    if u["name"] == widget.label.text():
                        u["sleep"] = sleep_num
                        u["domin"] = self.domin
                        accounts.append(u)
                        sleep_num += random.randint(60, 150)
        for i in range(self.score_account_show_layout.count()):
            item = self.score_account_show_layout.itemAt(i)
            if (widget := item.widget()) and isinstance(widget, IconToggleCheckboxCard) and (widget.isChecked()):
                pyaccounts.append(widget.label.text())

        if len(accounts) == 0:
            self.no_member_warnning('未选中评分账号')
            self.btn_Enable_true()
            return
        elif len(pyaccounts) == 0:
            self.no_member_warnning('未选中被评分用户')
            self.btn_Enable_true()
            return
        self.add_result(accounts, pyaccounts)

        try:
            self.task_number = len(accounts) * len(pyaccounts)
            for u in accounts:
                for py in pyaccounts:
                    u["pyer"] = py
                    u["pytype"] = 'user'
                    thread = ScoreThread(u)

                    thread.task_finished.connect(self.finish_score)
                    self.score_task_threads.append(thread)
                    thread.start()
        except Exception as e:
            # print('score_start', e)
            pass

    def add_account(self, text, layout):
        btn = IconToggleCheckboxCard(text)
        layout.addWidget(btn)

    def showDialog(self, info):
        w = CustomMessageBox(info, self)
        if w.exec():
            if '帖子' in info["title"]:
                self.add_account(w.urlLineEdit.text(), self.score_post_show_layout)
                with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
                    obj = json.load(f)
                obj["data"]["pypost"].append(w.urlLineEdit.text())
                with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                    json.dump(obj, f, ensure_ascii=False, indent=4)
                self.clear_success('帖子添加成功')
            elif '用户' in info["title"]:
                self.add_account(w.urlLineEdit.text(), self.score_account_show_layout)
                with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
                    obj = json.load(f)
                obj["data"]["pyaccount"].append(w.urlLineEdit.text())
                with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                    json.dump(obj, f, ensure_ascii=False, indent=4)
                self.clear_success('用户添加成功')

    def clear_widget(self, layout, message=None):
        # 清空账号选择区的所有卡片
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if (widget := item.widget()) and isinstance(widget, IconToggleCheckboxCard):
                layout.removeWidget(widget)
                widget.deleteLater()
            elif (widget := item.widget()) and isinstance(widget, HyperlinkButton):
                widget.deleteLater()

        if message and '帖子' in message:
            self.pypost_list = []
            with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
                obj = json.load(f)
            obj["data"]["pypost"] = []
            with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)
        elif message and '账号' in message:
            self.pyaccount_list = []
            with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
                obj = json.load(f)
            obj["data"]["pyaccount"] = []
            with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)
        elif message and '记录' in message:
            with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
                obj = json.load(f)
            obj["data"]["score_result"] = []
            with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)
        if message is not None:
            self.clear_success(message)

    def showEvent(self, event):
        with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        self.domin = obj["data"]["domin"][-1]
        user_list = []
        for u in obj["data"]["users"]:
            user_list.append({"name": u["name"], "cookie": u["cookie"], "uid": u["uid"]})
        if sorted(self.user_list, key=str) != sorted(user_list, key=str) :
            self.clear_widget(self.info_account_layout)
            self.user_list = user_list
            for user in self.user_list:
                self.add_account(user["name"], self.info_account_layout)

    def init_result(self):
        with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        for res in obj["data"]["score_result"]:
            text = ""
            if res["code"]:
                text = f'[评分成功] {res["nameA"]} 评分给 {res["nameB"]}\n[评分帖子] {res["title"]}\n[评分时间] {res["time"]}'
            else:
                text = f'[评分失败] {res["nameA"]} 评分给 {res["nameB"]}\n[评分帖子] {res["title"]}\n[失败原因] {res["error_reason"]}'

            button = HyperlinkButton(text=text, url=res["url"], parent=self.task_result_widget)
            if res["code"]:
                button.setStyleSheet("""
                    HyperlinkButton {
                        color: #1f1f1f; /* 字体颜色 */
                        font-size: 13px;
                        text-align: left;
                        padding: 6px 12px;
                        border: 2px solid #99d9ea; /* 明确设置边框 */
                        border-radius: 3px; /* 圆角 */
                        background-color: white; /* 设为白色背景，确保边框可见 */
                    }
                    HyperlinkButton:hover {
                        background-color: #E8F0FE; /* 悬停时背景变色 */
                    }
                    HyperlinkButton:pressed {
                        background-color: #E0F5F0;
                    }
                """)
            else :
                button.setStyleSheet("""
                    HyperlinkButton {
                        color: #e74032; /* 字体颜色 */
                        font-size: 13px;
                        text-align: left;
                        padding: 6px 12px;
                        border: 2px solid #99d9ea; /* 明确设置边框 */
                        border-radius: 3px; /* 圆角 */
                        background-color: white; /* 设为白色背景，确保边框可见 */
                    }
                    HyperlinkButton:hover {
                        background-color: #E8F0FE; /* 悬停时背景变色 */
                    }
                    HyperlinkButton:pressed {
                        background-color: #E0F5F0;
                    }
                """)
            self.task_result_layout.addWidget(button)

    def init(self):
        with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        self.pypost_list = obj["data"]["pypost"]
        self.pyaccount_list = obj["data"]["pyaccount"]
        for post in self.pypost_list:
            self.add_account(post, self.score_post_show_layout)
        for account in self.pyaccount_list:
            self.add_account(account, self.score_account_show_layout)
