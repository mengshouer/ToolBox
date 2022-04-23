# -*- coding: utf8 -*-

import requests, base64, json, hashlib, os, sys

sys.path.append(".")

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
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

netease_username = os.environ.get("netease_username")
netease_password = os.environ.get("netease_password")


def encrypt(key, text):
    backend = default_backend()
    cipher = Cipher(
        algorithms.AES(key.encode("utf8")),
        modes.CBC(b"0102030405060708"),
        backend=backend,
    )
    encryptor = cipher.encryptor()
    length = 16
    count = len(text.encode("utf-8"))
    if count % length != 0:
        add = length - (count % length)
    else:
        add = 16
    pad = chr(add)
    text1 = text + (pad * add)
    ciphertext = encryptor.update(text1.encode("utf-8")) + encryptor.finalize()
    cryptedStr = str(base64.b64encode(ciphertext), encoding="utf-8")
    return cryptedStr


def md5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding="utf-8"))
    return hl.hexdigest()


def protect(text):
    return {
        "params": encrypt("TA3YiYCfY2dDJQgg", encrypt("0CoJUm6Qyw8W8jud", text)),
        "encSecKey": "84ca47bca10bad09a6b04c5c927ef077d9b9f1e37098aa3eac6ea70eb59df0aa28b691b7e75e4f1f9831754919ea784c8f74fbfadf2898b0be17849fd656060162857830e241aba44991601f137624094c114ea8d17bce815b0cd4e5b8e2fbaba978c6d1d14dc3d1faf852bdd28818031ccdaaa13a6018e1024e2aae98844210",
    }


def run(*args):
    try:
        msg = ""
        s = requests.Session()
        url = "https://music.163.com/weapi/login/cellphone"
        url2 = "https://music.163.com/weapi/point/dailyTask"
        url3 = "https://music.163.com/weapi/v1/discovery/recommend/resource"
        logindata = {
            "phone": str(netease_username),
            "countrycode": "86",
            "password": md5(str(netease_password)),
            "rememberLogin": "true",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
        }
        headers2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
            "Referer": "http://music.163.com/",
            "Accept-Encoding": "gzip, deflate",
            "Cookie": "os=pc; osver=Microsoft-Windows-10-Professional-build-10586-64bit; appver=2.0.3.131777; channel=netease; __remember_me=true;",
        }

        res = s.post(url=url, data=protect(json.dumps(logindata)), headers=headers2)
        tempcookie = res.cookies
        object = json.loads(res.text)
        if object["code"] == 200:
            logger.info("登录成功！")
            msg += "登录成功！,"
        else:
            logger.info("登录失败！请检查密码是否正确！" + str(object))
            return f"登录失败！请检查密码是否正确！{object}"

        res = s.post(url=url2, data=protect('{"type":0}'), headers=headers)
        object = json.loads(res.text)
        if object["code"] != 200 and object["code"] != -2:
            logger.info("签到时发生错误：" + object["msg"])
            msg += "签到时发生错误,"
            pusher("Checkinbox通知", f"网易云音乐签到时发生错误{object['msg'][:200]}")
        else:
            if object["code"] == 200:
                logger.info("签到成功，经验+" + str(object["point"]))
                msg += "签到成功,"
            else:
                logger.info("重复签到")
                msg += "重复签到,"

        res = s.post(
            url=url3,
            data=protect(
                '{"csrf_token":"'
                + requests.utils.dict_from_cookiejar(tempcookie)["__csrf"]
                + '"}'
            ),
            headers=headers,
        )
        object = json.loads(res.text, strict=False)
        for x in object["recommend"]:
            url = (
                "https://music.163.com/weapi/v3/playlist/detail?csrf_token="
                + requests.utils.dict_from_cookiejar(tempcookie)["__csrf"]
            )
            data = {
                "id": x["id"],
                "n": 1000,
                "csrf_token": requests.utils.dict_from_cookiejar(tempcookie)["__csrf"],
            }
            res = s.post(url, protect(json.dumps(data)), headers=headers)
            object = json.loads(res.text, strict=False)
            buffer = []
            count = 0
            for j in object["playlist"]["trackIds"]:
                data2 = {}
                data2["action"] = "play"
                data2["json"] = {}
                data2["json"]["download"] = 0
                data2["json"]["end"] = "playend"
                data2["json"]["id"] = j["id"]
                data2["json"]["sourceId"] = ""
                data2["json"]["time"] = "240"
                data2["json"]["type"] = "song"
                data2["json"]["wifi"] = 0
                buffer.append(data2)
                count += 1
                if count >= 310:
                    break
            if count >= 310:
                break
        url = "http://music.163.com/weapi/feedback/weblog"
        postdata = {"logs": json.dumps(buffer)}
        res = s.post(url, protect(json.dumps(postdata)))
        object = json.loads(res.text, strict=False)
        if object["code"] == 200:
            text = "刷单成功！共" + str(count) + "首"
            logger.info(text)
            msg += text
        else:
            text = "发生错误：" + str(object["code"]) + object["message"]
            logger.info(text)
            msg += text
            pusher("Checkinbox通知", f"网易云音乐刷歌单时发生错误{object['message'][:200]}")
    except Exception as e:
        logger.info("repr(e):", repr(e))
        msg += "运行出错,repr(e):" + repr(e)
    return msg + "\n"


def main_handler(*args):
    msg = ""
    global netease_username, netease_password
    if "\\n" in netease_username:
        ulist = netease_username.split("\\n")
        plist = netease_password.split("\\n")
    else:
        ulist = netease_username.split("\n")
        plist = netease_password.split("\n")
    if len(ulist) == len(plist):
        i = 0
        while i < len(ulist):
            msg += f"第 {i+1} 个账号开始执行任务\n"
            netease_username = ulist[i]
            netease_password = plist[i]
            msg += run(netease_username, netease_password)
            i += 1
    else:
        msg = "账号密码个数不相符"
        logger.info(msg)
    return msg


if __name__ == "__main__":
    if netease_username and netease_password:
        logger.info("----------网易云音乐开始尝试执行日常任务----------")
        main_handler()
        logger.info("----------网易云音乐日常任务执行完毕----------")
