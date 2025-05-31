import json
import os
import re
import requests
import calendar

from datetime import datetime, timedelta, timezone
from time import sleep
from concurrent.futures import ThreadPoolExecutor

from Api import toolsOfFanza
from Model.message import Message as MSG
from Utils.path_resolver import resource_path


def get_beijing_time():
    # 获取当前北京时间（UTC+8）
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz)

    # 计算当天零点的时间戳
    beijing_time = datetime(now.year, now.month, now.day, tzinfo=beijing_tz)

    # 获取星期几（0=周一, 1=周二, ..., 6=周日）
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday_str = weekdays[beijing_time.weekday()]

    # 计算本周的星期二
    this_monday = beijing_time - timedelta(days=beijing_time.weekday())  # 获取本周一
    this_tuesday = this_monday + timedelta(days=1)  # 获取本周二

    # 计算本周的第几个星期二
    def tuesday_week_count(date):
        first_day = date.replace(day=1)  # 本月1号
        tuesday_count = 0
        week_number = 1
        current_day = first_day

        while current_day <= date:
            if current_day.weekday() == 1:  # 1代表星期二
                tuesday_count += 1  # 统计第几个星期二
                if current_day <= date:  # 确保今天已经过了这个星期二
                    week_number = tuesday_count  # 记录当前星期二的编号
            current_day += timedelta(days=1)  # 逐天增加

        return week_number

    tuesday_week_number = tuesday_week_count(this_tuesday)

    # 计算本周星期二之后的第4个星期五
    days_to_first_friday = (4 - this_tuesday.weekday() + 7) % 7  # 4代表周五
    first_friday = this_tuesday + timedelta(days=days_to_first_friday)
    fourth_friday = first_friday + timedelta(weeks=3)  # 第4个星期五（距离3个星期五）

    message = f"今天是北京时间 {beijing_time.year:04d}-{beijing_time.month:02d}-{beijing_time.day:02d} {weekday_str}, " \
              f"本周的 星期二 为本月第 {tuesday_week_number} 个\n程序将获取 FANZA 发布的配信日为 {fourth_friday.year:04d}-{fourth_friday.month:02d}-{fourth_friday.day:02d} 的新作预告 (此功能随日期自动更新且无法更改)"
    get_day = f"{fourth_friday.year:04d}-{fourth_friday.month:02d}-{fourth_friday.day:02d}"
    # 返回格式化的日期
    return message, get_day, tuesday_week_number, beijing_time, fourth_friday

def get_ban_words():
    file_name = resource_path("./Resource/text/屏蔽关键词.txt")
    keywords_list = []
    # 检查文件是否存在
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            keywords_list = [line.strip() for line in file if line.strip()]  # 去除空行和首尾空格
    return keywords_list

def make_folder(filename):
    # 拼接完整路径
    path = resource_path('./Resource/cache/file')
    folder_path = os.path.join(path, filename)

    # 检查是否存在
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def get_fanzaDetail_by_id(movie_id):
    url = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=" + movie_id + "/"
    return url

def movie_available(movie, ban_words, makers):
    test_title = movie["title"]
    test_id = movie["id"]
    test_maker = movie["maker"]
    for word in ban_words:
        if word in test_title or word in test_id:
            return False
    # if test_maker not in makers:
    #     return False
    return True

def maker_name_replace(maker):
    maker_names = {
        'ムーディーズ': 'Moodyz',
        'エスワン ナンバーワンスタイル': 'S1',
        'アイデアポケット': 'IdeaPocket',
        'マドンナ': 'Madonna',
        'プレミアム': 'PREMIUM',
        '溜池ゴロー': '溜池',
        'kawaii': 'Kawaii',
        'アタッカーズ': 'Attackers',
        'BeFree': 'BeFree',
        'NPJ': 'NPJ',
        'ワンズファクトリー': 'WANZ',
        'ビビアン': 'BBAN',
        'ダスッ！': 'DAS',
        'OPPAI': 'OPPAI',
        '本中': '本中',
        'Hunter': 'HHH-Group',
        'Hsoda': 'HHH-Group',
        'ロイヤル': 'HHH-Group',
        'ROOKIE': 'Rookie',
        'E-BODY': 'E-BODY',
        'Fitch': 'Fitch',
        'エムズビデオグループ': 'MVG',
        '無垢': '無垢',
        '痴女ヘブン': '痴女天堂',
        'えむっ娘ラボ': 'えむっ娘',
        'マックスエー': 'MAX-A',
        'ルナティックス': 'LUNATICS',
        'タカラ映像': 'タカラ映像',
    }
    return maker_names.get(maker, maker)

def get_post(url, headers, data):
    try_count = 1
    while True:
        try:
            response = requests.post(url, headers=headers, json=data, timeout=5)
            return response
        except Exception as e:
            # print(e)
            if try_count <= 3:
                # print(f'第 {try_count}/3 次请求失败, 出现请求错误, 3秒后自动重试')
                try_count += 1
                sleep(3)
            else:
                # print('请求失败, 请确保网络通畅并且已开启日本节点后重试')
                pass

