import os
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import time

class MultiThreadedDownloader:
    def __init__(self, isyut=False, max_workers=5, timeout=30):
        self.max_workers = max_workers
        self.timeout = timeout
        self.lock = threading.Lock()
        self.isyut = isyut
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def get_filename_from_url(self, url):
        filename = url.split("/")[-1]
        filename = filename.replace("pl", "").replace("hhb", "")  # 去除 "pl" 或 "hhb"
        filename = 'www.98t.la@' + filename if self.isyut else filename
        return filename

    def file_needs_download(self, filepath, expected_size):
        if not os.path.exists(filepath):
            return True
        actual_size = os.path.getsize(filepath)
        return expected_size > actual_size

    def download_task(self, url, save_dir):
        filename = self.get_filename_from_url(url)
        filepath = os.path.join(save_dir, filename)

        os.makedirs(save_dir, exist_ok=True)  # 确保路径存在

        for attempt in range(4):
            try:
                with requests.get(url, stream=True, timeout=self.timeout) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('Content-Length', 0))

                    if not self.file_needs_download(filepath, total_size):
                        return f"{filename} 已存在于 {save_dir}，跳过下载"

                    # with self.lock:
                    #     print(f"正在下载：{filename} 到 {save_dir}（尝试 {attempt+1}/3）", flush=True)

                    with open(filepath, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    return f"{filename} 下载完成!"

            except Exception as e:
                # with self.lock:
                #     print(f"下载失败：{filename}，原因：{e}（尝试 {attempt+1}/3）", flush=True)
                time.sleep(1)

        return f"{filename} 下载失败"

    def download_file(self, url, save_dir):
        # 每个任务都可以有自己的保存路径
        future = self.executor.submit(self.download_task, url, save_dir)
        return future

    def shutdown(self):
        self.executor.shutdown(wait=True)
