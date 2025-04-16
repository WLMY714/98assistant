
import json
import time
import sys
import shutil
from lxml import etree
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QThread, Signal

from qfluentwidgets import (ScrollArea, MessageBoxBase, SubtitleLabel, LineEdit, PushButton, CaptionLabel,
                            InfoBar, InfoBarPosition, ComboBox)

from Components.user_card import UserCard
from Model.user import User
from Api import api, xpath, photo_downloader
from Utils.path_resolver import resource_path

def test_domin(domin):
    url = domin
    try :
        content = api.GetContent.get_content(url)
        if 'static/safe/js/mainv2.js?v=' in content.content:
            return True, domin
        return False, domin
    except Exception as e:
        return False, domin

class TestWorkerDomin(QThread):
    finished = Signal(bool)  # 任务完成信号，传递验证结果
    domin_ready = Signal(str)  # 新增信号，用于传递 User 对象

    def __init__(self, domin, parent=None):
        super().__init__(parent)
        self.domin = domin

    def run(self):
        res, domin = test_domin(self.domin)  # 修改 test_cookie 返回 User 对象
        if res:
            self.domin_ready.emit(domin)  # 传递 User 对象
        self.finished.emit(res)  # 传递验证结果


class CustomMessageBoxDomin(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        if parent is not None:
            self.init_combox = parent.init_combox

        self.titleLabel = SubtitleLabel('输入论坛域名', self)
        self.urlLineEdit = LineEdit(self)
        self.urlLineEdit.setPlaceholderText('例如: https://www.sehuatang.net')

        self.testingLabel = CaptionLabel("正在测试域名", self)
        self.testingLabel.setStyleSheet("color: #cf1010;")

        self.errorLabel = CaptionLabel("error: 网络错误/域名无效，请重试", self)
        self.errorLabel.setStyleSheet("color: #cf1010;")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)
        self.viewLayout.addWidget(self.testingLabel)
        self.viewLayout.addWidget(self.errorLabel)
        self.testingLabel.hide()
        self.errorLabel.hide()

        self.yesButton.setText('确认')
        self.cancelButton.setText('取消')

        self.widget.setMinimumWidth(350)

    def validate(self):
        self.errorLabel.hide()
        self.testingLabel.setHidden(False)
        self.yesButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        self.worker = TestWorkerDomin(self.urlLineEdit.text())
        self.worker.finished.connect(self.onTestFinished)
        self.worker.domin_ready.connect(self.init_combox)
        self.worker.start()

    def onTestFinished(self, isValid):
        self.testingLabel.setHidden(True)
        self.yesButton.setEnabled(True)
        self.cancelButton.setEnabled(True)

        if isValid:
            self.accept()
        else:
            self.errorLabel.setHidden(False)
            self.urlLineEdit.setError(True)