def get_movie_list(cookie, get_day, ban_words, makers):
    url = 'https://api.video.dmm.co.jp/graphql'
    headers = toolsOfFanza.headers_fanza_post
    headers["cookie"] = cookie
    movie_list = []

    data = {
        "operationName": "AvSearch",
        "query": "query AvSearch($limit: Int!, $offset: Int, $floor: PPVFloor, $sort: ContentSearchPPVSort!, $query: SearchQueryInput, $filter: ContentSearchPPVFilterInput, $facetLimit: Int!, $hasFacet: Boolean!, $hasGenreDescription: Boolean!, $legacyProductType: LegacyProductType = DOWNLOAD, $hasLegacyProductType: Boolean!, $isLoggedIn: Boolean!, $excludeUndelivered: Boolean!, $shouldFetchGenreRelatedWords: Boolean!, $shouldFetchDirectorRelatedWords: Boolean!, $shouldFetchLabelRelatedWords: Boolean!, $shouldFetchSeriesRelatedWords: Boolean!, $shouldFetchActressRelatedWords: Boolean!, $shouldFetchMakerRelatedWords: Boolean!, $shouldFetchHistrionRelatedWords: Boolean!) {\n  legacySearchPPV(\n    limit: $limit\n    offset: $offset\n    floor: $floor\n    sort: $sort\n    query: $query\n    filter: $filter\n    facetLimit: $facetLimit\n    includeExplicit: true\n    excludeUndelivered: $excludeUndelivered\n  ) {\n    result {\n      contents {\n        ...searchContent\n        contentType\n        actresses {\n          id\n          name\n          __typename\n        }\n        maker {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      facet @include(if: $hasFacet) {\n        ...contentSearchFacet\n        __typename\n      }\n      pageInfo {\n        ...paginationFragment\n        __typename\n      }\n      isNoIndex\n      searchCriteria {\n        ...contentSearchCriteria\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\nfragment searchContent on PPVContentSearchContent {\n  id\n  title\n  packageImage {\n    mediumUrl\n    largeUrl\n    __typename\n  }\n  sampleImages {\n    number\n    largeUrl\n    __typename\n  }\n  sampleMovie {\n    hlsUrl\n    mp4Url\n    vrUrl\n    __typename\n  }\n  releaseStatus\n  review {\n    average\n    count\n    __typename\n  }\n  isExclusiveDelivery\n  bookmarkCount\n  salesInfo {\n    lowestPrice {\n      productId\n      price\n      discountPrice\n      legacyProductType\n      __typename\n    }\n    priceByLegacyProductType(legacyProductType: $legacyProductType) @include(if: $hasLegacyProductType) {\n      discountPrice\n      price\n      legacyProductType\n      __typename\n    }\n    campaign {\n      name\n      endAt\n      __typename\n    }\n    hasMultiplePrices\n    __typename\n  }\n  isOnSale\n  deliveryStartAt\n  utilization @include(if: $isLoggedIn) {\n    status\n    isTVODRentalPlayable\n    __typename\n  }\n  __typename\n}\nfragment contentSearchFacet on PPVContentSearchFacet {\n  floor {\n    items {\n      floor\n      count\n      __typename\n    }\n    __typename\n  }\n  actress {\n    items {\n      id\n      name\n      count\n      __typename\n    }\n    __typename\n  }\n  maker {\n    items {\n      id\n      name\n      count\n      __typename\n    }\n    __typename\n  }\n  label {\n    items {\n      id\n      name\n      count\n      __typename\n    }\n    __typename\n  }\n  series {\n    items {\n      id\n      name\n      count\n      __typename\n    }\n    __typename\n  }\n  genreAndCampaignCombined {\n    items {\n      ... on GenreFacetItem {\n        count\n        id\n        name\n        __typename\n      }\n      ... on CampaignFacetItem {\n        count\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\nfragment paginationFragment on OffsetPageInfoWithTotal {\n  offset\n  limit\n  hasNext\n  totalCount\n  __typename\n}\nfragment contentSearchCriteria on PPVContentSearchCriteria {\n  sort\n  filter {\n    actressIds {\n      ids {\n        id\n        name\n        nameRuby\n        relatedWords @include(if: $shouldFetchActressRelatedWords)\n        __typename\n      }\n      op\n      __typename\n    }\n    authorIds {\n      ids {\n        id\n        name\n        nameRuby\n        __typename\n      }\n      op\n      __typename\n    }\n    directorIds {\n      ids {\n        id\n        name\n        nameRuby\n        relatedWords @include(if: $shouldFetchDirectorRelatedWords)\n        __typename\n      }\n      op\n      __typename\n    }\n    genreIds {\n      ids {\n        id\n        name\n        relatedWords @include(if: $shouldFetchGenreRelatedWords)\n        description @include(if: $hasGenreDescription)\n        __typename\n      }\n      op\n      __typename\n    }\n    histrionIds {\n      ids {\n        id\n        name\n        nameRuby\n        relatedWords @include(if: $shouldFetchHistrionRelatedWords)\n        __typename\n      }\n      op\n      __typename\n    }\n    labelIds {\n      ids {\n        id\n        name\n        relatedWords @include(if: $shouldFetchLabelRelatedWords)\n        __typename\n      }\n      op\n      __typename\n    }\n    makerIds {\n      ids {\n        id\n        name\n        relatedWords @include(if: $shouldFetchMakerRelatedWords)\n        __typename\n      }\n      op\n      __typename\n    }\n    seriesIds {\n      ids {\n        id\n        name\n        relatedWords @include(if: $shouldFetchSeriesRelatedWords)\n        __typename\n      }\n      op\n      __typename\n    }\n    campaignIds {\n      ids {\n        id\n        name\n        __typename\n      }\n      op\n      __typename\n    }\n    __typename\n  }\n  __typename\n}",
        "variables": {
            "excludeUndelivered": False,
            "facetLimit": 100,
            "filter": {"legacyReleaseStatus": "PRE_ORDER"},
            "floor": "AV",
            "hasFacet": True,
            "hasGenreDescription": False,
            "hasLegacyProductType": False,
            "isLoggedIn": False,
            "limit": 120,
            "offset": 0,
            "shouldFetchActressRelatedWords": False,
            "shouldFetchDirectorRelatedWords": False,
            "shouldFetchGenreRelatedWords": False,
            "shouldFetchHistrionRelatedWords": False,
            "shouldFetchLabelRelatedWords": False,
            "shouldFetchMakerRelatedWords": False,
            "shouldFetchSeriesRelatedWords": False,
            "sort": "DELIVERY_START_DATE"
        }
    }

    for i in range(0, 100):
        flag = 1
        data["variables"]["offset"] = i * 120
        # print(f'获取FANZA第 {i + 1} 页数据 (预计3~5页)')

        response = get_post(url, headers, data)
        json_data = response.json()
        contents = json_data["data"]["legacySearchPPV"]["result"]["contents"]
        for content in contents:

            movie = {}
            movie['date'] = content["deliveryStartAt"][:10]
            movie['maker'] = maker_name_replace(content["maker"]["name"])
            movie['id'] = content["id"]
            movie_actress_list = []
            for actresses in content["actresses"]:
                movie_actress_list.append(actresses["name"])
            movie['name'] = "、".join(movie_actress_list)
            if movie['name'] == '':
                movie['name'] = '匿名'
            movie['title'] = content["title"]
            movie['face'] = content["packageImage"]["largeUrl"]
            movie['vedio'] = content["sampleMovie"]["mp4Url"]
            if movie['vedio'] is None:
                try :
                    vedio_id = transform_string(movie['id']).split('-')
                    movie['vedio'] = toolsOfFanza.get_url_vedio(vedio_id[0], vedio_id[1])
                except Exception as e:
                    movie['vedio'] = None
            movie['fanza'] = get_fanzaDetail_by_id(movie['id'])

            if datetime.strptime(movie['date'], "%Y-%m-%d") == datetime.strptime(get_day, "%Y-%m-%d"):
                if movie_available(movie, ban_words, makers):
                    movie_list.append(movie)
            elif datetime.strptime(movie['date'], "%Y-%m-%d") < datetime.strptime(get_day, "%Y-%m-%d"):
                flag = 0
                break
        if flag == 0:
            break
        sleep(1)
    return movie_list

