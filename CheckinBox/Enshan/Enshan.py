import requests, json, time, os, sys

sys.path.append(".")

from lxml import etree
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

cookie = os.environ.get("cookie_enshan")
proxy_url_http = os.environ.get("proxy_url_http")
proxy_url_https = os.environ.get("proxy_url_https")
if proxy_url_http and proxy_url_https:
    proxies = {"http": proxy_url_http, "https": proxy_url_https}
else:
    proxies = None


def run(*arg):
    msg = ""
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
        }
    )

    # 签到
    url = "https://www.right.com.cn/forum/home.php?mod=spacecp&ac=credit&op=log&suboperation=creditrulelog"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Connection": "keep-alive",
        "Host": "www.right.com.cn",
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": cookie,
    }
    try:
        r = s.get(url, headers=headers, proxies=proxies, timeout=120)
        # logger.info(r.text)
        if "每天登录" in r.text:
            h = etree.HTML(r.text)
            data = h.xpath("//tr/td[6]/text()")
            msg += f"签到成功或今日已签到，最后签到时间：{data[0]}"
        else:
            msg += "恩山论坛签到失败，可能是cookie失效了！"
            pusher("Checkinbox通知", msg)
    except:
        msg = "无法正常连接到网站，请尝试改变网络环境，试下本地能不能跑脚本，或者换几个时间点执行脚本"
    return msg + "\n"


def main_handler(*arg):
    msg = ""
    global cookie
    if "\\n" in cookie:
        clist = cookie.split("\\n")
    else:
        clist = cookie.split("\n")
    for i, c in enumerate(clist):
        if len(c) <= 0:
            continue
        msg += f"第 {i+1} 个账号开始执行任务\n"
        msg += run(c)
    logger.info(msg[:-1])
    return msg[:-1]


if __name__ == "__main__":
    if cookie:
        logger.info("----------恩山论坛开始尝试签到----------")
        main_handler()
        logger.info("----------恩山论坛签到执行完毕----------")