def test_cookie(cookie, domin):
    try :
        url = api.Url.url_home
        content = api.GetContent.get_content(url=url, cookie=cookie)

        if (not content.code) or ("98堂[原色花堂]" not in content.content):
            return False, None  # 返回 False 和 None

        tree = etree.HTML(content.content)

        try:
            photo = tree.xpath(xpath.XpathOfHome.photo)
            photo = photo[0]
        except Exception :
            photo = ""
        try :
            name = tree.xpath(xpath.XpathOfHome.name)
            name = name[0]
        except Exception :
            name = '获取失败'
        try :
            uid = tree.xpath(xpath.XpathOfHome.uid)
            uid = str(uid[0]).split(")")[0].split(" ")[-1]
        except Exception :
            uid = '获取失败'
        try :
            group = tree.xpath(xpath.XpathOfHome.group)
            group = group[0]
        except Exception :
            group = '获取失败'
        try :
            score = tree.xpath(xpath.XpathOfHome.score)
            score = str(score[0]).replace(" ", "")
        except Exception :
            score = '获取失败'
        try :
            money = tree.xpath(xpath.XpathOfHome.money)
            money = str(money[0]).replace(" ", "")
        except Exception :
            money = '获取失败'
        try :
            rate = tree.xpath(xpath.XpathOfHome.rate)
            rate = str(rate[0]).replace(" ", "")
        except Exception :
            rate = '获取失败'
        try :
            coin = tree.xpath(xpath.XpathOfHome.coin)
            coin = str(coin[0]).replace(" ", "")
        except Exception :
            coin = '获取失败'

        update_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        if photo == "":
            shutil.copy(folder_path + '/default.gif', folder_path + f'/{name}.gif')
        else:
            folder_path = resource_path('./Resource/cache/photo')
            down_sign = photo_downloader.download_photo(url=photo, username=name, domin=domin, cookie=cookie)
            if not down_sign:
                is_photo_exist = (Path(folder_path) / f'{name}.gif').is_file()
                if not is_photo_exist:
                    shutil.copy(folder_path+'/default.gif', folder_path+f'/{name}.gif')
        user = User(cookie=cookie, update_time=update_time, name=name, uid=uid, group=group, score=score, money=money, rate=rate, coin=coin)
        print(user)
        obj = json.load(open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8'))
        users = obj["data"]["users"]

        for i, u in enumerate(users):
            if u["uid"] == uid:
                del users[i]
        users.append({
            "main": 0,
            "cookie": cookie,
            "update_time": update_time,
            "name": name,
            "uid": uid,
            "group": group,
            "score": score,
            "money": money,
            "rate": rate,
            "coin": coin
        })
        obj["data"]["users"] = users
        with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf') as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)

        return True, user  # 返回 True 和 User 对象
    except Exception as e:
        return False, e


class TestWorker(QThread):
    finished = Signal(bool)  # 任务完成信号，传递验证结果
    user_ready = Signal(User)  # 新增信号，用于传递 User 对象

    def __init__(self, cookie, domin, parent=None):
        super().__init__(parent)
        self.cookie = cookie
        self.domin = domin

    def run(self):
        res, user = test_cookie(self.cookie, self.domin)  # 修改 test_cookie 返回 User 对象
        if res:
            self.user_ready.emit(user)  # 传递 User 对象
        self.finished.emit(res)  # 传递验证结果

class CustomMessageBox(MessageBoxBase):
    def __init__(self, title, contnet, parent=None):
        super().__init__(parent)
        self.worker = None
        self.titleLabel = SubtitleLabel(f'{title}', self)
        self.urlLineEdit = LineEdit(self)

        if parent is not None:
            self.domin = parent.domin
            self.add_user_card = parent.add_user_card

        self.urlLineEdit.setPlaceholderText('请完整输入cookie，不要带多余空格')

        if contnet != '':
            self.urlLineEdit.setText(contnet)

        self.testingLabel = CaptionLabel("正在测试cookie……", self)
        self.testingLabel.setStyleSheet("color: #cf1010;")
        self.errorLabel = CaptionLabel("error: 网络错误/cookie无效，请重试", self)
        self.errorLabel.setStyleSheet("color: #cf1010;")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)
        self.viewLayout.addWidget(self.testingLabel)
        self.viewLayout.addWidget(self.errorLabel)
        self.testingLabel.hide()
        self.errorLabel.hide()

        self.yesButton.setText('确认')
        self.cancelButton.setText('取消')

        self.widget.setMinimumWidth(350)

    def validate(self):
        self.errorLabel.hide()
        self.testingLabel.setHidden(False)
        self.yesButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        self.worker = TestWorker(self.urlLineEdit.text(), self.domin)
        self.worker.finished.connect(self.onTestFinished)
        self.worker.user_ready.connect(self.add_user_card)  # 连接 user_ready 信号
        self.worker.start()

    def onTestFinished(self, isValid):
        self.testingLabel.setHidden(True)
        self.yesButton.setEnabled(True)
        self.cancelButton.setEnabled(True)

        if isValid:
            self.accept()
        else:
            self.errorLabel.setHidden(False)
            self.urlLineEdit.setError(True)

class SettingPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("SettingPage")
        self.setStyleSheet("""
            #SettingPage {
                border: 1px solid rgb(229, 229, 229);
                background-color: rgb(249, 249, 249);
                border-radius : 10px;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 让 QWidget 使用样式背景
        self.setMinimumWidth(600)
        self.user_list = []
        self.domin = "https://sehuatang.net"
        self.cards = []

        # 选项区域
        add_widget = QWidget()
        add_widget.setObjectName("addwidget")
        add_widget.setStyleSheet("""
            #addwidget {
                background-color: rgb(240, 240, 240);  /* 设置背景色 */
                border: 1px solid rgb(200, 200, 200);  /* 设置边框 */
                border-radius: 10px;  /* 设置圆角 */
            }
        """)
        add_widget.setFixedSize(300, 130)
        add_widget.setAttribute(Qt.WA_StyledBackground, True)  # 让 QWidget 使用样式背景
        add_layout = QVBoxLayout(add_widget)
        add_widget.setLayout(QHBoxLayout())

        # 域名选择下拉菜单
        self.comboBox = ComboBox(self)
        self.comboBox.setPlaceholderText("选择域名")

        self.init_combox('')
        self.comboBox.currentTextChanged.connect(self.change_domin)
        add_layout.addWidget(self.comboBox)

        # 添加域名按钮
        add_domin_button = PushButton('增加域名', self)
        add_domin_button.clicked.connect(lambda: self.showDialogDomin('输入域名', ''))
        add_layout.addWidget(add_domin_button)

        # 添加用户按钮
        add_user_button = PushButton('添加账号', self)
        add_user_button.clicked.connect(lambda: self.showDialog('输入账号Cookie', ''))
        add_layout.addWidget(add_user_button)

        # 用户卡片布局
        self.content_layout = QVBoxLayout()
        self.content_layout.setAlignment(Qt.AlignTop)  # 让内容靠上对齐

        # 用户卡片界面
        scroll_widget = QWidget()
        scroll_widget.setObjectName("scroll_widget")
        scroll_widget.setStyleSheet("""
                    #scroll_widget {
                        border-radius: 10px;
                    }
                """)
        scroll_widget.setLayout(self.content_layout)

        # 滚动区域
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)  # 允许自动调整大小
        self.scroll_area.setWidget(scroll_widget)  # 设置 QWidget 为滚动区域的内容
        self.scroll_area.setStyleSheet("""
                    ScrollArea {
                        background-color: rgb(240, 240, 240);  /* 设置背景色 */
                        border: 1px solid rgb(200, 200, 200);  /* 设置边框 */
                        border-radius: 10px;  /* 设置圆角 */
                    }
                """)

        # 设置主布局
        setting_page_layout = QVBoxLayout()
        setting_page_layout.addWidget(add_widget)
        setting_page_layout.addWidget(self.scroll_area)  # 使用self.scroll_area添加到主布局中
        self.setLayout(setting_page_layout)

        self.init_user()

    def change_domin(self, text):
        obj = json.load(open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8'))
        domins = obj["data"]["domin"]
        domins.remove(text)
        domins.append(text)
        obj["data"]["domin"] = domins
        with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)
        self.domin = text

    def init_combox(self, domin):
        obj = json.load(open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8'))
        domin_list = obj["data"]["domin"]
        if domin != '':
            if domin in domin_list:
                domin_list.remove(domin)
            domin_list.append(domin)
            obj["data"]["domin"] = domin_list
            with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf') as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)
        self.comboBox.clear()
        self.comboBox.addItems(domin_list)
        self.comboBox.setCurrentIndex(len(domin_list)-1)

    def add_user_card(self, user_info):

        for i, card in enumerate(self.cards):
            if card.user.name == user_info.name:
                del self.cards[i]
                card.delete_card()
        card = UserCard(user_info, self)
        self.cards.append(card)
        self.content_layout.addWidget(card)


    def init_user(self):
        obj = json.load(open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8'))
        users = obj["data"]["users"]

        for u in users:
            if u["name"] == "":
                continue
            u_t = User(cookie=u['cookie'], name=u['name'], update_time=u['update_time'], uid=u['uid'], group=u['group'],
                       score=u['score'], money=u['money'], rate=u['rate'], coin=u['coin'])
            self.user_list.append(u_t)

        # 页面内容 - 用户卡片
        for u in self.user_list:
            self.add_user_card(u)

    def showSuccessMessage(self, content):
        InfoBar.success(
            title='成功',
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.parent()
        )

    def showDialogDomin(self, title, content):
        w = CustomMessageBoxDomin(self)
        if w.exec():
            self.showSuccessMessage("域名已添加")

    def showDialog(self, title, content):
        w = CustomMessageBox(title, content, self)
        if w.exec():
            self.showSuccessMessage("账号已添加/更新")