def get_exculsive_maker(maker_this_week, code):
    if code == 'lbsl98t' or code == 'lbsl98t-l':
        makers_of_lbsl = ["BeFree", "Fitch", "MADOOOON", "NPJ", "WANZ", "BBAN", "DAS", "HHH-Group", "Rookie", "E-BODY",
                          "MVG", "OPPAI", "無垢", "えむっ娘", "痴女天堂", "MAX-A", "LUNATICS", "タカラ映像"]
        if str(get_beijing_time()[2]) == '3':
            makers_of_lbsl.append('本中')

        new_makers = [maker for maker in maker_this_week if maker in makers_of_lbsl]
        return new_makers
    elif code == 'r3698t':
        makers_of_r3600 = ["Moodyz", "Kawaii", "Attackers", "S1", "IdeaPocket", "Madonna", "PREMIUM", "溜池"]
        if str(get_beijing_time()[2]) == '4':
            makers_of_r3600.append('本中')
        new_makers = [maker for maker in maker_this_week if maker in makers_of_r3600]
        return new_makers
    else:
        return maker_this_week

def save_file_with_type(save_type, filename, makers, movie_list):
    textname = 'filename'
    if save_type == 'face':
        textname = '高清封面链接.txt'
    elif save_type == 'vedio':
        textname = '预告视频链接.txt'
    elif save_type == 'fanza':
        textname = 'FANZA详情页.txt'
    path = resource_path('./Resource/cache/file/' + filename)
    file = open(path + '/' + textname, 'w', encoding='utf-8')

    for maker_name in makers:
        maker_cnt = sum(1 for movie in movie_list if movie['maker'] == maker_name)
        if maker_cnt < 1 :
            continue
        file.write(f'{maker_name} : {maker_cnt} 部\n')
        for movie in movie_list:
            if movie['maker'] == maker_name:
                try:
                    file.write(movie[save_type] + '\n')
                except Exception as e:
                    pass
        file.write('*' * 95 + '\n\n')
    file.close()

def transform_string(input_str):
    # 使用正则表达式将英文和数字部分提取出来
    match = re.match(r"([a-zA-Z]+)(\d+)", input_str)

    if match:
        # 提取英文部分并转换为大写
        letters = match.group(1).upper()
        # 提取数字部分，确保它是至少3位
        number = match.group(2).zfill(3)
        # 拼接成格式 "SAME-151"
        return f"{letters}-{int(number):03}"
    else:
        return input_str
        # raise ValueError("输入字符串格式不正确")

