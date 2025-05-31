import os

folder_path = r"C:\Users\wlmy\Desktop\98助手客户端UI 1.3\_internal"  # 例如 'C:/Users/YourName/Desktop'

# 打印该目录下的所有文件和文件夹
for item in os.listdir(folder_path):
    print(item)
