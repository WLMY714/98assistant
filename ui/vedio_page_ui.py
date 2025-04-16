
import os
import sys
import json

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

from Components.question_card import ExpandableQuestion
from Components.task_card import CardWidget
from Components.folder_card import FolderIconWidget
from Api import fanza_vedio
from Api.fanza_vedio import Downloader
from Utils.path_resolver import resource_path
from Utils.multi_threaded_downloader import MultiThreadedDownloader


def is_within_one_month(target_date_str: str) -> bool:
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    today = datetime.today().date()
    one_month_later = today + relativedelta(months=2)

    return today <= target_date <= one_month_later

def download(code, cookie, date):

    dl = Downloader(code=code, cookie=cookie, date=date)
    filename = dl.filename
    result = {
        "content": dl,
        "code": code,
        "path": resource_path(f"./Resource/cache/file/{filename}"),
        "name": filename,
        "icon": resource_path('./Resource/image/file.png'),
        "is_new": True
    }

    return result

class DownloadThread(QThread):
    # 获取fanza数据
    start_get_fanza = Signal(str)
    end_get_fanza = Signal(str)
    # 获取屏蔽词
    start_ban = Signal(str)
    end_ban = Signal(str)
    # 保存链接文件
    start_save_url = Signal(str)
    end_save_url = Signal(str)
    # 下载图片
    start_download_pic = Signal(str)
    end_download_pic = Signal(str)
    # 下载视频
    start_download_vedio = Signal(str)
    end_download_vedio = Signal(str)
    # 保存用户专属文件
    start_save_user = Signal(str)
    end_save_user = Signal(str)
    #结束
    task_finished = Signal(dict)

    def __init__(self, code: str, cookie: str, date: str):
        super().__init__()
        self.code = code
        self.cookie = cookie
        self.date = date

    def run(self):

        task_result = download(self.code, self.cookie, self.date)

        self.start_ban.emit('🍳正在获取屏蔽词……')
        task_result["content"].ban_words = fanza_vedio.get_ban_words()
        self.start_ban.emit('✅屏蔽词获取完成！')

        self.start_get_fanza.emit('🍳正在获取Fanza数据……')
        task_result["content"].solve_movie_list()
        self.end_get_fanza.emit('✅Fanza数据获取完成！')

        self.start_save_url.emit('🔗正在保存链接文件……')
        fanza_vedio.save_3(
            task_result["content"].filename,
            task_result["content"].makers,
            task_result["content"].movie_list
        )
        self.end_save_url.emit('✅链接文件保存完成！')

        if self.code == 'r3698t':
            self.start_save_user.emit('👑正在保存 R哥 帖子模板……')
            fanza_vedio.create_r_post(
                task_result["content"].get_day,
                task_result["content"].makers,
                task_result["content"].movie_list,
                task_result["content"].filename
            )
            self.end_save_user.emit('🎉R哥 帖子模板保存完成！')
        elif self.code == 'lbsl98t':
            self.start_save_user.emit('👑正在保存 礼部侍郎 帖子模板……')
            fanza_vedio.create_lbsl_post(
                task_result["content"].get_day,
                task_result["content"].makers,
                task_result["content"].movie_list,
                task_result["content"].filename
            )
            self.end_save_user.emit('🎉礼部侍郎 帖子模板保存完成！')
        elif self.code == 'lbsl98t-l':
            self.start_save_user.emit('👑正在保存 礼部侍郎 帖子模板……')
            fanza_vedio.create_lbsl_post(
                task_result["content"].get_day,
                task_result["content"].makers,
                task_result["content"].movie_list,
                task_result["content"].filename
            )
            self.end_save_user.emit('🎉礼部侍郎 帖子模板保存完成！')
        elif self.code == 'yut98t':
            self.start_save_user.emit('👑正在保存 YUt 帖子模板……')
            fanza_vedio.create_yut_post(
                task_result["content"].get_day,
                task_result["content"].movie_list,
                task_result["content"].filename
            )
            self.end_save_user.emit('🎉YUt 帖子模板保存完成！')
        elif self.code == 'yut98t-l':
            self.start_save_user.emit('👑正在保存 YUt 帖子模板……')
            fanza_vedio.create_yut_post(
                task_result["content"].get_day,
                task_result["content"].movie_list,
                task_result["content"].filename
            )
            self.end_save_user.emit('🎉YUt 帖子模板保存完成！')

        if self.code in ['2', '3', 'yut98t', 'lbsl98t', 'r3698t']:
            task_number = 0
            isyut = True if self.code == 'yut98t' else False
            vp_downloader = MultiThreadedDownloader(isyut=isyut, max_workers=10, timeout=60)
            futures = []
            for movie in task_result["content"].movie_list:
                path = resource_path(f'./Resource/cache/file/{task_result["content"].filename}')
                if self.code == 'yut98t':
                    path = str(path) + '/' + f'www.98t.la@{movie["maker"]}'
                else :
                    path = str(path) + '/' + movie["maker"]
                if self.code in ['2', 'yut98t', 'lbsl98t', 'r3698t']:
                    filename = movie["face"].split("/")[-1]
                    filename = filename.replace("pl", "").replace("hhb", "")  # 去除 "pl" 或 "hhb"
                    self.start_download_pic.emit(f'📸开始下载：{filename}')
                    task_number += 1
                    futures.append(vp_downloader.download_file(url=movie["face"], save_dir=path))
                if self.code in ['3', 'yut98t']:
                    filename = movie["vedio"].split("/")[-1]
                    filename = filename.replace("pl", "").replace("hhb", "")  # 去除 "pl" 或 "hhb"
                    self.start_download_vedio.emit(f'🎬开始下载：{filename}')
                    task_number += 1
                    futures.append(vp_downloader.download_file(url=movie["vedio"], save_dir=path))

            finish_num = 1
            for future in as_completed(futures):
                res = future.result()
                if '失败' in res :
                    self.end_download_pic.emit(f'❌({finish_num}/{task_number})' + res)
                elif '完成' in res :
                    self.end_download_pic.emit(f'✅({finish_num}/{task_number})' + res)
                finish_num += 1


        self.task_finished.emit(task_result)