def find_nth_weekday_of_month(n, weekday):
    # 获取当前月份的第一天和最后一天
    now = datetime.now()
    first_day_of_month = datetime(now.year, now.month, 1)
    last_day_of_month = datetime(now.year, now.month + 1, 1) - timedelta(days=1)

    weekday -= 1

    # 获取该月所有周几的日期
    weekday_dates = []
    current_date = first_day_of_month
    while current_date <= last_day_of_month:
        if current_date.weekday() == weekday:
            weekday_dates.append(current_date)
        current_date += timedelta(days=1)

    # 如果找到对应的第n个周几，返回日期，否则返回“本月无第n个周X”
    if len(weekday_dates) >= n:
        return weekday_dates[n - 1].strftime("%Y-%m-%d")
    else:
        return f"无第{n}个周{calendar.day_name[weekday]}"


def create_yut_post(get_day, movie_list, filename):
    path = resource_path(f'./Resource/cache/file/{filename}')
    file = open(path + '/' + '【YUt】帖子模板.txt', 'w', encoding='utf-8')
    file.write('标题：\n')
    p_time = get_beijing_time()[4]
    file.write(
        f'【整理】【115ed2k+磁力链接】只需消耗一配额，今日预告全收着！（{get_day}【{len(movie_list)}V+{len(movie_list)}P/[*size*]GB/1配额】\n')
    file.write('\n使用方法:\n')
    file.write('※ 堂内新建空白帖子  -->  勾选“纯文本” -->  复制 "*" 线下方所有内容粘贴到空白帖 -> 取消“纯文本”\n')
    file.write('※ 粘贴前确保“纯文本”按钮已被勾选\n')
    file.write(
        '*****************************************************************************************************\n')
    file.write(f'[font=楷体, 楷体_GB2312][size=4]【资源名称】：{p_time.month}月{p_time.day}日新作打包合集（预告片+封面）\n')
    file.write('【资源类型】：视频+图片\n')
    file.write(f'【有码无码】：有码无水印\n')
    file.write(f'【资源大小】：{len(movie_list)}V+{len(movie_list)}P/[*size*]GB/1配额】\n')
    file.write('【资源预览】：[/size][/font]\n')
    file.write(
        '[align=center][img=600,28]https://t.tmh7.app/tupian/forum/202412/24/103034s7akw3kw7is66ael.png[/img][font=楷体, 楷体_GB2312][size=5]\n')
    file.write('FANZA预览新作的网页换了新的域名\n')
    file.write('现在只有日本节点才能访问\n')
    file.write('把更新的预告爬下来做了ed2k\n')
    file.write('内含本周更新的所有预告和封面\n')
    file.write('也做了一个磁力方便无115的堂友也能下载观看\n')
    file.write('堂友有什么建议也可以在帖子里提出[/size][/font][/align]\n')
    file.write(
        '[align=center][font=楷体, 楷体_GB2312][size=5]【**帖子链接A**】[/size][/font][/align][align=center][font=楷体, 楷体_GB2312][size=5]【**帖子链接B**】[/size][/font][/align]\n')
    file.write('[align=center][font=楷体, 楷体_GB2312][size=5]对新作有自己看法的堂友\n')
    file.write('可以移步[color=#ff0000]R哥[/color]和[color=#ff0000]礼部侍郎[/color]的新作预告贴展开讨论\n')
    file.write('他们对于新作是有一些自己的独到理解[/size][/font][/align][align=center]\n')
    file.write(
        '[img=600,28]https://t.tmh7.app/tupian/forum/202412/24/103034gn2g7rnfn7xnexqm.png[/img][/align][align=center]\n')
    file.write('[/size][/align]\n')
    file.write('[align=center]\n')
    file.write('[/size][/align]\n')
    file.write(
        '[font=楷体, 楷体_GB2312][size=4]【资源链接】：[/size][/font][code]ed2k[/code][code]磁链[/code][align=center][b][size=6][font=楷体, 楷体_GB2312]给个[/font][color=#ff00ff][font=楷体, 楷体_GB2312]免费[/font][/color][font=楷体, 楷体_GB2312]的评分吧！[/font][/size][/b][/align]\n')


