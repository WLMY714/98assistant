from qfluentwidgets import ToggleButton, SimpleCardWidget, FluentIcon as FIF, setTheme, Theme, IconWidget
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class IconToggleButton(ToggleButton):
    """优化图标大小的双态复选框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置更紧凑的按钮尺寸
        self.setFixedSize(20, 20)  # 减小按钮尺寸

        # 创建图标部件
        self.iconWidget = IconWidget(self)
        self.iconWidget.setFixedSize(12, 12)  # 减小图标尺寸
        self.iconWidget.move(4, 4)  # 调整图标位置

        # 初始状态
        self._updateIcon()

        # 状态变化时更新图标
        self.toggled.connect(self._updateIcon)

    def _updateIcon(self):
        """根据状态更新图标"""
        if self.isChecked():
            self.iconWidget.setIcon(FIF.ACCEPT)  # 选中状态显示对钩
        else:
            self.iconWidget.setIcon(QIcon())  # 未选中状态不显示任何图标（空图标）

        # 更新样式
        self.setStyleSheet(self._getStyleSheet())

    def _getStyleSheet(self):
        """获取当前状态的样式表"""
        if self.isChecked():
            return """
                IconToggleButton {
                    background-color: rgba(0, 90, 158, 0.1);
                    border: 1px solid rgba(0, 90, 158, 0.3);
                    border-radius: 4px;
                }
                IconToggleButton:hover {
                    background-color: rgba(0, 90, 158, 0.2);
                    border: 1px solid rgba(0, 90, 158, 0.5);
                }
            """
        else:
            return """
                IconToggleButton {
                    background-color: white;
                    border: 1px solid rgba(0, 0, 0, 0.2);
                    border-radius: 4px;
                }
                IconToggleButton:hover {
                    border: 1px solid rgba(0, 0, 0, 0.4);
                }
            """


class IconToggleCheckboxCard(SimpleCardWidget):
    """优化后的带图标双态复选框卡片"""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)

        # 设置卡片样式（浅色主题）
        self.setObjectName(text)
        self.setStyleSheet("""
            IconToggleCheckboxCard {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
            }
        """)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 主布局
        self.hBoxLayout = QHBoxLayout(self)

        # 创建带图标的复选框
        self.checkbox = IconToggleButton(self)

        # 创建文本标签
        self.label = QLabel(text, self)
        self.label.setStyleSheet("font-size: 14px;")  # 字体大小

        # 将组件添加到布局
        self.hBoxLayout.addWidget(self.checkbox)
        self.hBoxLayout.addWidget(self.label)

    def _onLabelClicked(self, event):
        """点击标签也切换复选框状态"""
        self.checkbox.click()
        event.accept()

    def isChecked(self) -> bool:
        return self.checkbox.isChecked()

    def setChecked(self, checked: bool):
        self.checkbox.setChecked(checked)


if __name__ == '__main__':
    app = QApplication([])

    # 创建演示窗口
    window = QWidget()

    layout = QVBoxLayout(window)
    # 创建示例复选框
    option1 = IconToggleCheckboxCard("同意用户协议")
    option2 = IconToggleCheckboxCard("接收促销邮件")
    option3 = IconToggleCheckboxCard("记住登录状态")
    option3.setChecked(True)  # 默认选中

    layout.addWidget(option1)
    layout.addWidget(option2)
    layout.addWidget(option3)
    layout.addStretch()

    window.show()
    app.exec()
