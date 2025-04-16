# utils/path_resolver.py
import sys
import os
from pathlib import Path


def resource_path(relative_path):
    """ 统一资源路径解决方案 """
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        # 始终基于项目根目录（假设utils/在项目根目录）
        base_path = Path(__file__).parent.parent

    # 统一处理路径格式
    path = (base_path / relative_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"资源路径不存在: {path}")
    return str(path)