def create_r_post(get_day, makers, movie_list, filename):
    path = resource_path(f'./Resource/cache/file/{filename}')
    file = open(path + '/' + '【R哥】帖子模板.txt', 'w', encoding='utf-8')
    file.write('标题：\n')
    p_time = get_beijing_time()[4]
    file.write(f'【新作预告】{"、".join(makers)} {p_time.month}月{p_time.day}日 新作预告\n')
    file.write('\n使用方法:\n')
    file.write('※ 堂内新建空白帖子  -->  勾选“纯文本” -->  复制 "*" 线下方所有内容粘贴到空白帖 -> 取消“纯文本”\n')
    file.write('※ 粘贴前确保“纯文本”按钮已被勾选\n')
    file.write(
        '*****************************************************************************************************\n')
    file.write(
        '[postbg]bg2.png[/postbg][b][size=4][font=微软雅黑][color=#ff0000]本期预告信息：[/color][/font][/size][/b][b]\n')
    file.write(f'[color=#444444][font=微软雅黑][size=3]{"、".join(makers)} 新作预告[/size][/font][/color]\n')
    file.write(f'[font=微软雅黑][size=3]配信日期：{get_day}（这天0点开始会陆续放出网络资源，堂内可获取）[/size][/font]\n')
    file.write(
        '[font=微软雅黑][size=3]其他厂商移步[color=#ff00ff]@礼部侍郎[/color][color=#444444]老哥的帖子[/color]：[/size][/font][/b]\n')
    file.write('[b][font=微软雅黑][size=3]【**帖子链接留白**】[/size][/font][/b]\n')
    file.write('\n')
    file.write('[b][font=微软雅黑][size=4][color=#ff0000]查看预告方式：[/color][/size][/font]\n')
    file.write('[font=微软雅黑][size=3][color=#444444]方法1：开启日本节点，点击视频链接[/color][/size][/font]\n')
    file.write(
        '[font=微软雅黑][size=3][color=#444444]方法2：点击下方链接获取[/color][/size][/font][font=微软雅黑][size=3][color=#ff00ff]@YUt[/color][/size][/font][font=微软雅黑][size=3][color=#444444]老哥下载好的视频和封面[/color][/size][/font][font=微软雅黑][size=3][color=#444444]帖子链接[/color][/size][/font][/b]\n')
    file.write('[font=微软雅黑][size=3][color=#444444][b]【**帖子链接留白**】[/b][/color][/size][/font]\n')
    file.write('[b][font=微软雅黑][size=3][color=#444444]\n')
    file.write(
        '[/color][/size][/font][size=4][font=微软雅黑][color=#ff0000]本期精彩看点：[/color][/font][/size][/b][b]\n')
    for maker in makers:
        number = sum(1 for movie in movie_list if movie['maker'] == maker)
        if number < 1 :
            continue
        file.write(f'[font=微软雅黑][size=3][color=#ff00ff]{maker} 更新 {number} 部[/color][/size][/font]\n')
        file.write(
            '[/b][b][color=#444444][font=微软雅黑][size=3]【**编辑文本留白**】[/size][/font][/color][/b][b][font=微软雅黑][size=3]\n')
        file.write('[b][font=微软雅黑][size=3][color=#ff0000]\n')
    file.write(
        '[/size][/font][font=微软雅黑][size=3][color=#ff0000][backcolor=yellow]喜欢的话，麻烦给个免费评分支持一下，感谢[/backcolor][/color][/size][/font][/b][/size]\n')
    file.write('[b][font=微软雅黑][size=3][color=#ff0000]\n')
    file.write(
        '[/color][/size][/font][/b][b][font=微软雅黑][size=4][color=#ff0000]新作预告：[/color][/size][/font][/b]\n')
    for maker in makers:
        number = sum(1 for movie in movie_list if movie['maker'] == maker)
        if number < 1 :
            continue
        file.write(f'[b][font=微软雅黑][size=3][color=#ff00ff]{maker}【{number}部】[/color][/size][/font][/b]\n')
        num = 1
        for movie in movie_list:
            if movie['maker'] == maker:
                file.write('[font=微软雅黑][size=3][color=#444444][/color][/size][/font]\n')
                file.write(
                    f'[b][size=3][color=#444444]【{num}/{number}】[/color][/size][url={movie["vedio"]}][size=3]{transform_string(movie["id"])}[/size][/url] [b][size=3][color=#444444]{movie["name"]}[/b][/size][/color]\n')
                file.write('[font=微软雅黑][size=3][color=#444444][/color][/size][/font]\n')
                num += 1
    file.write('[b][font=微软雅黑][size=3][color=#a0522d]SODstar新作放在评论区1楼[/color][/size][/font][/b]\n')
    file.write(
        '[b][font=微软雅黑][size=3][color=#a0522d]查看其他片商点击：[/color][/size][/font][/b][b][color=#444444][font=微软雅黑][size=3]【**帖子链接留白**】[/size][/font][/color][/b][b]\n')
    file.write(
        '[font=微软雅黑][size=3][color=#a0522d]查看封面和视频点击：[/color][/size][/font][/b][b][color=#444444][font=微软雅黑][size=3]【**帖子链接留白**】[/size][/font][/color][/b]\n')
    file.write('[font=微软雅黑][size=3][color=#ff0000][/color][/size][/font]\n')
    file.write(
        '[b][font=微软雅黑][size=4][color=#ff0000]以上就是今天的更新，你最期待哪部作品呢？[/color][/size][/font]\n')
    file.write('[font=微软雅黑][size=5][color=#ff0000]老哥们别忘了给个免费评分呀[/color][/size][/font][/b]\n')
    file.close()

