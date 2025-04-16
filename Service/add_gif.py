
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

def updateFrame(label, photo):
    # 获取当前帧
    current_frame: QPixmap = photo.currentPixmap()
    if current_frame.isNull():
        return

    # 使用高质量平滑缩放，将当前帧按比例缩放到 QLabel 的尺寸
    scaled_frame = current_frame.scaled(
        label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
    )
    label.setPixmap(scaled_frame)
