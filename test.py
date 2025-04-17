from PySide6.QtCore import QThread
from time import sleep

class MyThread(QThread):
    def __init__(self, info):
        super().__init__()
        self.info = info

    def run(self):
        print("线程中 info：", self.info)

info = {"sleep": 1}
t1 = MyThread(info)
t1.start()

# 修改 info
info["sleep"] = 2
t2 = MyThread(info)
t2.start()

t1.wait()
t2.wait()