def create_lbsl_post(get_day, makers, movie_list, filename):
    path = resource_path(f'./Resource/cache/file/{filename}')
    file = open(path + '/' + '【礼部侍郎】帖子模板.txt', 'w', encoding='utf-8')
    file.write('标题：\n')
    p_time = get_beijing_time()[4]
    p_now_time = get_beijing_time()[3]
    file.write(
        f'【新作预告】【北都+蚊香社】{p_time.month}月{p_time.day} E-BODY、Fitch、MVG、OPPAI、本中、無垢\n')
    file.write('\n使用方法:\n')
    file.write('※ 堂内新建空白帖子  -->  勾选“纯文本” -->  复制 "*" 线下方所有内容粘贴到空白帖 -> 取消“纯文本”\n')
    file.write('※ 粘贴前确保“纯文本”按钮已被勾选\n')
    file.write(
        '*****************************************************************************************************\n')
    file.write('[img=272,23]https://sehuatang.net/static/image/hrline/5.gif[/img]\n')
    file.write('\n')
    file.write('\n')
    file.write(
        '[font=微软雅黑][b][size=3][color=#0000ff]※ 直接观看视频需挂梯子并[/color][color=#ff00ff]选择小日子节点[/color][color=#0000ff]。[/color][/size][/b][/font][font=微软雅黑][b][size=3]\n')
    file.write('\n')
    file.write(
        '[color=#0000ff]※ 本没有日本节点可前往[/color][color=#ff00ff]@YUt[/color][color=#0000ff]老哥的帖子下载资源：\n')
    file.write('[/color][/size][/b][size=3][color=#ff0000][b][color=#ff00ff]【**帖子链接留白**】[/color][/b][/color]\n')
    file.write(
        '[/size][b][size=3][color=#0000ff]※ 同档期其他厂商预告移步[/color][color=#ff00ff]@R[/color][color=#0000ff]哥帖子：\n')
    file.write('[/color][/size][/b][b][color=#ff00ff][size=3]【**帖子链接留白**】[/size][/color][/b][/font]\n')
    file.write(
        '[b][font=微软雅黑][size=3][color=#0000ff]※ [/color][/size][size=3][color=#0000ff]整理不易，别忘了[/color][color=#ff0000]留个评分[/color][color=#0000ff]哟。感谢感谢[/color][/size][/font][/b]\n')
    file.write('\n')
    file.write('[img=272,23]https://sehuatang.net/static/image/hrline/5.gif[/img]\n')
    file.write('[font=微软雅黑][size=3][b][color=#0000ff][font=微软雅黑][size=3][b][color=#0000ff]\n')
    file.write('[/color][/b][/size][/font]\n')
    file.write('【WILL】（北都）集团主要片商【下月】新作预告：[/color][/b][/size][size=3][font=微软雅黑]\n')
    file.write('\n')
    file.write('[font=微软雅黑][size=3][b][color=#ff0000]【预告】排期列表：[/color][/b][/size][size=3][font=微软雅黑]\n')
    file.write('[table]\n')
    file.write(
        f'[tr][td][font=微软雅黑][size=3][color=#444444][b]第１个周二: {find_nth_weekday_of_month(1, 2)}[/b][/color][/size][/font][/td][td][font=微软雅黑][size=3][b]Moodyz（1）、Kawaii、Attackers[/b][/size][/font][/td][/tr]\n')
    file.write(
        '[tr][td][/td][td][font=微软雅黑][size=3][b]BeFree、Fitch（1）、MADOOOON、NPJ、WANZ[/b][/size][/font][/td][/tr]\n')
    file.write(
        f'[tr][td][font=微软雅黑][size=3][color=#444444][b]第２个周二: {find_nth_weekday_of_month(2, 2)}[/b][/color][/size][/font][/td][td][font=微软雅黑][size=3][b]S1（1）、Madonna（1）、IdeaPocket[/b][/size][/font][/td][/tr]\n')
    file.write(
        '[tr][td][/td][td][font=微软雅黑][size=3][b]BBAN、DAS（1）、HHH-Group（1）、Rookie[/b][/size][/font][/td][/tr]\n')
    file.write(
        f'[tr][td][font=微软雅黑][size=3][color=#444444][b]第３个周二: {find_nth_weekday_of_month(3, 2)}[/b][/color][/size][/font][/td][td][font=微软雅黑][size=3][b]Moodyz（2）、PREMIUM、溜池ゴロー[/b][/size][/font][/td][/tr]\n')
    file.write(
        '[tr][td][/td][td][font=微软雅黑][size=3][b]E-BODY、Fitch（2）、MVG、OPPAI、本中（1）、無垢[/b][/size][/font][/td][/tr]\n')
    file.write(
        f'[tr][td][font=微软雅黑][size=3][color=#444444][b]第４个周二: {find_nth_weekday_of_month(4, 2)}[/b][/color][/size][/font][/td][td][font=微软雅黑][size=3][b]S1（2）、Madonna（2）、本中（2）[/b][/size][/font][/td][/tr]\n')
    file.write(
        '[tr][td][/td][td][font=微软雅黑][size=3][b]DAS（2）、HHH-Group（2）、えむっ娘、痴女天堂[/b][/size][/font][/td][/tr]\n')
    file.write('[/table][font=微软雅黑][size=3]\n')
    file.write('※ 点击列表中对应档期的链接可跳转直达预告帖。\n')
    file.write('\n')
    file.write('※ 片商后面（1）、（2）表示该片商每个月有2个档期。\n')
    file.write(
        '例：如果在第1档【S1（1）】中没有看到【河北彩伽】（[/size][/font][/font][/size][/font][/font][/size][/font][font=微软雅黑][size=3]河北彩花[/size][/font][font=微软雅黑][size=3]）的话，\n')
    file.write('那就应该会在第2档【S1（2）】发布。其她女优同理。（档期一般都是固定的）\n')
    file.write('\n')
    file.write('※ 预告每月有4档，固定在周二发布。发行日为次月对应的周二。\n')
    file.write('（并不是按照自然月所对应的相同的日期）\n')
    file.write('例：12月第１个周二（12月03日）预告 → 1月第１个周二（1月07日）发行\n')
    file.write('\n')
    file.write('※ 配信日一般是提前4天，即发行日上一周的周五当天。\n')
    file.write('例：12月第２档（发行日：1月14日）→ 配信日为1月10日（周五）\n')
    file.write('（也就是说从配信日这天开始网上就有对应的资源可以下载了）\n')
    file.write('\n')
    file.write('※ 如遇节假日或者一个月有5个星期二等一些特殊情况，发布日期一般会轮空。\n')
    file.write('\n')
    file.write('※ 北都旗下片商众多全部集中于一帖发布过于凌乱，本帖仅对常见的同一档[/size][/font]\n')
    file.write(
        '[font=微软雅黑][font=微软雅黑][size=3][font=微软雅黑][font=微软雅黑][font=微软雅黑][size=3][font=微软雅黑][font=微软雅黑][font=微软雅黑][size=3][font=微软雅黑][font=微软雅黑][font=微软雅黑][size=3]期中R哥未发布的进行适当补充。其它集团的、独立厂商的本帖一般不作收录。\n')
    file.write('[/size][/font]\n')
    file.write('[align=center][b][img=430,20]https://sehuatang.net/static/image/hrline/1.gif[/img][/b][/align]\n')
    file.write('\n')
    file.write('[align=center][b][img=380,93]https://iili.io/J4nBce2.png[/img][/b][/align]\n')
    file.write('[align=center][b][color=#0000ff]【本期更新】[/color][/b][/align]\n')
    file.write(f'[align=center][b][color=#ff0000]{"、".join(makers)}[/color][/b][/align]\n')
    file.write(f'[align=center][b]※ 配信日：{get_day}（周五）[/b][/align]\n')
    file.write('[align=center][b]※ 从配信日0点开始会陆续放出网络资源，堂内可获取[/b][/align]\n')
    file.write('[/font][/font]\n')
    file.write('\n')
    file.write('[align=center][img=430,20]https://sehuatang.net/static/image/hrline/1.gif[/img][/align]\n')
    file.write('\n')
    file.write('\n')
    for maker in makers:
        for movie in movie_list:
            if movie['maker'] == maker:
                file.write('[font=微软雅黑][size=3][color=#444444][/color][/size][/font]\n')
                file.write(
                    f'[b] [size=3][color=#444444]{movie["name"]}[/size][/color]：[url={movie["vedio"]}][size=3]{transform_string(movie["id"])}[/size][/url][/b]\n')
                file.write('[font=微软雅黑][size=3][color=#444444][/color][/size][/font]\n')
                file.write('[font=微软雅黑][size=3][color=#444444][/color][/size][/font]\n')
        file.write('\n')
        file.write('[align=center][img=430,20]https://sehuatang.net/static/image/hrline/1.gif[/img][/align]\n')
        file.write('\n')
    file.write('\n')
    file.write(
        '[b][font=微软雅黑][size=3][color=#0000ff]【温故知新】 —— 【WILL】（北都）集团主要片商【本月】最新上线作品：[/color]\n')
    file.write('\n')
    file.write('[color=#ff0000]【配信】日期列表：[/color][/size][/font][size=3][font=微软雅黑]\n')
    file.write('[table]\n')
    file.write(
        f'[tr][td][font=微软雅黑][size=3][color=#444444]【**？**】上线：{find_nth_weekday_of_month(1, 5)}（周五）[/color][/size][/font][/td][td][font=微软雅黑][size=3]Moodyz（1）、Kawaii、Attackers[/size][/font][/td][/tr]\n')
    file.write('[tr][td][/td][td][font=微软雅黑][size=3]BeFree、Fitch（1）、MADOOOON、NPJ、WANZ[/size][/font][/td][/tr]\n')
    file.write(
        f'[tr][td][size=3][color=#000]【**？**】[/color][/size][font=微软雅黑][size=3][color=#444444]上线：{find_nth_weekday_of_month(2, 5)}（周五）[/color][/size][/font][/td][td][font=微软雅黑][size=3]S1（1）、Madonna（1）、IdeaPocket[/size][/font][/td][/tr]\n')
    file.write('[tr][td][/td][td][font=微软雅黑][size=3]BBAN、DAS（1）、HHH-Group（1）、Rookie[/size][/font][/td][/tr]\n')
    file.write(
        f'[tr][td][size=3][color=#000]【**？**】[/color][/size][font=微软雅黑][size=3][color=#444444]上线：{find_nth_weekday_of_month(3, 5)}（周五）[/color][/size][/font][/td][td][font=微软雅黑][size=3]Moodyz（2）、PREMIUM、溜池ゴロー[/size][/font][/td][/tr]\n')
    file.write(
        '[tr][td][/td][td][font=微软雅黑][size=3]E-BODY、Fitch（2）、MVG、OPPAI、本中（1）、無垢[/size][/font][/td][/tr]\n')
    file.write(
        f'[tr][td][size=3][color=#000]【**？**】上线[/color][/size][font=微软雅黑][size=3][color=#444444]：{find_nth_weekday_of_month(4, 5)}（周五）[/color][/size]\n')
    file.write('[/font][/td][td][font=微软雅黑][size=3]S1（2）、Madonna（2）、本中（2）[/size][/font][/td][/tr]\n')
    file.write(
        '[tr][td][/td][td][font=微软雅黑][size=3]DAS（2）、HHH-Group（2）、えむっ娘、痴女天堂[/size][/font][/td][/tr]\n')
    file.write('[/table][/b]\n')
    file.write('\n')
    file.write('\n')
    file.write('\n')
    file.write('[align=center][img=430,20]https://sehuatang.net/static/image/hrline/1.gif[/img][/align]\n')
    file.write('\n')
    file.write('[align=center][img=220,57]https://iili.io/dRxL8AP.png[/img][/align]\n')
    file.write('\n')
    file.write('\n')
    file.write(
        '[b][align=center][font=微软雅黑][size=4][color=#0000ff]【Prestige】（蚊香社） [/color][/size][/font][/align][/b]\n')
    file.write('[size=3][b]【**编辑留白**】[/b][/size]\n')

    file.close()