class CustomMessageBox(MessageBoxBase):
    """ Custom message box """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('输入功能码', self)
        self.urlLineEdit = LineEdit(self)

        self.urlLineEdit.setPlaceholderText('在此输入')
        self.urlLineEdit.setClearButtonEnabled(True)

        self.warningLabel = CaptionLabel("输入功能码无效")
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
        isValid = False
        valid_code = ['1', '2', '3', 'lbsl98t', 'yut98t', 'r3698t', 'lbsl98t-l', 'yut98t-l']
        if self.urlLineEdit.text() in valid_code :
            isValid = True
        self.warningLabel.setHidden(isValid)
        self.urlLineEdit.setError(not isValid)
        return isValid

class VedioPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("VedioPage")
        self.setStyleSheet("""
            #VedioPage {
                border: 1px solid rgb(229, 229, 229);
                background-color: rgb(249, 249, 249);
                border-radius : 10px;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 让 QWidget 使用样式背景
        self.setMinimumWidth(600)

        self.fanza_cookie = ""
        self.fanza_date = ""
        self.file_list = []
        self.code = "1"
        self.download_thread = []
        self.downloading = None

        main_layout = QVBoxLayout(self)

        setting_widget = QWidget()
        setting_layout = QGridLayout(setting_widget)

        # cookie行
        # cookie图标
        cookie_icon = QLabel()
        cookie_icon.setPixmap(QPixmap(resource_path("./Resource/image/cookie.png")))
        cookie_icon.setFixedSize(24, 24)
        cookie_icon.setScaledContents(True)
        setting_layout.addWidget(cookie_icon, 0, 0)
        # cookie标签
        cookie_label = QLabel(" FANZA Cookie：")
        setting_layout.addWidget(cookie_label, 0, 1, 1, 2)
        # cookie内容
        self.cookie_edit = LineEdit()
        self.cookie_edit.setPlaceholderText("输入FANZA账号的cookie")
        self.cookie_edit.setText('top_dummy=01d724ab-1444-4905-b85a-98d70960c7a8; uid=QJlFpjyCCqZUZglfQLBG; suid=QJlFpjyCCqZUZglfQLBG; rieSh3Ee_ga=GA1.1.2090002890.1720154938; _yjsu_yjad=1720154937.a210dbea-61b6-4a1c-874f-488558faa658; adpf_uid=YqMNohFLBavMDshs; i3_ab=2fa0c07d-9389-400a-9499-7a831e460946; _gcl_au=1.1.1549709294.1736264676; FPID=FPID2.3.iV6XAq%2BfU2%2BguV3hIohePvqEGHXDQf%2FWRB%2BBu4R7K%2FI%3D.1720154938; FPAU=1.3.1675289702.1736264678; _tt_enable_cookie=1; _ttp=fX_CEPsOAkMk_mVnuBeyquCFZ_V.tt.2; guest_id=BBJaWA5AVUdQDAFb; digital[play_volume]=0.65; cklg=ja; check_done_login=true; cdp_id=1JT5HWgzRGs88jhB; rieSh3Ee_ga_KQYE0DE5JW=deleted; _fbp=fb.2.1737797832720.826011200583805379; alcb=true; pt_21j2m5ao=deviceId%3D6cc013fd-e36f-4e29-97cc-5642b7ddb261%26sessionId%3Dbb422d65-2172-4313-a931-86ca779a8a6f%26accountId%3D1JT5HWgzRGs88jhB%26vn%3D5%26pvn%3D1%26lastActionTime%3D1739970313535%26; digital[play_muted]=1; subscription_members_status=non; secid=37857f75fde8d5519e542590735e2f08; login_secure_id=37857f75fde8d5519e542590735e2f08; age_check_done=1; d_mylibrary=nINks%2BxgI%2F1I329WV6UBoA%3D%3D; ixd_lastclick=6828,1743434808; dig_history=mdon00074%2C1start00305%2Cvrkm01533%2Ccawd00818%2Cwaaa00516%2Cwaaa00518%2Cmmpb00076%2Cwaaa00497%2Csame00162%2Cmida00106%2Cmida00150%2Catad00189%2Cadn00669%2Clulu00375%2Cadn00668%2Ch_1711fch00101%2Cipvr00300%2Cipzz00170%2Csame00157%2Creal00905%2Cpfes00107%2Cvenz00052%2Csone00707%2Csykh00142%2Cjur00285%2Csone00687%2Coae00275%2Cmkmp00631%2Cbibivr00150%2Cktra00706%2Ch_1472erhav00037%2Cmida00039%2Cipbz00013%2C1start00273v%2Cmaqq00002%2Cdmdg00060%2Caukg00625%2Cmyba00081%2Ckdmi00064%2Chmn00691; top_pv_uid=b89e9ad5-c4d9-48fa-bbc1-d3d6a8bde6a3; is_intarnal=true; sort_search=eyJzb3J0IjoicmFua3Byb2ZpbGUiLCJsaW1pdCI6IjMwIn0%3D; _clck=12plec7%7C2%7Cfuu%7C0%7C1840; dmm_service=BFsBAx1FWwQCR1JXXlsJWUNeVwwBAx9KWFYNREEKRURHWkMDUQxDQFkLWlFdUUQMHBg_; _clsk=5p6j3q%7C1743915514301%7C2%7C0%7Cv.clarity.ms%2Fcollect; ckcy=1; FPLC=asH4rZxGpWBtetqynC60lmNlTjYJeT2Qgq0sZIrHberGORTqGcTsnamZZaruQLaPatfKsTWFJEhA%2BIs6vJQ4Nsbhmn8StWj8ss%2BQyGj18ch41Z4m5UT09Z9iqAhycw%3D%3D; rieSh3Ee_ga_KQYE0DE5JW=GS1.1.1743959658.50.1.1743959664.0.0.1392379379')
        setting_layout.addWidget(self.cookie_edit, 0, 3, 1, 11)

        # 日期行
        # 日期图标
        date_icon = QLabel()
        date_icon.setPixmap(QPixmap(resource_path("./Resource/image/calendar.png")))
        date_icon.setFixedSize(24, 24)
        date_icon.setScaledContents(True)
        setting_layout.addWidget(date_icon, 1, 0)
        # 日期标签
        date_label = QLabel(" 配信开始日：")
        setting_layout.addWidget(date_label, 1, 1, 1, 2)
        # 日期内容
        date_picker = CalendarPicker(self)
        date_picker.setText('选择日期（加载可能较慢，勿重复点击）')
        date_picker.dateChanged.connect(self.on_date_changed)
        setting_layout.addWidget(date_picker, 1, 3, 1, 6)

        # 功能码行
        # 功能码图标
        code_icon = QLabel()
        code_icon.setPixmap(QPixmap(resource_path("./Resource/image/code.png")))
        code_icon.setFixedSize(24, 24)
        code_icon.setScaledContents(True)
        setting_layout.addWidget(code_icon, 2, 0)
        # 功能码标签
        code_label = QLabel(" 功能码选择：")
        setting_layout.addWidget(code_label, 2, 1, 1, 2)
        # 功能码内容
        self.code_picker = ComboBox(self)
        self.init_code_picker()
        self.code_picker.currentTextChanged.connect(self.change_code)
        setting_layout.addWidget(self.code_picker, 2, 3, 1, 6)
        # 功能码按钮
        code_add_btn = PushButton(text='添加功能码', parent=self)
        code_add_btn.clicked.connect(self.add_code)
        setting_layout.addWidget(code_add_btn, 2, 9, 1, 2)

        # 功能码介绍行
        # 功能码介绍图标
        introduce_icon = QLabel()
        introduce_icon.setPixmap(QPixmap(resource_path("./Resource/image/code_introduce.png")))
        introduce_icon.setFixedSize(24, 24)
        introduce_icon.setScaledContents(True)
        setting_layout.addWidget(introduce_icon, 3, 0)
        # 功能码介绍标签
        introduce_label = QLabel(" 功能码介绍：")
        setting_layout.addWidget(introduce_label, 3, 1, 1, 2)
        # 功能码介绍内容
        introduce_text = TextBrowser(self)
        introduce_text.setMarkdown("🎈功能码【1】：获取FANZA详情页面、高清预告封面、高清预告视频链接\n\n"
                                   "🎈功能码【2】：下载高清预告封面\n\n"
                                   "🎈功能码【3】：下载高清预告视频(耗时较长、消耗流量较多)\n\n"
                                   ".\n\n"
                                   "✅可添加用户专属功能码\n\n"
                                   "✅软件使用疑问、新作预告日期选择等问题，可参考【常见问题】板块相关答疑")
        setting_layout.addWidget(introduce_text, 3, 3, 1, 11)

        # 屏蔽词按钮行
        # 屏蔽词按钮图标
        ban_btn_icon = QLabel()
        ban_btn_icon.setPixmap(QPixmap(resource_path("./Resource/image/cancel.png")))
        ban_btn_icon.setFixedSize(24, 24)
        ban_btn_icon.setScaledContents(True)
        setting_layout.addWidget(ban_btn_icon, 4, 0)
        # 屏蔽词按钮标签
        introduce_label = QLabel(" 屏蔽词列表：")
        setting_layout.addWidget(introduce_label, 4, 1, 1, 2)
        self.ban_btn = PushButton(text='打开屏蔽列表', parent=self)
        self.ban_btn.clicked.connect(self.open_ban)
        setting_layout.addWidget(self.ban_btn, 4, 3, 1, 11)

        # 开始按钮行
        # 开始按钮图标
        start_btn_icon = QLabel()
        start_btn_icon.setPixmap(QPixmap(resource_path("./Resource/image/start.png")))
        start_btn_icon.setFixedSize(24, 24)
        start_btn_icon.setScaledContents(True)
        setting_layout.addWidget(start_btn_icon, 5, 0)
        # 开始按钮标签
        introduce_label = QLabel(" 开始获取：")
        setting_layout.addWidget(introduce_label, 5, 1, 1, 2)
        self.start_btn = PrimaryPushButton(text='获取新作预告', parent=self)
        self.start_btn.clicked.connect(self.start_download)
        setting_layout.addWidget(self.start_btn, 5, 3, 1, 11)

        # setting卡片
        setting_card = CardWidget(title='基础设置', content_widget=setting_widget)
        main_layout.addWidget(setting_card)

        task_layout = QHBoxLayout()

        message_widget = QWidget()
        self.message_layout = QVBoxLayout(message_widget)
        self.message_layout.addStretch()
        # message_widget.setMinimumWidth(250)
        message_scroll = ScrollArea()
        message_scroll.setWidgetResizable(True)
        message_scroll.setWidget(message_widget)
        message_scroll.setObjectName('messageScroll')
        message_scroll.setStyleSheet("""
                    #messageScroll {
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
        message_card = CardWidget(title='进度', content_widget=message_scroll)

        content_widget = QWidget()
        self.content_layout = FlowLayout(content_widget)
        content_widget.setMinimumHeight(100)
        content_scroll = ScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setWidget(content_widget)
        content_scroll.setObjectName('contentScroll')
        content_scroll.setStyleSheet("""
            #contentScroll {
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
        content_card = CardWidget(title='新作文件', content_widget=content_scroll)

        task_layout.addWidget(message_card)
        task_layout.addWidget(content_card)
        task_layout.setStretch(0, 3)
        task_layout.setStretch(1, 7)

        main_layout.addLayout(task_layout)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 5)

        self.init_widget()

    def download_tip(self):
        if self.downloading:
            self.downloading.setContent('新作预告获取完成！😎')
            self.downloading.setTitle('任务完成')
            self.downloading.setState(True)
            self.downloading = None
        else:
            self.downloading = StateToolTip('任务进行中', f'正在获取 {self.fanza_date} 的新作预告……😴', self)
            width = self.width()
            self.downloading.move(width-300, 20)
            self.downloading.show()

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

    def add_message(self, message):
        if len(message) > 30 :
            message = message[:30] + '...'
        msg_label = QLabel(text=message, parent=self)
        self.message_layout.insertWidget(0, msg_label)

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

    def open_ban(self):
        try :
            file = os.path.abspath(resource_path('./Resource/text/屏蔽关键词.txt'))
            if os.path.exists(file):
                os.startfile(file)  # Windows 中直接打开文件
            else:
                return
        except Exception as e:
            return

    def add_folder(self, file_info):
        card = FolderIconWidget(file_info["path"], file_info["name"], file_info["icon"], is_new=file_info["is_new"], parent=self)
        self.content_layout.insertWidget(0, card)

        if file_info["is_new"]:
            self.start_btn.setEnabled(True)
            self.add_message(f'✅任务完成，本次获取 {len(file_info["content"].movie_list)} 部预告信息')
            if len(file_info["content"].movie_list) < 60:
                self.add_message('❓若获取过少请检查是否开启日本节点，或重启软件重试')
                self.add_message('❓周二发布预告通常在75部以上')
            self.add_message(f'💠💠💠💠💠💠💠💠💠💠💠💠')
            self.download_tip()

    def init_widget(self):
        folder = resource_path('./Resource/cache/file')
        file_list = [name for name in os.listdir(folder)
                     if os.path.isdir(os.path.join(folder, name)) and '新作' in name]

        for file in file_list:
            path = os.path.join(folder, file)
            file_info = {'path': path, 'name': file, 'icon': resource_path('./Resource/image/file.png'), 'is_new': False}
            self.add_folder(file_info)

    def on_date_changed(self, date: QDate):
        self.fanza_date = date.toString("yyyy-MM-dd")

    def init_code_picker(self, code=None):
        is_re = False
        with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        code_list = obj['fanza']['code']
        if code is not None:
            if code in code_list:
                is_re = True
                code_list.remove(code)
            code_list.append(code)
            with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)
        self.code_picker.clear()
        self.code_picker.addItems(code_list)
        self.code_picker.setCurrentIndex(len(code_list)-1)
        self.code = code_list[-1]
        if is_re:
            self.success_message('功能码已选择')
        else :
            self.success_message('功能码已添加')

    def change_code(self, text):
        with open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8') as f:
            obj = json.load(f)
        obj['fanza']['code'].remove(text)
        obj['fanza']['code'].append(text)
        with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)
        self.code = text

    def add_code(self):
        w = CustomMessageBox(self)
        if w.exec():
            self.code = w.urlLineEdit.text()
            self.init_code_picker(w.urlLineEdit.text())

    def start_download(self):

        if self.fanza_date == "":
            self.warnning_meaages('未选择日期')
            return
        if not is_within_one_month(self.fanza_date):
            self.warnning_meaages('仅能获取未来两个月内的新作预告')
            return

        self.fanza_cookie = self.cookie_edit.text()
        self.start_btn.setEnabled(False)
        self.download_tip()

        thread = DownloadThread(code=self.code, cookie=self.fanza_cookie, date=self.fanza_date)

        thread.start_get_fanza.connect(self.add_message)
        thread.end_get_fanza.connect(self.add_message)

        thread.start_ban.connect(self.add_message)
        thread.end_ban.connect(self.add_message)

        thread.start_save_url.connect(self.add_message)
        thread.end_save_url.connect(self.add_message)

        thread.start_download_pic.connect(self.add_message)
        thread.end_download_pic.connect(self.add_message)

        thread.start_download_vedio.connect(self.add_message)
        thread.end_download_vedio.connect(self.add_message)

        thread.start_save_user.connect(self.add_message)
        thread.end_save_user.connect(self.add_message)

        thread.task_finished.connect(self.add_folder)
        self.download_thread.append(thread)
        thread.start()

