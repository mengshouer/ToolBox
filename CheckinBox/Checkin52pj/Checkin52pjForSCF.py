# -*- coding: utf8 -*-

import requests, os, sys, re
from bs4 import BeautifulSoup

sys.path.append(".")

import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
try:
    from pusher import pusher
except:

    def pusher(*args):
        pass


try:
    from notify import send as pusher
except:
    logger.info("无青龙推送文件")


cookie = os.environ.get("cookie_52pj")
pj_rate = os.environ.get("rate_52pj")
proxy_url_http = os.environ.get("proxy_url_http")
proxy_url_https = os.environ.get("proxy_url_https")
if proxy_url_http and proxy_url_https:
    proxies = {"http": proxy_url_http, "https": proxy_url_https}
else:
    proxies = None
s = requests.session()
headers = {
    "ContentType": "text/html;charset=gbk",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
}


def main(*args):
    msg = ""
    s.put(
        "https://www.52pojie.cn/home.php?mod=task&do=apply&id=2",
        headers=headers,
        proxies=proxies,
    )
    r = s.put(
        "https://www.52pojie.cn/home.php?mod=task&do=draw&id=2",
        headers=headers,
        proxies=proxies,
    )
    br = BeautifulSoup(r.text, "html.parser")
    text = br.find("div", id="messagetext").find("p").text
    if "您需要先登录才能继续本操作" in text:
        msg += "Cookie 失效"
    elif "恭喜" in text:
        msg += "签到成功"
    elif "不是进行中的任务" in text:
        msg += "不是进行中的任务"
    else:
        msg += "签到失败"
    return msg + "\n"


def pjRate(*args):
    msg = ""
    try:
        # 获取热门帖子
        rssurl = "https://www.52pojie.cn/forum.php?mod=guide&view=hot&rss=1"
        r = s.get(rssurl, headers=headers, proxies=proxies)
        tidlist = re.findall("tid=\d+", r.text)
        for tid in tidlist:
            tid = tid[4:]
            # 获取评分所需信息
            url = f"https://www.52pojie.cn/forum.php?mod=viewthread&tid={tid}"
            r = s.get(url, headers=headers, proxies=proxies)
            if "需要登录" in r.text:
                pusher("52pojie  Cookie过期")
                msg += "cookie_52pj失效，需重新获取"
                break
            formhash = re.findall("formhash=\w+", r.text)[0][9:]
            pid = re.findall("pid=\d+", r.text)[0][4:]
            data = {
                "formhash": formhash,
                "tid": tid,
                "pid": pid,
                "referer": f"https://www.52pojie.cn/forum.php?mod=viewthread&tid={tid}&page=0#pid{pid}",
                "handlekey": "rate",
                "score2": "1",
                "score6": "1",
                "reason": "热心回复！".encode("GBK"),
            }
            # 免费评分
            rateurl = "https://www.52pojie.cn/forum.php?mod=misc&action=rate&ratesubmit=yes&infloat=yes&inajax=1"
            r = s.post(rateurl, headers=headers, proxies=proxies, data=data)
            if "succeedhandle_rate" in r.text:
                msg += re.findall("succeedhandle_rate\('.*'", r.text)[0][19:]
                break
            elif "评分数超过限制" in r.text:
                msg += re.findall("errorhandle_rate\('.*'", r.text)[0][18:-1]
                break
            else:
                msg += re.findall("errorhandle_rate\('.*'", r.text)[0][18:-1]
                msg += "\n"
    except:
        # pusher("52pojie  免费评分失败")
        pass
    return msg + "\n"


def main_handler(*args):
    global cookie, headers
    msg = ""
    if "\\n" in cookie:
        clist = cookie.split("\\n")
    else:
        clist = cookie.split("\n")
    for i, c in enumerate(clist):
        if len(c) <= 0:
            continue
        msg += f"第 {i+1} 个账号开始执行任务\n"
        headers["Cookie"] = c
        msg += main()
        if pj_rate:
            msg += pjRate()
    logger.info(msg[:-1])
    return msg


if __name__ == "__main__":
    if cookie:
        logger.info("----------52pojie开始尝试签到----------")
        main_handler()
        logger.info("----------52pojie签到执行完毕----------")
