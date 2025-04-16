
import urllib.request, urllib.error
from time import sleep
import random

headers_fanza = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cookie': 'top_dummy=01d724ab-1444-4905-b85a-98d70960c7a8; uid=QJlFpjyCCqZUZglfQLBG; suid=QJlFpjyCCqZUZglfQLBG; rieSh3Ee_ga=GA1.1.2090002890.1720154938; _yjsu_yjad=1720154937.a210dbea-61b6-4a1c-874f-488558faa658; adpf_uid=YqMNohFLBavMDshs; i3_ab=2fa0c07d-9389-400a-9499-7a831e460946; _gcl_au=1.1.1549709294.1736264676; FPID=FPID2.3.iV6XAq%2BfU2%2BguV3hIohePvqEGHXDQf%2FWRB%2BBu4R7K%2FI%3D.1720154938; FPAU=1.3.1675289702.1736264678; _tt_enable_cookie=1; _ttp=fX_CEPsOAkMk_mVnuBeyquCFZ_V.tt.2; guest_id=BBJaWA5AVUdQDAFb; digital[play_volume]=0.65; cklg=ja; check_done_login=true; cdp_id=1JT5HWgzRGs88jhB; rieSh3Ee_ga_KQYE0DE5JW=deleted; rieSh3Ee_ga_KQYE0DE5JW=deleted; _fbp=fb.2.1737797832720.826011200583805379; alcb=true; pt_21j2m5ao=deviceId%3D6cc013fd-e36f-4e29-97cc-5642b7ddb261%26sessionId%3Dbb422d65-2172-4313-a931-86ca779a8a6f%26accountId%3D1JT5HWgzRGs88jhB%26vn%3D5%26pvn%3D1%26lastActionTime%3D1739970313535%26; digital[play_muted]=1; subscription_members_status=non; secid=37857f75fde8d5519e542590735e2f08; login_secure_id=37857f75fde8d5519e542590735e2f08; age_check_done=1; d_mylibrary=nINks%2BxgI%2F1I329WV6UBoA%3D%3D; ixd_lastclick=6828,1743434808; dig_history=mdon00074%2C1start00305%2Cvrkm01533%2Ccawd00818%2Cwaaa00516%2Cwaaa00518%2Cmmpb00076%2Cwaaa00497%2Csame00162%2Cmida00106%2Cmida00150%2Catad00189%2Cadn00669%2Clulu00375%2Cadn00668%2Ch_1711fch00101%2Cipvr00300%2Cipzz00170%2Csame00157%2Creal00905%2Cpfes00107%2Cvenz00052%2Csone00707%2Csykh00142%2Cjur00285%2Csone00687%2Coae00275%2Cmkmp00631%2Cbibivr00150%2Cktra00706%2Ch_1472erhav00037%2Cmida00039%2Cipbz00013%2C1start00273v%2Cmaqq00002%2Cdmdg00060%2Caukg00625%2Cmyba00081%2Ckdmi00064%2Chmn00691; top_pv_uid=b89e9ad5-c4d9-48fa-bbc1-d3d6a8bde6a3; _clck=12plec7%7C2%7Cfuu%7C0%7C1840; ckcy=1; FPLC=asH4rZxGpWBtetqynC60lmNlTjYJeT2Qgq0sZIrHberGORTqGcTsnamZZaruQLaPatfKsTWFJEhA%2BIs6vJQ4Nsbhmn8StWj8ss%2BQyGj18ch41Z4m5UT09Z9iqAhycw%3D%3D; ckcy=1; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22SQPyyuPOHZp9gB1tsvff%22%2C%22expiryDate%22%3A%222026-04-07T08%3A22%3A29.800Z%22%7D; is_intarnal=true; rieSh3Ee_ga_KQYE0DE5JW=GS1.1.1744014149.51.1.1744015342.0.0.888610233; _dd_s=rum=0&expire=1744018314673&logs=1&id=19934c24-aee8-4fcf-acb2-4937d390c20b&created=1744017414673',
    'if-none-match': '"otf01xm95n6ah5"',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}


