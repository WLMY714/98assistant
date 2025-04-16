
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from qfluentwidgets import ScrollArea, TextBrowser, TextEdit

from Components.question_card import ExpandableQuestion

class HelpPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("HelpPage")
        self.setStyleSheet("""
            #HelpPage {
                border: 1px solid rgb(229, 229, 229);
                background-color: rgb(249, 249, 249);
                border-radius : 10px;
            }
        """)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 让 QWidget 使用样式背景
        self.setMinimumWidth(600)

        # 主布局
        main_layout = QVBoxLayout(self)

        # 滚动区域
        scroll_area = ScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("helpScroll")
        scroll_area.setStyleSheet("""
            #helpScroll {
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
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        content_layout = QVBoxLayout(content_widget)
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        question1 = 'Q1：如何获取cookie？'
        answer1 = TextBrowser(self)
        answer1.setMarkdown("🎈第一步：浏览器打开网站，正常登录账号\n\n"
                            "🎈第二步：按F12打开控制台，点网络（或Network）\n\n"
                            "🎈第三步：刷新网页，在控制台找到第一个html网络文件，点击打开\n\n"
                            "🎈第四步：找到“请求标头”的“cookie”，完整复制即可\n\n"
                            ".\n\n"
                            "✅以堂的cookie为例，cookie大致为：cPNj_2132_saltkey=LN7x……3425%09home.php%09spacecp;\n\n"
                            "✅cookie很长，注意完整复制，仍有困难可参考图片教程“如何获取cookie.png”\n\n"
                            "✅cookie时效看服务器检测，几分钟或者几个月，堂的cookie短时间不会失效，半个月更新一次都行，重复添加已经添加的账号，就可以更新cookie")
        card1 = ExpandableQuestion(question1, answer1, self)
        content_layout.addWidget(card1)

        question1_1 = 'Q2：头像是默认头像，或者账号信息显示获取失败？'
        answer1_1 = TextBrowser(self)
        answer1_1.setMarkdown("🧡方法1：在安装目录的\\Resource\\cache中的“data.json”中手动修改账号信息，在\\Resource\\cache\\photo文件夹中添加账号同名的gif图（用户名.gif，其他格式的图片要转换成gif格式）\n\n"
                              "💌方法2：联系作者更新软件")
        card1_1 = ExpandableQuestion(question1_1, answer1_1, self)
        content_layout.addWidget(card1_1)

        question2 = 'Q3：签到流程？'
        answer2 = TextBrowser(self)
        answer2.setMarkdown("✨1、先检测选中的账号能否正常签到（是否重复签到？网络有没有问题？）\n\n"
                            "✨2、如果可以签到，则进行签到，没有回复的话会先找个帖子回复\n\n"
                            "✨3、签到完成后，会反馈签到结果，在签到记录中点击记录可以查看回复的帖子和回复的内容\n\n"
                            ".\n\n"
                            "🍳回复帖子：限定【国产原创区、亚洲有码原创区、亚洲无码原创区】按时间排序的【20~40】页（共600个帖子）随机选一贴\n\n"
                            "🍳回复内容：提前设定好的400个万金油回复，随机选一个回复\n\n"
                            ".\n\n"
                            "✅修改或添加回复内容，可以在安装目录文件夹\\Resource\\cache中的“data.json”中修改")
        card2 = ExpandableQuestion(question2, answer2, self)
        content_layout.addWidget(card2)

        question3 = 'Q4：签到常遇问题'
        answer3 = TextBrowser(self)
        answer3.setMarkdown("❓为什么签到时间很久甚至签到失败？\n\n"
                            "✅因为网络原因，或者论坛有每分钟签到账号数量限制，签到失败后，程序会休眠1分钟左右重新尝试签到，最多失败3次反馈结果\n\n"
                            ".\n\n"
                            "❓为什么签到记录点开后没有看到账号的回复？\n\n"
                            "✅有时候成功回复后，出现了上述问题，程序休眠了，再次尝试签到时换了一个帖子，这种问题可以自行登录账号查看")
        card3 = ExpandableQuestion(question3, answer3, self)
        content_layout.addWidget(card3)

        question4 = 'Q5：评分流程？'
        answer4 = TextBrowser(self)
        answer4.setMarkdown("✨1、先选中【执行签到行为的账号】和被评分的【帖子tid】或【用户名】，点击相应的【开始评分】按钮\n\n"
                            "✨2、如果是【帖子tid】，则会直接评分，因此添加时注意不要添加悬赏区的tid\n\n"
                            "✨3、如果是【用户名】，则会寻找这些用户个人主页【主题】【第一页】的发帖记录中，合法板块的第一个帖子进行评分\n\n"
                            "（因此注意如果【主题第一页】没有帖子，或者帖子全不在合法版块，如全是悬赏区帖子，则会签到失败）\n\n"
                            ".\n\n"
                            "🍳合法板块：限定【综合讨论区，网友原创区，AI专区，资源出售区，新作区，自提字幕区，自译字幕区，原创自拍区（某南专属）】\n\n"
                            "🍳回复与提醒：评分后会提醒楼主已评分，但不会留下评分留言\n\n"
                            "🍳评分分数：在【能评的最大值】和【剩余评分】之间取最大值评分")
        card4 = ExpandableQuestion(question4, answer4, self)
        content_layout.addWidget(card4)

        question5 = 'Q6：为什么新作预告的日历选择框点了没反应还有点卡？'
        answer5 = TextBrowser(self)
        answer5.setMarkdown("😐因为这个模型有点大，有时候点击会卡顿一下，重复点击就关闭了\n\n"
                            "😕所以点击一下后等3~5秒模型加载出来即可，不要重复点击")
        card5 = ExpandableQuestion(question5, answer5, self)
        content_layout.addWidget(card5)

        question6 = 'Q7：新作预告的日期？'
        answer6 = TextBrowser(self)
        answer6.setMarkdown("🎁本周预告的新作配信日应当是从本周起的第4个周五（本周五是第1个），若本周有5个周二，则是第5个周五\n\n"
                            "🎀日期是fanza网站中，影片详情页的【配信開始日】（周五），而不是预告页面显示的【配信日】，显示的时间会比实际时间早一天")
        card6 = ExpandableQuestion(question6, answer6, self)
        content_layout.addWidget(card6)

        question7 = 'Q8：新作预告获取失败？'
        answer7 = TextBrowser(self)
        answer7.setMarkdown("🧐首先确保开启了日本节点\n\n"
                            "💔其次检查配信日期是否选择正确，参考问题7\n\n"
                            "😢打开FANZA官网的预告页查看这天的预告是否已经发布\n\n"
                            "网址：https://video.dmm.co.jp/av/list/?release=reservation&sort=date&limit=120")
        card7 = ExpandableQuestion(question7, answer7, self)
        content_layout.addWidget(card7)

        question8 = 'Q9：软件中显示的文件夹，本地磁盘删除了但是软件里还显示？'
        answer8 = TextBrowser(self)
        answer8.setMarkdown("💖软件里面不会实时刷新系统文件夹，只是虚拟显示，磁盘删除后关闭软件重启即可")
        card8 = ExpandableQuestion(question8, answer8, self)
        content_layout.addWidget(card8)

        content_layout.setAlignment(Qt.AlignTop)
        content_layout.addStretch()
