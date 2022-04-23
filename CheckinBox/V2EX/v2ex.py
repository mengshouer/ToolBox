import requests, json, time, os, re, sys

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

cookie = os.environ.get("cookie_v2ex")
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
    )

    # 获取签到的once
    url = "https://www.v2ex.com/mission/daily"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Cookie": cookie,
    }
    try:
        r = s.get(url, headers=headers, verify=False, proxies=None, timeout=120)
    except Exception as e:
        pusher("Checkinbox通知", f"v2ex签到失败，无法访问到网页{repr(e)}")
    # logger.info(r.text)
    if "需要先登录" in r.text:
        msg = "cookie失效啦！！！！\n"
        pusher("Checkinbox通知", f"V2EX  Cookie失效啦！！！\n{r.text[:200]}")
        return msg
    elif "每日登录奖励已领取" in r.text:
        msg = "今天已经签到过啦！！！\n"
        return msg
    once = re.compile(r"once\=\d+").search(r.text)
    # logger.info(once[0])

    # 签到
    sign_url = f"https://www.v2ex.com/mission/daily/redeem?{once[0]}"
    sign = s.get(sign_url, headers=headers, verify=False, proxies=proxies, timeout=120)
    # 获取签到情况
    r = s.get(url, headers=headers, verify=False)
    if "每日登录奖励已领取" in r.text:
        msg += "签到成功！"
        # 查看获取到的数量
        check_url = "https://www.v2ex.com/balance"
        r = s.get(
            check_url, headers=headers, verify=False, proxies=proxies, timeout=120
        )
        data = re.compile(r"\d+?\s的每日登录奖励\s\d+\s铜币").search(r.text)
        msg += data[0] + "\n"
    elif "登录" in sign.text:
        msg = "cookie失效啦！！！！\n"
        pusher("Checkinbox通知", "V2EX  Cookie失效啦！！！")
        return msg
    else:
        msg = "签到失败！\n"
        pusher("Checkinbox通知", f"V2EX  签到失败！！！\nsign.text[:200]")
    return msg


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
        logger.info("----------V2EX开始尝试签到----------")
        main_handler()
        logger.info("----------V2EX签到执行完毕----------")