headers_fanza_post = {
    'accept': 'application/graphql-response+json, application/graphql+json, application/json, text/event-stream, multipart/mixed',
    'accept-language': 'en-US',
    'content-length': '5940',
    'content-type': 'application/json',
    'cookie': 'top_dummy=01d724ab-1444-4905-b85a-98d70960c7a8; uid=QJlFpjyCCqZUZglfQLBG; suid=QJlFpjyCCqZUZglfQLBG; rieSh3Ee_ga=GA1.1.2090002890.1720154938; _yjsu_yjad=1720154937.a210dbea-61b6-4a1c-874f-488558faa658; adpf_uid=YqMNohFLBavMDshs; i3_ab=2fa0c07d-9389-400a-9499-7a831e460946; _gcl_au=1.1.1549709294.1736264676; FPID=FPID2.3.iV6XAq%2BfU2%2BguV3hIohePvqEGHXDQf%2FWRB%2BBu4R7K%2FI%3D.1720154938; FPAU=1.3.1675289702.1736264678; _tt_enable_cookie=1; _ttp=fX_CEPsOAkMk_mVnuBeyquCFZ_V.tt.2; guest_id=BBJaWA5AVUdQDAFb; digital[play_volume]=0.65; cklg=ja; check_done_login=true; cdp_id=1JT5HWgzRGs88jhB; rieSh3Ee_ga_KQYE0DE5JW=deleted; _fbp=fb.2.1737797832720.826011200583805379; alcb=true; pt_21j2m5ao=deviceId%3D6cc013fd-e36f-4e29-97cc-5642b7ddb261%26sessionId%3Dbb422d65-2172-4313-a931-86ca779a8a6f%26accountId%3D1JT5HWgzRGs88jhB%26vn%3D5%26pvn%3D1%26lastActionTime%3D1739970313535%26; digital[play_muted]=1; subscription_members_status=non; secid=37857f75fde8d5519e542590735e2f08; login_secure_id=37857f75fde8d5519e542590735e2f08; age_check_done=1; d_mylibrary=nINks%2BxgI%2F1I329WV6UBoA%3D%3D; ixd_lastclick=6828,1743434808; top_pv_uid=b89e9ad5-c4d9-48fa-bbc1-d3d6a8bde6a3; _clck=12plec7%7C2%7Cfuu%7C0%7C1840; FPLC=asH4rZxGpWBtetqynC60lmNlTjYJeT2Qgq0sZIrHberGORTqGcTsnamZZaruQLaPatfKsTWFJEhA%2BIs6vJQ4Nsbhmn8StWj8ss%2BQyGj18ch41Z4m5UT09Z9iqAhycw%3D%3D; is_intarnal=true; dig_history=adn00669%2Cmdon00074%2C1start00305%2Cvrkm01533%2Ccawd00818%2Cwaaa00516%2Cwaaa00518%2Cmmpb00076%2Cwaaa00497%2Csame00162%2Cmida00106%2Cmida00150%2Catad00189%2Clulu00375%2Cadn00668%2Ch_1711fch00101%2Cipvr00300%2Cipzz00170%2Csame00157%2Creal00905%2Cpfes00107%2Cvenz00052%2Csone00707%2Csykh00142%2Cjur00285%2Csone00687%2Coae00275%2Cmkmp00631%2Cbibivr00150%2Cktra00706%2Ch_1472erhav00037%2Cmida00039%2Cipbz00013%2C1start00273v%2Cmaqq00002%2Cdmdg00060%2Caukg00625%2Cmyba00081%2Ckdmi00064%2Chmn00691; mbox=check#true#1744017616|session#1744017555805-772541#1744019416; ckcy=1; rieSh3Ee_ga_KQYE0DE5JW=GS1.1.1744017416.52.1.1744017773.0.0.1781575959',
    'fanza-device': 'BROWSER',
    'origin': 'https://video.dmm.co.jp',
    'priority': 'u=1, i',
    'referer': 'https://video.dmm.co.jp/',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
}


