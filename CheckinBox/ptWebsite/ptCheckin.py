# -*- coding: utf8 -*-

import requests, os, sys, re

sys.path.append(".")

try:
    from pusher import pusher
except:

    def pusher(*args):
        pass


cookie = os.environ.get("cookie_pt")
pt_website = os.environ.get("pt_website")
proxy_url_http = os.environ.get("proxy_url_http")
proxy_url_https = os.environ.get("proxy_url_https")
if proxy_url_http and proxy_url_https:
    proxies = {"http": proxy_url_http, "https": proxy_url_https}
else:
    proxies = None


def main(cookie, website):
    try:
        s = requests.Session()
        s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
            }
        )

        url = f"{website}?action=addbonus"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cookie": cookie,
            "Referer": website,
        }

        r = s.get(url, headers=headers, proxies=proxies, verify=False)
        award = re.compile(r"今天签到您获得\d+点魔力值").search(r.text)
        if award:
            msg = award.group(0)
        elif not award and "欢迎回来" in r.text:
            msg = "已经签到过了！"
        elif 'value="每日打卡"' in r.text:
            award = re.compile(r"恭喜您,获得了\d+魔力值奖励!").search(r.text)
            url = website.replace("index.php", "signin.php")
            r = s.get(url, headers=headers, verify=False)
            if award:
                msg = award.group(0)
            else:
                msg = f"PT站点{website} Cookie过期"
                pusher("Checkinbox通知", f"PT站点{website} Cookie过期\n{r.text[:200]}")
        elif 'value="已经打卡"' in r.text:
            msg = "已经签到过了！"
        else:
            msg = f"PT站点{website} Cookie过期"
            pusher("Checkinbox通知", f"PT站点{website} Cookie过期\n{r.text[:200]}")
    except Exception as e:
        print("repr(e):", repr(e))
        msg = "运行出错,repr(e):" + repr(e)
    return msg + "\n"


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
        msg += f"第 {i+1} 个网站开始执行任务\n"
        cookie = clist[i]
        website = weblist[i]
        msg += main(cookie, website)
        i += 1
    return msg


if __name__ == "__main__":
    if cookie:
        print("----------PTwebsite开始尝试签到----------")
        print(main_handler())
        print("----------PTwebsite签到执行完毕----------")
