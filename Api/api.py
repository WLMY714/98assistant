import re
import json
from datetime import datetime

import requests
import urllib.request
import random
import base64
import string

from time import sleep, time
from urllib.parse import urlencode
from lxml import etree

import Model.message as MSG
from Api import xpath


headers = {
    # ':authority': 'sehuatang.net',
    # ':method': 'GET',
    # ':path': '/forum.php?mod=viewthread&tid=2551793',
    # ':scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    # 'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cookie': '',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"132.0.6834.83"',
    'sec-ch-ua-full-version-list': '"Not A(Brand";v="8.0.0.0", "Chromium";v="132.0.6834.83", "Google Chrome";v="132.0.6834.83"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-Model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}


class Url:
    url = 'https://www.sehuatang.net'
    url1 = 'https://www.sehuatang.net'
    url2 = 'https://www.sehuatang.org'
    url_home = 'https://sehuatang.net/home.php?mod=space'


class Cookie:
    pass

class GetContent:

    @staticmethod
    def get_content(url, head=None, cookie=None, content_type=None, referer=None):

        if head is None:
            head = headers
            if content_type is not None:
                head['Content-Type'] = content_type
            if referer is not None:
                head['Referer'] = referer
            if cookie is None:
                request = urllib.request.Request(url=url)
            else:
                head['cookie'] = cookie
                request = urllib.request.Request(url=url, headers=head)
        else:
            request = urllib.request.Request(url=url, headers=head)

        request_cnt = 1
        while True:
            code = 404
            try:
                response = urllib.request.urlopen(request, timeout=10)
                code = response.getcode()
                content = response.read().decode('utf-8')
            except Exception as e:
                if request_cnt <= 3:
                    sleep_time = request_cnt * 5
                    print(f'第 {request_cnt}/3 次请求超时, {sleep_time}s 后自动重新请求')
                    request_cnt += 1
                    sleep(sleep_time)
                else:
                    msg = MSG.Message(message="请求失败")
                    return msg
            else:
                msg = MSG.Message(True, content=content, message="请求完毕")
                return msg

class Rate:

    @staticmethod
    def find_a_post(domin, cookie, username):

        encode_username = {
            'username': username
        }
        url = f'{domin}/home.php?mod=space&{urlencode(encode_username)}&do=thread&view=me&from=space'
        content = GetContent.get_content(url=url, cookie=cookie)

        content_tree = etree.HTML(content.content)
        sectors = content_tree.xpath(xpath.XpathOfTheme.sector)
        posts = content_tree.xpath(xpath.XpathOfTheme.href)

        for i in range(len(sectors)):
            valid_sector = ['综合讨论区', '网友原创区', 'AI专区', '资源出售区', '新作区', '自提字幕区', '自译字幕区', '原创自拍区']
            if sectors[i] in valid_sector:
                return domin+'/'+posts[i]
        return url

    @staticmethod
    def get_rate_info(tid, pid, timestamp, cookie, domin):
        """
        评分失败：alert_error
            1、评分不足   正常 需要手动报错
            2、重复评分   error
            3、权限不足   error
            4、帖子不存在  error
            5、其他
        """

        rate_info_url = f'{domin}/forum.php?mod=misc&action=rate&tid={tid}&pid={pid}&infloat=yes&handlekey=rate&t={timestamp}&inajax=1&ajaxtarget=fwin_content_rate'
        content_mgs = GetContent.get_content(url=rate_info_url, cookie=cookie)

        info = {
            "state": False,
            "score": 0,
            "formHash": "",
            "referer": "",
            "handleKey": "",
            "error": ""
        }

        if content_mgs.code:
            try:
                if 'alert_error' in content_mgs.content:
                    content = re.search(r"errorhandle_rate\('([^']+)'", content_mgs.content).group(1)
                    msg = MSG.Message(content=info, message=content)
                    return msg
                else:
                    info["state"] = True
                    score = re.findall(r'<td>\s*~?\s*(\d+)\s*</td>', content_mgs.content)
                    score = [int(num) for num in score]
                    info["score"] = min(score[0], score[1])
                    if info["score"] < 1:
                        msg = MSG.Message(message="评分不足")
                        return msg

                    referer = re.search(r'name="referer" value="([^"]+)"', content_mgs.content).group(1)
                    info["referer"] = referer
                    formHash = re.search(r'name="formhash" value="([^"]+)"', content_mgs.content).group(1)
                    info["formHash"] = formHash
                    handleKey = re.search(r'name="handlekey" value="([^"]+)"', content_mgs.content).group(1)
                    info["handleKey"] = handleKey

                    msg = MSG.Message(code=True, content=info)
                    return msg

            except Exception as e:
                msg = MSG.Message(message="评分失败")
                return msg
        else:
            msg = MSG.Message(content=info, message="评分失败")
            return msg

    @staticmethod
    def subrate(url, head, data):
        try_count = 1
        while True:
            try:
                response = requests.post(url, headers=head, data=data, timeout=5)
                msg = MSG.Message(code=True, content=response.text, message="评分成功,已通知作者")
                return msg
            except Exception as e:
                # print(e)
                if try_count <= 3:
                    # print(f'第 {try_count}/3 次请求失败, 出现请求错误, 3秒后自动重试')
                    try_count += 1
                    sleep(3)
                else:
                    msg = MSG.Message(content=str(e), message="评分失败")
                    return msg

    @staticmethod
    def rate(tid, pid, cookie, domin=None):

        if domin is None:
            domin = Url.url

        timestamp = int(time() * 1000)
        rate_info = Rate.get_rate_info(tid, pid, timestamp, cookie, domin)
        if not rate_info.code:
            return rate_info

        rate_url = domin + "/forum.php?mod=misc&action=rate&ratesubmit=yes&infloat=yes&inajax=1"
        head = headers
        head["cookie"] = cookie

        data = {
            "formhash": rate_info.content["formHash"],
            "tid": tid,
            "pid": pid,
            "referer": rate_info.content["referer"],
            "handlekey": rate_info.content["handleKey"],
            "score8": rate_info.content["score"],
            "reason": "",
            "sendreasonpm": "on"
        }

        rate_result_msg = Rate.subrate(url=rate_url, head=head, data=data)

        return rate_result_msg


class Sign:

    @staticmethod
    def reply(fid, tid, pid, cookie, domin, message):

        url = f"{domin}/forum.php?mod=post&action=reply&fid={fid}&tid={tid}&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1"

        head = headers
        head["cookie"] = cookie
        timestamp = int(time() * 1000)
        data = {
            "file": "",
            "message": message,
            "posttime": str(timestamp),
            "formHash": "",
            "usesig": "1",
            "subject": ""
        }
        info = Rate.get_rate_info(tid=tid, pid=pid, timestamp=timestamp, cookie=cookie, domin=domin)
        data["formhash"] = info.content["formHash"]
        request = requests.post(url=url, headers=head, data=data)

    @staticmethod
    def try_sign(fid, tid, pid, cookie, domin, message):
        try:
            url = f'{domin}/plugin.php?id=dd_sign&ac=sign&infloat=yes&handlekey=pc_click_ddsign&inajax=1&ajaxtarget=fwin_content_pc_click_ddsign'
            content = GetContent.get_content(url=url, cookie=cookie, referer=f'{domin}/plugin.php?id=dd_sign')

            formhash_match = re.search(r'name="formhash" value="(.*?)"', content.content)
            formhash = formhash_match.group(1) if formhash_match else None
            signtoken_match = re.search(r'name="signtoken" value="(.*?)"', content.content)
            signtoken = signtoken_match.group(1) if signtoken_match else None
            secqaa_match = re.search(r'<span id="(secqaa_[^"]+)"', content.content)
            secqaa = secqaa_match.group(1) if secqaa_match else None
            if secqaa:
                secqaa = secqaa.split('_')[1]
            signhash_match = re.search(r'(signhash=[^"]+)', content.content)
            signhash = signhash_match.group(1) if signhash_match else None
            if signhash:
                signhash = signhash.split('=')[1]

            # 获取答案
            # 提取set-cookie
            url = f'{domin}/misc.php?mod=secqaa&action=update&idhash={secqaa}'
            # content = api.GetContent.get_content(url=url, cookie=cookie, referer=f"{domin}/plugin.php?id=dd_sign")
            head = headers
            head["Referer"] = f"{domin}/plugin.php?id=dd_sign"
            response = requests.get(url, headers=head, timeout=5)
            set_cookie = response.headers.get("Set-Cookie", "")

            # 更新 Cookie
            # 提取 `cPNj_2132_lastact` 和 `cPNj_2132_secqaaq` 相关值
            lastact_match = re.search(r"(cPNj_2132_lastact=[^;]+)", set_cookie)
            secqaa_match = re.search(r"(cPNj_2132_secqaaq[^=]+=[^;]+)", set_cookie)
            # 提取匹配到的值
            lastact_cookie = lastact_match.group(1) if lastact_match else None
            secqaa_cookie = secqaa_match.group(1) if secqaa_match else None
            # 移除旧的 `cPNj_2132_lastact`
            new_cookie_parts = [cookie.strip() for cookie in re.split(r";\s*", cookie) if
                                not cookie.startswith("cPNj_2132_lastact")]
            # 追加 `secqaa`（如果存在）
            if secqaa_cookie:
                new_cookie_parts.append(secqaa_cookie)
            # 最后追加 `lastact`
            if lastact_cookie:
                new_cookie_parts.append(lastact_cookie)
            # 重新拼接 `cookie`
            new_cookie = "; ".join(new_cookie_parts)

            # 提取问题并计算
            match = re.search(r'(\d+\s*[\+\-\*/]\s*\d+)\s*=', str(response.content))
            answer = 0
            if match:
                math_expr = match.group(1)  # 获取表达式 "59 + 6"
                answer = eval(math_expr)

            # url = f'{domin}/misc.php?mod=secqaa&action=check&inajax=1&modid=&idhash={secqaa}&secverify={answer}'
            # content = GetContent.get_content(url=url, cookie=new_cookie, referer=f'{domin}/plugin.php?id=dd_sign')

            url = f'{domin}/plugin.php?id=dd_sign&ac=sign&signsubmit=yes&handlekey=pc_click_ddsign&signhash={signhash}&inajax=1'
            data = {
                "formhash": formhash,
                "signtoken": signtoken,
                "secqaahash": secqaa,
                "secanswer": str(answer),
            }

            head["Referer"] = f'{domin}/plugin.php?id=dd_sign'
            head["cookie"] = new_cookie

            request = requests.post(url=url, headers=head, data=data, timeout=5)

            # print("response.content: ", response.content)
            # print("formhash: ", formhash)
            # print("signtoken: ", signtoken)
            # print("secqaahash: ", secqaa)
            # print("secanswer: ", str(answer))
            # print("new_cookie: ", new_cookie)
            # print(request.text)

            if '请至少发表或回复一个帖子后再来签到' in request.text:
                Sign.reply(fid, tid, pid, cookie, domin, message)
                request = requests.post(url=url, headers=head, data=data, timeout=5)

            if '系统繁忙' in request.text or '验证问答填写错误' in request.text:
                msg = MSG.Message(content='系统繁忙，请稍等重试…', message='系统繁忙，请稍等重试…')
                return msg
            if '请勿重复签到' in request.text:
                msg = MSG.Message(content='今日已签到', message='今日已签到')
                return msg
            if '请至少发表或回复一个帖子后再来签到' in request.text:
                msg = MSG.Message(content='请至少发表或回复一个帖子后再来签到', message='请至少发表或回复一个帖子后再来签到')
                return msg
            if '签到成功' in request.text:
                msg = MSG.Message(code=True, content='签到成功', message='签到成功')
                return msg
            msg = MSG.Message(content='系统繁忙，请稍等重试…', message='系统繁忙，请稍等重试…')
            return msg
        except Exception as e:
            msg = MSG.Message(content='系统繁忙，请稍等重试…', message='系统繁忙，请稍等重试…')
            return msg

    @staticmethod
    def sign(fid, tid, pid, cookie, domin, message):

        # print('###########  开始签到  ############')

        try_sign_number = 3

        while try_sign_number >= 0:
            msg = Sign.try_sign(fid, tid, pid, cookie, domin, message)
            if '系统繁忙' in msg.content:
                sleep(60)
                if try_sign_number >= 0:
                    try_sign_number -= 1
                    continue
                return msg
            if msg.content == '今日已签到':
                return msg
            if msg.content == '签到成功':
                return msg
            if msg.content == '请至少发表或回复一个帖子后再来签到':
                Sign.reply(fid, tid, pid, cookie, domin, message)
                msg = Sign.try_sign(domin=domin, cookie=cookie)
                if msg.content == '今日已签到':
                    return msg
        # elif 出错 return 签到失败，请重试……
        msg = MSG.Message(content='网络错误，请重试…', message='网络错误，请重试…')
        return msg

class Darkroom:

    @staticmethod
    def save_all_users_in_txt(all_users, folder):
        print('save: ', all_users)
        filetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        file = open(f'{folder}/小黑屋_{filetime}.txt', 'w', encoding='utf-8')
        usercnt = 1

        for user in all_users:
            file.write(f'【{usercnt}/{len(all_users)}】 : {user[1]}(uid={user[2]})\n')
            file.write(f'操作者:  {user[3]}\n')
            file.write(f'操作原因: {user[4]}\n')
            file.write(f'操作时间: {user[5]}\n')
            file.write('\n' + '*' * 50 + '\n\n')
            usercnt += 1
        file.close()

    @staticmethod
    def get_all_users(domin, head):
        numbers = 100
        all_users = []

        cid = 99999999
        pos = 0
        while cid > 1:
            # while cnt < 10:
            try:
                url = f'{domin}/forum.php?mod=misc&action=showdarkroom&cid={cid}&t=5389259&ajaxdata=json'
                request = urllib.request.Request(url=url, headers=head)
                response = urllib.request.urlopen(request)
                content = response.read().decode('utf-8')

                # 解析 JSON
                fixed_content = re.sub(r'(\{|,)(\d+):', r'\1"\2":', content)
                pattern = r'"dateline":\s*"<span title=\\"([^"]+)\\"[^>]*>.*?</span>"'
                fixed_content = re.sub(pattern, r'"dateline": "\1"', fixed_content)

                data = json.loads(fixed_content, object_pairs_hook=dict)

                if len(data['data']) == 0:
                    cid -= 1
                    continue

                for user in data["data"]:
                    all_users.append([
                        data["data"][user]["cid"],
                        data["data"][user]["username"],
                        data["data"][user]["uid"],
                        data["data"][user]["operator"],
                        data["data"][user]["reason"],
                        data["data"][user]["dateline"]
                    ])
                    if len(all_users) == numbers:
                        return all_users
                cid = int(data["data"][user]["cid"])
                pos = 0

            except Exception as e:
                if pos < 3:
                    pos += 1
                    sleep(2)
                else:
                    break

    @staticmethod
    def start_get_darkroom(domin, cookie, folder):
        head = headers
        head['cookie'] = cookie
        all_users = Darkroom.get_all_users(domin=domin, head=head)

        all_users = sorted(all_users, key=lambda x: x[5], reverse=True)
        Darkroom.save_all_users_in_txt(all_users, folder)

