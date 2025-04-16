import random
import json
import time
import re

from time import sleep
from lxml import etree
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication
from PySide6.QtCore import Qt, QThread, Signal
from qfluentwidgets import ScrollArea, FlowLayout, PushButton, PrimaryPushButton, HyperlinkButton, InfoBar, InfoBarPosition

from Components.task_card import CardWidget
from Components.user_check import IconToggleCheckboxCard
from Api import api, xpath
from Utils.path_resolver import resource_path


def sign(user):
    try:
        sleep(user["sleep"])
        with open(resource_path("./Resource/cache/data.json"), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        reply = random.choice(obj["data"]["reply"])
        fid = random.choice([2, 36, 37])

        cookie = user["cookie"]
        domin = user["domin"]

        # 获取某板块某一页
        url = f"{domin}/forum.php?mod=forumdisplay&fid={fid}&orderby=dateline&orderby=dateline&filter=author&page={random.randint(20, 40)}"
        content = api.GetContent.get_content(url=url, cookie=cookie)

        # 获取此页随机一个帖子tid
        tree = etree.HTML(content.content)
        tids = tree.xpath(xpath.XpathOfSector.post_tid)
        tids = [tid for tid in tids if 'tid=' in tid]
        tids = [re.search(r'tid=(\d+)', url).group(1) for url in tids]
        tid = random.choice(tids)

        # 获取此帖子的pid、title
        url = f"{domin}/forum.php?mod=viewthread&tid={tid}"
        content = api.GetContent.get_content(url=url, cookie=cookie)

        tree = etree.HTML(content.content)
        title = str(tree.xpath(xpath.XpathOfPost.title)[0])
        pid = str(tree.xpath(xpath.XpathOfPost.pid)[0]).split('_')[1]

        msg = api.Sign.sign(fid=fid, tid=tid, pid=pid, cookie=cookie, domin=domin, message=reply)

        return {
            "code": msg.code,
            "error_reason": msg.message,
            "name": user["name"],
            "title": title,
            "reply": reply,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": url
        }
    except Exception as e:
        # print('sign:', e)
        return {
            "code": False,
            "error_reason": '未知错误，请重试…',
            "name": user["name"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": user["domin"]
        }

class WorkThread(QThread):
    task_finished = Signal(dict)

    def __init__(self, task_data: dict):
        super().__init__()
        self.task_data = task_data

    def run(self):
        try:
            task_result = sign(self.task_data)
            self.task_finished.emit(task_result)
        except Exception as e:
            # print('run: ', e)
            pass

class SignPage(QWidget):
    def __init__(self):
        super().__init__()

        self.sign_task_threads = []
        self.setObjectName("SignPage")
        self.setStyleSheet("""
            #SignPage {
                border: 1px solid rgb(229, 229, 229);
                background-color: rgb(249, 249, 249);
                border-radius : 10px;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 让 QWidget 使用样式背景
        self.setMinimumWidth(600)
        self.user_list = []
        self.domin = "https://sehuatang.net"

        # 主布局
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # 信息布局
        info_layout = QVBoxLayout()
        main_layout.addLayout(info_layout)

        # 信息布局-开始签到
        self.btn_sign = PrimaryPushButton(text='\n\n\n\n开\n始\n签\n到\n\n\n\n', parent=self)
        main_layout.addWidget(self.btn_sign)
        self.btn_sign.clicked.connect(self.start_sign)
        self.task_clear_button = PushButton(text='\n\n\n\n清\n空\n记\n录\n\n\n\n', parent=self)
        main_layout.addWidget(self.task_clear_button)
        self.task_clear_button.clicked.connect(self.clear_result)

        # 信息布局-签到账号
        self.info_account_widget = QWidget()
        self.info_account_layout = FlowLayout(self.info_account_widget)
        self.info_account_widget.setLayout(self.info_account_layout)
        info_account_scroll = ScrollArea()
        info_account_scroll.setWidgetResizable(True)
        info_account_scroll.setWidget(self.info_account_widget)
        info_account_card = CardWidget('签到账号', info_account_scroll)

        info_layout.addWidget(info_account_card)

        # 信息布局-签到板块
        info_sector_widget = QWidget()
        info_sector_layout = FlowLayout(info_sector_widget)
        info_sector_widget.setLayout(info_sector_layout)
        info_sector_scroll = ScrollArea()
        info_sector_scroll.setWidgetResizable(True)
        info_sector_scroll.setWidget(info_sector_widget)
        info_sector_card = CardWidget('签到板块', info_sector_scroll)

        sector1 = PushButton(text='国产原创区', parent=info_sector_widget)
        sector2 = PushButton(text='亚洲有码原创区', parent=info_sector_widget)
        sector3 = PushButton(text='亚洲无码原创区', parent=info_sector_widget)
        info_sector_layout.addWidget(sector1)
        info_sector_layout.addWidget(sector2)
        info_sector_layout.addWidget(sector3)
        info_layout.addWidget(info_sector_card)

        # 信息布局-签到回复
        self.info_reply_widget = QWidget()
        self.info_reply_layout = FlowLayout(self.info_reply_widget)
        self.info_reply_widget.setLayout(self.info_reply_layout)
        info_reply_scroll = ScrollArea()
        info_reply_scroll.setWidgetResizable(True)
        info_reply_scroll.setWidget(self.info_reply_widget)
        info_reply_card = CardWidget('签到内容', info_reply_scroll)

        self.init_reply()
        info_layout.addWidget(info_reply_card)

        # 信息布局空间分配
        info_layout.setStretch(0, 2)
        info_layout.setStretch(1, 1)
        info_layout.setStretch(2, 4)

        # 任务结果布局
        self.task_result_widget = QWidget()
        self.task_result_layout = QVBoxLayout(self.task_result_widget)
        self.task_result_widget.setLayout(self.task_result_layout)
        self.task_result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        task_result_scroll = ScrollArea()
        task_result_scroll.setWidgetResizable(True)
        task_result_scroll.setWidget(self.task_result_widget)
        task_result_card = CardWidget('签到记录', task_result_scroll)

        self.init_result()
        self.task_number = 0
        main_layout.addWidget(task_result_card)
        main_layout.setStretch(0, 10)
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 1)
        main_layout.setStretch(3, 12)

    def add_account(self, text):
        btn = IconToggleCheckboxCard(text)
        btn.setChecked(True)
        self.info_account_layout.addWidget(btn)

    def clear_success(self):
        InfoBar.success(
            title='成功',
            content='签到记录已清空',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def clear_result(self):
        for i in range(self.task_result_layout.count()):
            item = self.task_result_layout.itemAt(i)
            if item and (button := item.widget()):
                button.deleteLater()
        with open(resource_path("./Resource/cache/data.json"), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        obj["data"]["sign_result"] = []
        with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)
        self.clear_success()

    def add_result(self, accounts):

        for u in accounts:
            text = f'[排队中……] {u["name"]}\n[签到帖子] 正在获取…\n[签到内容] 正在获取…\n[签到时间] 平均3~5分钟/账号，请勿关闭程序…'
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

    def init_result(self):
        with open(resource_path("./Resource/cache/data.json"), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        for res in obj["data"]["sign_result"]:
            text = ""
            if res["code"]:
                text = f'[签到完成] {res["name"]}\n[签到帖子] {res["title"]}\n[签到回复] {res["reply"]}\n[签到时间] {res["time"]}'
            else:
                text = f'[签到失败] {res["name"]}\n[失败原因] {res["error_reason"]}'

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

    def init_reply(self):
        with open(resource_path("./Resource/cache/data.json"), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        reply_list = obj["data"]["reply"]
        for reply in reply_list[:100]:
            btn = PushButton(text=reply, parent=self.info_reply_widget)
            self.info_reply_layout.addWidget(btn)
        if len(reply_list) > 100:
            num = len(reply_list) - 100
            btn = PrimaryPushButton(text=f'剩余{num}个备用回复未展示……', parent=self.info_reply_widget)
            self.info_reply_layout.addWidget(btn)

    def clear_widget(self):
        # 清空账号选择区的所有卡片
        for i in reversed(range(self.info_account_layout.count())):
            item = self.info_account_layout.itemAt(i)
            if (widget := item.widget()) and isinstance(widget, IconToggleCheckboxCard):
                self.info_account_layout.removeWidget(widget)
                widget.deleteLater()

        # 可选：立即强制清理（非必须）
        QApplication.processEvents()  # 立即处理删除事件

    def showEvent(self, event):
        with open(resource_path("./Resource/cache/data.json"), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        self.domin = obj["data"]["domin"][-1]
        user_list = []
        for u in obj["data"]["users"]:
            user_list.append({"name": u["name"], "cookie": u["cookie"], "uid": u["uid"]})
        if sorted(self.user_list, key=str) != sorted(user_list, key=str) :
            self.clear_widget()
            self.user_list = user_list
            for user in self.user_list:
                self.add_account(user["name"])

    def no_member_warnning(self):
        InfoBar.warning(
            title='签到失败',
            content="尚未添加或选中账号",
            orient=Qt.Horizontal,
            isClosable=False,  # disable close button
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )

    def finish_sign(self, sign_info):
        """找到对应任务的按钮，并更新文本"""
        # print(sign_info, '\n\n')
        self.task_number -= 1
        for i in range(self.task_result_layout.count()):
            item = self.task_result_layout.itemAt(i)
            if item and (button := item.widget()):
                if sign_info["name"] in button.text():  # 任务匹配
                    button.deleteLater()
                    new_Text = ""
                    if sign_info["code"] :
                        new_Text = f'[签到完成] {sign_info["name"]}\n[签到帖子] {sign_info["title"]}\n[签到回复] {sign_info["reply"]}\n[签到时间] {sign_info["time"]}'
                    else :
                        new_Text = f'[签到失败] {sign_info["name"]}\n[失败原因] {sign_info["error_reason"]}'
                    new_button = HyperlinkButton(text=new_Text, url=sign_info["url"], parent=self.task_result_widget)
                    if sign_info["code"]:
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

                    with open(resource_path("./Resource/cache/data.json"), 'r', encoding='utf-8') as f:
                        obj = json.load(f)
                    obj["data"]["sign_result"].append(sign_info)
                    with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                        json.dump(obj, f, ensure_ascii=False, indent=4)

                    break
        if self.task_number == 0:
            self.btn_sign.setEnabled(True)
            self.task_clear_button.setEnabled(True)

    def start_sign(self):
        """输出所有账号及其选中状态"""
        accounts = []
        self.btn_sign.setEnabled(False)  # 任务开始，暂停签到按钮
        self.task_clear_button.setEnabled(False)
        sleep_num = 10
        for i in range(self.info_account_layout.count()):
            item = self.info_account_layout.itemAt(i)
            if (widget := item.widget()) and isinstance(widget, IconToggleCheckboxCard) and (widget.isChecked()):
                for u in self.user_list:
                    if u["name"] == widget.label.text():
                        u["sleep"] = sleep_num
                        u["domin"] = self.domin
                        accounts.append(u)
                        sleep_num += random.randint(30, 50)

        if len(accounts) == 0:
            self.no_member_warnning()
            self.btn_sign.setEnabled(True)
            self.task_clear_button.setEnabled(True)
            return

        self.add_result(accounts)

        try:
            self.task_number = len(accounts)
            for u in accounts:
                thread = WorkThread(u)

                thread.task_finished.connect(self.finish_sign)
                self.sign_task_threads.append(thread)
                thread.start()

        except Exception as e:
            # print('start', e)
            pass
