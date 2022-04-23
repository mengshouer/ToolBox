# -*- coding: utf8 -*-

import requests, json, time, os, sys

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

cookie = os.environ.get("cookie_smzdm")


def main(*arg):
    try:
        msg = ""
        s = requests.Session()
        s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
            }
        )
        t = round(int(time.time() * 1000))
        url = f"https://zhiyou.smzdm.com/user/checkin/jsonp_checkin?_={t}"

        headers = {"cookie": cookie, "Referer": "https://www.smzdm.com/"}

        r = s.get(url, headers=headers, verify=False, timeout=10)
        logger.info(r.text.encode("latin-1").decode("unicode_escape"))
        if r.json()["error_code"] != 0:
            pusher("Checkinbox通知", f"smzdm  Cookie过期{r.text[:200]}")
            msg += "smzdm cookie失效"
        else:
            msg += "smzdm签到成功"
    except Exception as e:
        logger.info("repr(e):", repr(e))
        msg += "运行出错,repr(e):" + repr(e)
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
        msg += main(c)
    logger.info(msg[:-1])
    return msg[:-1]


if __name__ == "__main__":
    if cookie:
        logger.info("----------什么值得买开始尝试签到----------")
        main_handler()
        logger.info("----------什么值得买签到执行完毕----------")
