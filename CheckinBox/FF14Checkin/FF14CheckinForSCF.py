# -*- coding: utf8 -*-

import json
import time
import os
import requests, sys

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

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "CASCID=CID2BFCADB9A0154A9D877294366E144906; sdo_cas_id=10.129.20.137; CAS_LOGIN_STATE=1; sdo_dw_track=G81Y/L1voXjLY8VH5ZWfpw==; CASTGC=ULSTGT-f0caef48519646a09e4ecee2f864e40a",
    "Host": "cas.sdo.com",
    "Pragma": "no-cache",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
}

login_name = os.environ.get("fflogin_name")
login_password = os.environ.get("fflogin_password")
area_name = os.environ.get("area_name")
server_name = os.environ.get("server_name")
role_name = os.environ.get("role_name")
global cookie
cookie = {}


def __put_cookie(items):
    for item in items:
        cookie.setdefault(item[0], item[1])


# 提交用户名和密码, 获取ticket
def step1() -> str:
    logger.info("将以 %s 登录" % (login_name))
    params = {
        "callback": "staticLogin_JSONPMethod",
        "inputUserId": login_name,
        "password": login_password,
        "appId": "100001900",
        "areaId": "1",
        "serviceUrl": "http://act.ff.sdo.com/20180707jifen/Server/SDOLogin.ashx?returnPage=index.html",
        "productVersion": "v5",
        "frameType": "3",
        "locale": "zh_CN",
        "version": "21",
        "tag": "20",
        "authenSource": "2",
        "productId": "2",
        "scene": "login",
        "usage": "aliCode",
        "customSecurityLevel": "2",
        "autoLoginFlag": "0",
        "_": int(round(time.time() * 1000)),
    }
    url = "https://cas.sdo.com/authen/staticLogin.jsonp"
    r = requests.get(url, params=params, headers=headers)
    __put_cookie(r.cookies.items())
    text = r.text
    text = text[text.find("(") + 1 : text.rfind(")")]
    obj = json.loads(text)
    if "ticket" in obj["data"]:
        logger.info("登录成功, 正在设置cookie...")
        return obj["data"]["ticket"]
    else:
        logger.info("登录失败, 短期内登录失败次数过多, 服务器已开启验证码, 请在1-3天后再试...")
        pusher("Checkinbox通知", "FF14签到出错", "登录失败, 短期内登录失败次数过多, 服务器已开启验证码, 请在1-3天后再试...")
        return None


# 设置cookie
def step2():
    url = "http://login.sdo.com/sdo/Login/Tool.php"
    params = {
        "value": "index|%s" % login_name,
        "act": "setCookie",
        "name": "CURRENT_TAB",
        "r": "0.8326684884385089",
    }
    r = requests.get(url, params=params, cookies=cookie)
    __put_cookie(r.cookies.items())


# 设置cookie
def step3():
    url = "https://cas.sdo.com/authen/getPromotionInfo.jsonp"
    params = {
        "callback": "getPromotionInfo_JSONPMethod",
        "appId": "991000350",
        "areaId": "1001",
        "serviceUrl": "http://act.ff.sdo.com/20180707jifen/Server/SDOLogin.ashx?returnPage=index.html",
        "productVersion": "v5",
        "frameType": "3",
        "locale": "zh_CN",
        "version": "21",
        "tag": "20",
        "authenSource": "2",
        "productId": "2",
        "scene": "login",
        "usage": "aliCode",
        "customSecurityLevel": "2",
        "_": "1566623599098",
    }
    r = requests.get(url, params=params, cookies=cookie)
    __put_cookie(r.cookies.items())


# 设置cookie
def step4(ticket: str):
    url = (
        "http://act.ff.sdo.com/20180707jifen/Server/SDOLogin.ashx?returnPage=index.html&ticket="
        + ticket
    )
    r = requests.get(url, cookies=cookie)
    __put_cookie(r.cookies.items())
    logger.info("设置cookie成功...")


