
import urllib.request
from Api import api
from PIL import Image
from io import BytesIO
from Utils.path_resolver import resource_path

def download_photo(url, username, domin, cookie):
    headers = {
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': '',
        'sec-ch-ua': ' "Chromium";v="134", "Not: A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    }

    # url = url.replace('small', 'big')
    headers["referer"] = domin
    headers["cookie"] = 'cf_clearance=dN.JJ2Wpv42s85MXoE5fEqS_3OGgZ5e1m3.vS.N1m3o-1744283003-1.2.1.1-GIdVZW3h8zUEwr58COMLiwtgThf6u78rOyhmarOtfenTSsuaziKkhl81eqw0TFu7mqKBY.mhFNMIa94XRxocvZ2AktnMPIIeqG0JhDTPxOwugPJ7DwaoBPw2FJl8Y9YR3HifgEIJbe9VsyMqCJIhWT9lkv_3tR0qopkLQUtOR9uqZujoxwztFUMhvy378uuCfnylrFL74.Wo7NmcFrKxlrQ2k7r8gzxry4khgXQ0.fQRPbSmbu_WxHvWqowS2rAQUD7n9TfbNaOVgII4JtEo7gZkMqNZWAWX9iQrUiol5EBk099IH2ImHPwKopjvXg.CMWt8wlzFG5Lu2RE6t1_jYnY.oYY.fuSkRl1tMWxMWf5nR5ltkrYf480YB4_rFLUo'

    try_cnt = 0

    while True:
        try :
            print('start_down: \n')
            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(request)
            print('response: ', response.read().decode('utf-8'))
            content = response.read()
            print('content:', content)
            img = Image.open(BytesIO(content))
            try :
                path = resource_path(f"./Resource/cache/photo")
                img.save(str(path) + '/' + f'{username}.gif', save_all=True, loop=0)
            except Exception as e:
                # print('头像下载失败……')
                pass
            return True
        except Exception as e:
            if try_cnt < 3:
                try_cnt += 1
            else :
                return False

