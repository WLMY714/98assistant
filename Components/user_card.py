import random
import json

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, \
    QSizePolicy
from PySide6.QtGui import QPixmap, QIcon, QMovie
from PySide6.QtCore import Qt, QTimer

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import MessageBox

from Service import add_gif
from Utils.path_resolver import resource_path

class UserCard(QWidget):
    def __init__(self, user, parent=None):
        super().__init__()
        self.setFixedSize(630, 110)
        self.setObjectName("user_card")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.user = user
        self.parent = parent

        # 头像
        self.photo = QLabel()
        self.photo.setAlignment(Qt.AlignCenter)
        self.photo.setFixedSize(90, 90)  # 设置 QLabel 大小
        self.gif = QMovie(resource_path(f'./Resource/cache/photo/{user.name}.gif'))
        self.gif.frameChanged.connect(lambda: add_gif.updateFrame(self.photo, self.gif))
        self.gif.start()

        # 用户信息与资产
        self.user_name = QLabel(f'{self.user.name}', self)
        self.user_name.setStyleSheet(f'font-size: 17px bold; font-weight: bold;')
        self.user_id = QLabel(f'UID : {user.uid}', self)
        self.user_group = QLabel(f'{user.group}', self)
        self.user_group.setObjectName('user_group')
        self.score = QLabel(f'积分: {user.score}', self)
        self.money = QLabel(f'金钱: {user.money}', self)
        self.rate= QLabel(f'评分: {user.rate}', self)
        self.coin = QLabel(f'色币: {user.coin}', self)
        self.update_time = QLabel(f'更新: {user.update_time}', self)

        # 用户信息排列
        self.user_info_layout = QVBoxLayout()
        self.user_info_layout.addWidget(self.user_name)
        self.user_info_layout.addWidget(self.user_id)
        self.user_info_layout.addWidget(self.user_group)
        self.user_info_layout.addWidget(self.update_time)

        # 用户资产排列
        self.user_asset_layout = QVBoxLayout()
        self.user_asset_layout.addWidget(self.score)
        self.user_asset_layout.addWidget(self.money)
        self.user_asset_layout.addWidget(self.rate)
        self.user_asset_layout.addWidget(self.coin)

        # 按钮布局
        self.button_layout = QVBoxLayout()

        # 随机换色按钮
        self.update_button = QPushButton('随机皮肤', self)
        self.update_button.clicked.connect(self.change_color)
        self.button_layout.addWidget(self.update_button)
        self.update_button.setStyleSheet("""
            QPushButton {
                background: #8fdaf8;
                border-radius: 5px;
                border: 1px solid #f0f0f0;
                padding: 5px 1px;
            }
            QPushButton:hover {
                background-color: #03b9f2;
            }
            QPushButton:pressed {
                background-color: #03aeef;
            }
        """)

        # 信息更新按钮
        self.update_button = QPushButton('信息更新', self)
        self.update_button.clicked.connect(self.update_clicked)  # 点击删除按钮时的回调
        self.button_layout.addWidget(self.update_button)
        self.update_button.setStyleSheet("""
            QPushButton {
                background: #afd8a3;
                border-radius: 5px;
                border: 1px solid #f0f0f0;
                padding: 5px 1px;
            }
            QPushButton:hover {
                background-color: #3cba6d;
            }
            QPushButton:pressed {
                background-color: #01a756;
            }
        """)

        # 删除账号按钮
        self.delete_button = QPushButton('删除账号', self)
        self.delete_button.clicked.connect(self.on_delete_clicked)  # 点击删除按钮时的回调
        self.button_layout.addWidget(self.delete_button)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background: #f5afab;
                border-radius: 5px;
                border: 1px solid #f0f0f0;
                padding: 5px 1px;
            }
            QPushButton:hover {
                background-color: #f48677;
            }
            QPushButton:pressed {
                background-color: #ee1e25;
            }
        """)

        # 总体布局
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.photo)
        self.main_layout.addSpacing(15)
        self.main_layout.addLayout(self.user_info_layout)
        self.main_layout.addSpacing(15)
        self.main_layout.addLayout(self.user_asset_layout)
        self.main_layout.addSpacing(15)
        self.main_layout.addLayout(self.button_layout)

        self.change_color()

    def delete_card(self):
        self.gif.frameChanged.disconnect()
        # self.deleteLater()  # 删除当前卡片
        QTimer.singleShot(0, self.deleteLater)

    def showDialog(self, parent):
        title = '确定删除账号？'
        content = ""
        w = MessageBox(title, content, parent)
        w.setClosableOnMaskClicked(True)
        if w.exec():
            obj = json.load(open(resource_path('./Resource/cache/data.json'), 'r', encoding='utf-8'))
            obj["data"]["users"] = [u for u in obj["data"]["users"] if u["uid"] != self.user.uid]
            with open(resource_path('./Resource/cache/data.json'), 'w', encoding='utf') as f:
                json.dump(obj, f, ensure_ascii=False, indent=4)

            self.delete_card()
        else:
            pass

    def on_delete_clicked(self):
        self.showDialog(self.parent)

    def update_clicked(self):
        self.parent.showDialog('确认更新此Cookie？', self.user.cookie)
        # self.delete_card()

    def change_color(self):
        # 背景颜色列表
        color = [
            '#e8f2c7', '#fefcb4', '#fde8b8', '#fdd6c3',  # 你给的浅色
            '#f5f9e8', '#f4f1e1', '#f1e6d6', '#f9e0c5',
            '#f7e1d3', '#f1f5e3', '#f0f5e2', '#f7f7c4',
            '#f9f9a1', '#fbf9ab', '#fdf79e', '#fcf8c2',
            '#e9f7ca', '#e7f5b1', '#c9f4a5', '#c1f3a3',
            '#c8f4b4', '#c6f7d0', '#c9f7b7', '#d6f8b8',
            '#d8f4c4', '#d3f5bb', '#e0f5cb', '#e8f9cf',
            '#d1f6c7', '#f3f7d9', '#f8fbd9', '#eaf6cb'
        ]

        # 随机选择背景颜色
        background_color = random.choice(color)

        # 设置背景颜色
        self.setStyleSheet(f"""
            #user_card {{
                background-color: {background_color};
                border-radius: 10px;
                border: 1px solid rgb(229, 229, 229);
            }}
        """)

        # 设置用户组颜色（如果需要）
        group_color = ""
        if self.user.group == '原创精英':
            group_color = '#cc0000'  # 红色
        elif self.user.group == '荣耀精英':
            group_color = '#ff8c00'  # 橙色
        elif '版主' in self.user.group:
            group_color = '#0033ff'  # 蓝色

        # 如果有指定颜色，更新 `user_group` 字体颜色
        if group_color:
            self.setStyleSheet(f"""
                #user_card {{
                    background-color: {background_color};
                    border-radius: 10px;
                    border: 1px solid rgb(229, 229, 229);
                }}
                #user_group {{
                    color: {group_color};
                }}
            """)