def count_unique_makers(nested_list):
    maker_set = set()
    for sublist in nested_list:
        for item in sublist:
            maker = item.get('maker')
            if maker is not None:
                maker_set.add(maker)
    return len(maker_set), list(maker_set)

def create_kokomi_post(get_day, makers, movie_list, filename):
    path = resource_path(f'./Resource/cache/file/{filename}')
    file = open(path + '/' + '【kokomigin】帖子模板.txt', 'w', encoding='utf-8')
    file.write('[postbg]bg2.png[/postbg]\n')
    file.write('\n')
    file.write('[index]\n')

    # cnts, mks = count_unique_makers(movie_list)

    file.write('[#1] 首页\n')
    file.write(f'[#2] {get_day} 配信内容\n')

    file.write('[/index]\n')
    file.write('\n')
    file.write('[align=center][img=600,100]https://tju.7pzzv.us/tupian/forum/202505/06/012251itpmssx3imrt1drz.gif[/img][/align]\n')
    file.write('\n')
    file.write('[align=center][img=667,500]https://tju.7pzzv.us/tupian/forum/202505/07/132249wkonu99tq24to0o4.gif[/img][/align]\n')
    file.write('\n')
    file.write('[align=center][img]https://tupian.li/images/2025/03/08/67cbf1ca30feb.png[/img][/align]\n')
    file.write('\n')

    file.write('[page]\n')

    file.write('\n')
    for mk in maker_all:
        number = sum(1 for movie in movie_list if movie['maker'] == mk)
        if number < 1:
            continue
        file.write(f'[align=center][font=微软雅黑][size=5][b] {mk} : 共{number}部 [/b][/size][/font][/align]\n')
        file.write('[align=center][font=微软雅黑][size=5] [/size][/font][/align]\n')
        for movie in movie_list:
            if movie['maker'] == mk:
                file.write(f'[b][color=#5375e1][font=微软雅黑][size=4]出演：{movie["name"]}[/size][/font][/color][/b]\n')
                file.write(f'[b][color=#5375e1][font=微软雅黑][size=4]番号：{transform_string(movie["id"])}[/size][/font][/color][/b]\n')
                file.write(f'[b][color=#5375e1][font=微软雅黑][size=4]片名：{movie["title"]}[/size][/font][/color][/b]\n')
                file.write('\n')
                file.write('[font=微软雅黑][size=4][color=#ff0000][b]【预览视频】[/b][/color][/size][/font]\n')
                file.write('\n')
                file.write('\n')
                file.write('[img]static/image/hrline/2.gif[/img]\n')
                file.write('\n')
                file.write('\n')
                file.write('\n')
    file.close()

