# -*- coding: utf8 -*-

import requests, time, re, rsa, json, base64, os, sys

sys.path.append(".")

from urllib import parse
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

username = os.environ.get("username_c189")
password = os.environ.get("password_c189")


def main(username: str, password: str):
    try:
        msg = ""
        s = login(username, password)
        if s == "error":
            return "天翼云盘登录出错"
        else:
            msg += "登录成功\n"
        rand = str(round(time.time() * 1000))
        surl = f"https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K"
        url = f"https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN"
        url2 = f"https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6",
            "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
            "Host": "m.cloud.189.cn",
            "Accept-Encoding": "gzip, deflate",
        }
        # 签到
        response = s.get(surl, headers=headers, timeout=20)
        netdiskBonus = response.json()["netdiskBonus"]
        if response.json()["isSign"] == "false":
            msg += f"未签到，签到获得  {netdiskBonus}  M空间\n"
        else:
            msg += f"已经签到过了，签到获得  {netdiskBonus}  M空间,"

        # 第一次抽奖
        response = s.get(url, headers=headers, timeout=20)
        if "errorCode" in response.text:
            if "User_Not_Chance" in response.text:
                msg += "抽奖次数不足,"
            elif "InternalError" in response.text:
                msg += "内部错误，可能是活动下线,"
            else:
                msg += "第一次抽奖出错\n" + response.text
                pusher("Checkinbox通知", f"天翼云盘第一次抽奖出错\n{response.text[:200]}")
        else:
            try:
                description = response.json()["description"]
            except:
                description = "未知"
            msg += f"抽奖获得  {description}  ,"

        # 第二次抽奖
        response = s.get(url2, headers=headers, timeout=20)
        if "errorCode" in response.text:
            if "User_Not_Chance" in response.text:
                msg += "抽奖次数不足,"
            elif "InternalError" in response.text:
                msg += "内部错误，可能是活动下线,"
            else:
                msg += "第二次抽奖出错\n" + response.text
                pusher("Checkinbox通知", f"天翼云盘第二次抽奖出错\n{response.text[:200]}")
        else:
            try:
                description = response.json()["description"]
            except:
                description = "未知"
            msg += f"抽奖获得  {description}  ,"
    except Exception as e:
        pusher("Checkinbox通知", f"天翼云签到出错{repr(e)}")
        msg += "天翼云签到出错：" + repr(e)
    return msg + "\n"


BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")


def int2char(a):
    return BI_RM[a]


b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def b64tohex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d


def rsa_encode(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex(
        (base64.b64encode(rsa.encrypt(f"{string}".encode(), pubkey))).decode()
    )
    return result


def login(username, password):
    s = requests.Session()
    url = "https://cloud.189.cn/api/portal/loginUrl.action?redirectURL=https://cloud.189.cn/web/redirect.html"
    r = s.get(url)
    captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
    lt = re.findall(r'lt = "(.+?)"', r.text)[0]
    returnUrl = re.findall(r"returnUrl = '(.+?)'", r.text)[0]
    paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
    j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
    s.headers.update({"lt": lt})

    username = rsa_encode(j_rsakey, username)
    password = rsa_encode(j_rsakey, password)
    url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0",
        "Referer": "https://open.e.189.cn/",
    }
    data = {
        "appKey": "cloud",
        "accountType": "01",
        "userName": f"{{RSA}}{username}",
        "password": f"{{RSA}}{password}",
        "validateCode": "",
        "captchaToken": captchaToken,
        "returnUrl": returnUrl,
        "mailSuffix": "@189.cn",
        "paramId": paramId,
    }
    r = s.post(url, data=data, headers=headers, timeout=5)
    if r.json()["result"] == 0:
        # logger.info(r.json()['msg'])
        pass
    else:
        msg = r.json()["msg"]
        logger.info(msg)
        pusher("Checkinbox通知", "天翼云盘登录出错", f"错误提示：{msg[:200]}")
        return "error"
    redirect_url = r.json()["toUrl"]
    r = s.get(redirect_url)
    return s


def main_handler(*args):
    msg = ""
    global username, password
    if "\\n" in username:
        ulist = username.split("\\n")
        plist = password.split("\\n")
    else:
        ulist = username.split("\n")
        plist = password.split("\n")
    if len(ulist) == len(plist):
        i = 0
        while i < len(ulist):
            msg += f"第 {i+1} 个账号开始执行任务\n"
            username = ulist[i]
            password = plist[i]
            msg += main(username, password)
            i += 1
    else:
        msg = "账号密码个数不相符\n"
    logger.info(msg[:-1])
    return msg


if __name__ == "__main__":
    if username and password:
        logger.info("----------天翼云盘开始尝试签到----------")
        main_handler()
        logger.info("----------天翼云盘签到执行完毕----------")
