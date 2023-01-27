# -*- coding: utf8 -*-

import requests, os, sys, json, time, re, urllib3, logging

sys.path.append(".")
urllib3.disable_warnings()
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

cookie = os.environ.get("cookie_pt")
pt_website = os.environ.get("pt_website")
proxy_url_http = os.environ.get("proxy_url_http")
proxy_url_https = os.environ.get("proxy_url_https")
if proxy_url_http and proxy_url_https:
    proxies = {"http": proxy_url_http, "https": proxy_url_https}
else:
    proxies = None


def main(cookie, website):
    s = requests.Session()
    thanks_id = 0
    if os.path.exists("./ptconfig.json"):
        with open("ptconfig.json", "r", encoding="utf8") as f:
            data = json.load(f)
        try:
            thanks_id = data[website]["thanks_id"]
            if thanks_id == "disable":
                return f"{website} 未启用说谢谢\n"
        except:
            try:
                data[website]["thanks_id"] = "disable"
            except:
                data[website] = {}
                data[website]["thanks_id"] = "disable"
            with open("./ptconfig.json", "w", encoding="utf8") as f:
                json.dump(data, f, ensure_ascii=False)
            return f"{website} 说谢谢初始化，自行修改起始id才会开始运行\n"
    else:
        try:
            data = {}
            data[website] = {}
            data[website]["thanks_id"] = "disable"
            with open("./ptconfig.json", "w", encoding="utf8") as f:
                json.dump(data, f, ensure_ascii=False)
            return f"{website} 说谢谢初始化，自行修改起始id才会开始运行\n"
        except:
            msg = "warning::: ptSayThanks.py无法写入ptconfig.json,请使用有读写权限的环境运行脚本\n"
            logger.info(msg)
            pusher("Checkinbox通知", msg)
            return msg
    url = f'{website.replace("index.php", "thanks.php")}'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": cookie,
        "Referer": website,
    }
    s.headers.update(headers)
    invalid_time = 0
    for id in range(int(thanks_id), int(thanks_id) + 110):
        time.sleep(0.8)
        try:
            r = s.post(url, data={"id": id}, proxies=proxies, verify=False)
            if not r.status_code == 200:
                break

            if not r.text:
                invalid_time = 0
                tips = "感谢成功，魔力 +1"
            else:
                r = re.compile(r'<tr><td class="text">(.+?)</td></tr>')
                tips = r.search(r.text).group(1)
                if tips == "Invalid torrent id!":
                    invalid_time += 1
                    if invalid_time > 40:
                        logger.info("种子连续不存在，任务终止")
                        id = id - 40
                        break
                else:
                    invalid_time = 0

            logger.info(f"种子id：{id}，{tips}")
        except:
            logger.warning(f"种子id：{id}，发生了点意外~")
    else:
        logger.info("本轮结束")

    data[website]["thanks_id"] = id
    with open("./ptconfig.json", "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)
    return ""


def main_handler(*args):
    msg = ""
    global cookie, pt_website
    if "\\n" in cookie:
        clist = cookie.split("\\n")
        weblist = pt_website.split("\\n")
    else:
        clist = cookie.split("\n")
        weblist = pt_website.split("\n")
    i = 0
    while i < len(clist):
        logger.info(f"第 {i+1} 个网站开始执行任务\n")
        cookie = clist[i]
        website = weblist[i]
        logger.info(main(cookie, website))
        i += 1
    return msg[:-1]


if __name__ == "__main__":
    if cookie:
        logger.info("----------PTwebsite_SayThanks开始尝试执行----------")
        main_handler()
        logger.info("----------PTwebsite_SayThanks执行完毕----------")
