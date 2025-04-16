

class XpathOfHome :
    photo = "/html/body[@id='nv_home']/div[@id='hd']/div[@class='wp']/div[@class='hdc cl']/div[@id='um']/div[@class='avt y']/a/img/@src"
    name = "/html/body[@id='nv_home']/div[@id='hd']/div[@class='wp']/div[@class='hdc cl']/div[@id='um']/p[1]/strong[@class='vwmy']/a/text()"
    uid = "/html/body[@id='nv_home']/div[@id='wp']/div[@id='ct']/div[@class='mn']/div[@class='bm bw0']/div[@class='bm_c']/div[@class='bm_c u_profile']/div[@class='pbm mbm bbda cl'][1]/h2[@class='mbn']/span[@class='xw0']/text()"
    group = "/html/body[@id='nv_home']/div[@id='wp']/div[@id='ct']/div[@class='mn']/div/div/div/div/ul/li/span/a/text()"
    score = "/html/body[@id='nv_home']/div[@id='wp']/div[@id='ct']/div[@class='mn']/div[@class='bm bw0']/div[@class='bm_c']/div[@class='bm_c u_profile']/div[@id='psts']/ul[@class='pf_l']/li[2]/text()"
    money = "/html/body[@id='nv_home']/div[@id='wp']/div[@id='ct']/div[@class='mn']/div[@class='bm bw0']/div[@class='bm_c']/div[@class='bm_c u_profile']/div[@id='psts']/ul[@class='pf_l']/li[4]/text()"
    rate = "/html/body[@id='nv_home']/div[@id='wp']/div[@id='ct']/div[@class='mn']/div[@class='bm bw0']/div[@class='bm_c']/div[@class='bm_c u_profile']/div[@id='psts']/ul[@class='pf_l']/li[6]/text()"
    coin = "/html/body[@id='nv_home']/div[@id='wp']/div[@id='ct']/div[@class='mn']/div[@class='bm bw0']/div[@class='bm_c']/div[@class='bm_c u_profile']/div[@id='psts']/ul[@class='pf_l']/li[5]/text()"

class XpathOfTheme :
    sector = "//table//tr/td[2]/a[@class='xg1']/text()"
    href = "//table//td[@class='icn']/a/@href"

class XpathOfSector:
    post_tid = "//div[@id='wp']/div//div[@class='mn']//tr/th/a/@href"

class XpathOfPost:
    title = '//div[@id="postlist"]//span[@id="thread_subject"]/text()'
    pid = '//div[@id="postlist"]/div[starts-with(@id,"post_")]/@id'