# 查询角色列表
def step5() -> str:
    ipid = ""
    if area_name == "陆行鸟":
        ipid = "1"
    elif area_name == "莫古力":
        ipid = "6"
    else:
        ipid = "7"
    url = "http://act.ff.sdo.com/20180707jifen/Server/ff14/HGetRoleList.ashx"
    params = {
        "method": "queryff14rolelist",
        "ipid": ipid,
        "i": "0.8075943537407986",
    }
    r = requests.get(url, params=params, cookies=cookie)
    text = r.text
    obj = json.loads(text)
    attach = obj["Attach"]
    role = "{0}|{1}|{2}"
    logger.info("正在获取角色列表...")
    for r in attach:
        if r["worldnameZh"] == server_name and r["name"] == role_name:
            logger.info("获取角色列表成功...")
            return role.format(r["cicuid"], r["worldname"], r["groupid"])
    logger.info("获取角色列表失败...")
    pusher("Checkinbox通知", "FF14签到出错", "获取角色列表失败...")
    return None


# 选择区服及角色
def step6(role: str):
    url = "http://act.ff.sdo.com/20180707jifen/Server/ff14/HGetRoleList.ashx"
    AreaId = ""
    if area_name == "陆行鸟":
        AreaId = "1"
    elif area_name == "莫古力":
        AreaId = "6"
    else:
        AreaId = "7"
    params = {
        "method": "setff14role",
        "AreaId": AreaId,
        "AreaName": area_name,
        "RoleName": "[%s]%s" % (server_name, role_name),
        "Role": role,
        "i": "0.8326684884385089",
    }
    r = requests.post(url, params=params, cookies=cookie)
    __put_cookie(r.cookies.items())
    logger.info("已选择目标角色...")


# 签到
def step7():
    logger.info("正在签到...")
    url = "http://act.ff.sdo.com/20180707jifen/Server/User.ashx"
    params = {"method": "signin", "i": "0.855755357775076"}
    r = requests.post(url, params=params, cookies=cookie)
    obj = json.loads(r.text)
    logger.info(obj["Message"])
    if obj["Message"] != "成功":
        pusher("Checkinbox通知", "FF14签到出错签到失败...")
        return False
    return True


# 查询当前积分
def step8():
    url = "http://act.ff.sdo.com/20180707jifen/Server/User.ashx"
    params = {"method": "querymystatus", "i": "0.855755357775076"}
    r = requests.post(url, params=params, cookies=cookie)
    obj = json.loads(r.text)
    attach = obj["Attach"]
    jifen = json.loads(attach)["Jifen"]
    logger.info("当前积分为: %d" % jifen)
    return jifen


def main(*arg):
    ticket = step1()
    if not ticket:
        return "登录失败, 短期内登录失败次数过多, 服务器已开启验证码, 请在1-3天后再试..."
    step2()
    step3()
    step4(ticket)
    role = step5()
    if not role:
        return "获取角色列表失败..."
    step6(role)
    r = step7()
    if r:
        jifen = step8()
        jifen = f"当前积分为: {jifen} "
        return jifen
    else:
        return "签到失败..."


def main_handler(*arg):
    msg = ""
    global login_name, login_password, area_name, server_name, role_name
    if "\\n" in login_name:
        nlist = login_name.split("\\n")
        plist = login_password.split("\\n")
        alist = area_name.split("\\n")
        slist = server_name.split("\\n")
        rlist = role_name.split("\\n")
    else:
        nlist = login_name.split("\n")
        plist = login_password.split("\n")
        alist = area_name.split("\n")
        slist = server_name.split("\n")
        rlist = role_name.split("\n")

    if len(nlist) == len(plist) == len(alist) == len(slist) == len(rlist):
        i = 0
        while i < len(nlist):
            msg += f"\n第 {i+1} 个账号开始执行任务\n"
            login_name = nlist[i]
            login_password = plist[i]
            area_name = alist[i]
            server_name = slist[i]
            role_name = rlist[i]
            msg += main()
            i += 1
    else:
        msg = "账号密码或其他参数个数不相符"
        logger.info(msg)
    return msg


if __name__ == "__main__":
    if login_name and login_password and area_name and server_name and role_name:
        logger.info("----------FF14积分商城开始尝试签到----------")
        main_handler()
        logger.info("----------FF14积分商城签到执行完毕----------")