def save_3(filename, makers, movie_list):
    save_file_with_type('face', filename, makers, movie_list)
    save_file_with_type('fanza', filename, makers, movie_list)
    save_file_with_type('vedio', filename, makers, movie_list)

# 每周厂商
weeks = {
    "week1": [
        "Moodyz",
        "Kawaii",
        "Attackers",
        "BeFree",
        "Fitch",
        "MADOOOON",
        "NPJ",
        "WANZ"
    ],
    "week2": [
        "S1",
        "IdeaPocket",
        "Madonna",
        "BBAN",
        "DAS",
        "HHH-Group",
        "Rookie"
    ],
    "week3": [
        "Moodyz",
        "PREMIUM",
        "溜池",
        "E-BODY",
        "Fitch",
        "MVG",
        "OPPAI",
        "本中",
        "無垢"
    ],
    "week4": [
        "S1",
        "Madonna",
        "本中",
        "DAS",
        "HHH-Group",
        "痴女天堂",
        "えむっ娘"
    ]
}
week = 'week' + str(get_beijing_time()[2])
# maker_this_week = weeks[week]  # 本周厂商
maker_all = ['Moodyz', 'S1', 'IdeaPocket', 'Madonna', 'PREMIUM', '溜池', 'Kawaii', 'Attackers', 'BeFree', 'NPJ',
             'WANZ', 'BBAN', 'DAS', 'OPPAI', '本中', 'HHH-Group', 'Rookie', 'E-BODY', 'Fitch', 'MVG', '無垢',
             'えむっ娘', '痴女天堂', 'MAX-A', 'LUNATICS', 'タカラ映像']
maker_this_week = maker_all

class Downloader:
    def __init__(self, code: str, date: str, cookie: str):
        self.code = code
        self.get_day = date
        self.cookie = cookie
        self.ban_words = []

        self.filename = '预告_' + self.get_day
        self.makers = get_exculsive_maker(maker_this_week, self.code)  # 专属用户厂商

        # 获取列表
        self.movie_list = []

        make_folder(self.filename)
        # self.solve_code()

    def solve_movie_list(self):
        self.movie_list = get_movie_list(self.cookie, self.get_day, self.ban_words, self.makers)
        # 按照 maker 排序，如果相同则按 id 排序
        for movie in self.movie_list:
            if movie['maker'] not in maker_all:
                maker_all.append(movie['maker'])
        self.movie_list = sorted(self.movie_list, key=lambda x: (maker_all.index(x["maker"]), x["id"]))
        # 删除0部的厂家
        for maker in maker_all:
            number = sum(1 for movie in self.movie_list if movie['maker'] == maker)
            if number < 1 and maker in self.makers:
                self.makers.remove(maker)

if __name__ == '__main__':

    pass