headers_vedio = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': 'top_dummy=01d724ab-1444-4905-b85a-98d70960c7a8; uid=QJlFpjyCCqZUZglfQLBG; suid=QJlFpjyCCqZUZglfQLBG; rieSh3Ee_ga=GA1.1.2090002890.1720154938; _yjsu_yjad=1720154937.a210dbea-61b6-4a1c-874f-488558faa658; adpf_uid=YqMNohFLBavMDshs; i3_ab=2fa0c07d-9389-400a-9499-7a831e460946; _gcl_au=1.1.1549709294.1736264676; FPID=FPID2.3.iV6XAq%2BfU2%2BguV3hIohePvqEGHXDQf%2FWRB%2BBu4R7K%2FI%3D.1720154938; FPAU=1.3.1675289702.1736264678; _tt_enable_cookie=1; _ttp=fX_CEPsOAkMk_mVnuBeyquCFZ_V.tt.2; guest_id=BBJaWA5AVUdQDAFb; digital[play_volume]=0.65; cklg=ja; check_done_login=true; cdp_id=1JT5HWgzRGs88jhB; _fbp=fb.2.1737797832720.826011200583805379; alcb=true; pt_21j2m5ao=deviceId%3D6cc013fd-e36f-4e29-97cc-5642b7ddb261%26sessionId%3Dbb422d65-2172-4313-a931-86ca779a8a6f%26accountId%3D1JT5HWgzRGs88jhB%26vn%3D5%26pvn%3D1%26lastActionTime%3D1739970313535%26; digital[play_muted]=1; subscription_members_status=non; secid=37857f75fde8d5519e542590735e2f08; login_secure_id=37857f75fde8d5519e542590735e2f08; age_check_done=1; d_mylibrary=nINks%2BxgI%2F1I329WV6UBoA%3D%3D; ixd_lastclick=6828,1743434808; top_pv_uid=b89e9ad5-c4d9-48fa-bbc1-d3d6a8bde6a3; _clck=12plec7%7C2%7Cfuu%7C0%7C1840; FPLC=asH4rZxGpWBtetqynC60lmNlTjYJeT2Qgq0sZIrHberGORTqGcTsnamZZaruQLaPatfKsTWFJEhA%2BIs6vJQ4Nsbhmn8StWj8ss%2BQyGj18ch41Z4m5UT09Z9iqAhycw%3D%3D; is_intarnal=true; dig_history=adn00669%2Cmdon00074%2C1start00305%2Cvrkm01533%2Ccawd00818%2Cwaaa00516%2Cwaaa00518%2Cmmpb00076%2Cwaaa00497%2Csame00162%2Cmida00106%2Cmida00150%2Catad00189%2Clulu00375%2Cadn00668%2Ch_1711fch00101%2Cipvr00300%2Cipzz00170%2Csame00157%2Creal00905%2Cpfes00107%2Cvenz00052%2Csone00707%2Csykh00142%2Cjur00285%2Csone00687%2Coae00275%2Cmkmp00631%2Cbibivr00150%2Cktra00706%2Ch_1472erhav00037%2Cmida00039%2Cipbz00013%2C1start00273v%2Cmaqq00002%2Cdmdg00060%2Caukg00625%2Cmyba00081%2Ckdmi00064%2Chmn00691; mbox=check#true#1744017616|session#1744017555805-772541#1744019416; rieSh3Ee_ga_KQYE0DE5JW=GS1.1.1744017416.52.1.1744017558.0.0.1781575959; ckcy=1',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}

def create_request(url, web):
    if web == 'fanza':
        request = urllib.request.Request(url=url, headers=headers_fanza)
    else :
        request = urllib.request.Request(url=url, headers=headers_vedio)
    return request

def test_get_response(request):
    cnt = 1
    while cnt < 3:
        try :
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                return True
        except Exception as e:
            try :
                if e.code == 404:
                    return False
                else :
                    cnt += 1
                    sleep(5)
            except Exception as e:
                cnt += 1
                sleep(1)
    return False

def get_url_fanza(sig, number, cnt="fanza1"):
    sig = sig.lower()
    url_fanza = ""
    if cnt == "fanza1":
        url_fanza = f'https://www.dmm.co.jp/litevideo/-/detail/=/cid={sig}{number:03}/'
    elif cnt == "fanza2":
        url_fanza = f'https://www.dmm.co.jp/litevideo/-/detail/=/cid={sig}{number:05}/'
    return url_fanza

def get_url_vedio(sig, number, cnt="vedio1"):
    sig = sig.lower()
    if len(sig) < 3:
        sig0 = sig + '0'
    else :
        sig0 = sig
    vedio_url = ""
    if cnt == "vedio1":
        vedio_url = f'https://cc3001.dmm.co.jp/litevideo/freepv/{sig0[0]}/{sig0[0:3]}/{sig}00{number:03}/{sig}00{number:03}hhb.mp4'
    elif cnt == "vedio2":
        vedio_url = f'https://cc3001.dmm.co.jp/litevideo/freepv/{sig0[0]}/{sig0[0:3]}/{sig}00{number:03}/{sig}00{number:03}_dmb_w.mp4'
    elif cnt == "vedio3":
        vedio_url = f'https://cc3001.dmm.co.jp/litevideo/freepv/{sig0[0]}/{sig0[0:3]}/{sig}{number:03}/{sig}{number:03}hhb.mp4'

    return vedio_url

def test_exist(sig, number, web):  # same00148

    if web == "fanza1" or web == "fanza2":
        search_url = get_url_fanza(sig, number, web)
        search_request = create_request(search_url, web)
    else :
        vedio_url = get_url_vedio(sig, number, web)
        search_request = create_request(vedio_url, web)
    is_exist = test_get_response(search_request)

    sleep(random.uniform(0.1, 0.2))
    return is_exist

if __name__ == "__main__":

    sig = "ADN"
    number = 3
    # print(test_exist(sig, number, 'fanza'))
    # print(test_exist(sig, number, 'vedio3'))
