import requests, sys, json, time, hashlib, os, sys

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

s = requests.Session()

note_username = os.environ.get("note_username")
note_password = os.environ.get("note_password")
user_dict = {}


def checkin(YNOTE_SESS):
    checkin_url = "http://note.youdao.com/yws/mapi/user?method=checkin"
    cookies = {"YNOTE_LOGIN": "true", "YNOTE_SESS": YNOTE_SESS}
    r = s.post(url=checkin_url, cookies=cookies, verify=False)
    if r.status_code == 200:
        info = json.loads(r.text)
        total = info["total"] / 1048576
        space = info["space"] / 1048576
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info["time"] / 1000))
        msg = (
            " 签到成功，本次获取 " + str(space) + " M, 总共获取 " + str(total) + " M, 签到时间 " + str(t)
        )
        return msg
    # cookie 登录失效或获取失败，改用用户名密码登录
    elif "AUTHENTICATION_FAILURE" in r.text:
        if note_username and note_password:
            YNOTE_SESS = login(note_username, note_password)
            if YNOTE_SESS:
                msg = checkin(YNOTE_SESS)
        else:
            msg = "未设置账号密码并且cookie过期"
        return msg
    else:
        pusher("Checkinbox通知", f"有道云笔记签到出现未知错误{r.text[:200]}")
        return r.text


def login(username, password):
    t = str(round(time.time() * 1000))
    login_url = (
        "https://note.youdao.com/login/acc/urs/verify/check?app=web&product=YNOTE&tp=ursto"
        "ken&cf=6&fr=1&systemName=&deviceType=&ru=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2Flo"
        "ginCallback.html&er=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&vc"
        f"ode=&systemName=Windows&deviceType=WindowsPC&timestamp={t}"
    )
    password = hashlib.md5(password.encode()).hexdigest()
    data = {"username": username, "password": password}
    r = s.post(url=login_url, data=data, verify=False)
    x = [i.value for i in s.cookies if i.name == "YNOTE_SESS"]
    if x.__len__() == 0:
        YNOTE_SESS = "-1"
        msg = f" {username} 有道云登录失败"
        pusher("Checkinbox通知", f"{msg}\n{r.text[:200]}")
        return ""
    else:
        logger.info(f"{username} 登陆成功，更新YNOTE_SESS,重新签到")
        YNOTE_SESS = x[0]
        # 尝试更新cookie到config.json
        try:
            global user_dict
            user_dict[f"{username}"] = YNOTE_SESS
            with open("./config.json", "w", encoding="utf8") as f:
                json.dump(user_dict, f, ensure_ascii=False)
        except:
            logger.info("有道云笔记无法写入config.json ,pass")
        return YNOTE_SESS


def main_handler(*args):
    try:
        with open("./config.json", "r", encoding="utf8") as f:
            data = json.load(f)
            msg = check(data)
    except:
        data = {}
        msg = check(data)
    return msg


def check(data):
    global note_username, note_password, user_dict
    msg = ""
    user_dict = data
    if "\\n" in note_username:
        ulist = note_username.split("\\n")
        plist = note_password.split("\\n")
    else:
        ulist = note_username.split("\n")
        plist = note_password.split("\n")
    # 如果cookie个数与账号数量不匹配则所有账号都重新登录一遍
    if len(data) != len(ulist):
        if len(ulist) == len(plist):
            i = 0
            while i < len(ulist):
                note_username = ulist[i]
                note_password = plist[i]
                YNOTE_SESS = login(note_username, note_password)
                if YNOTE_SESS:
                    msg += checkin(YNOTE_SESS)
                else:
                    msg += f"{note_username} 登录失败"
                msg += "\n"
                i += 1
        else:
            msg = "账号密码个数不相符"
        return msg
    else:
        c = 0
        # 防止存在不为账号的键值，重新登录所有账号
        for i in list(data):
            if i not in str(ulist):
                user_dict.pop(i)
                msg = check(user_dict)
                break
            YNOTE_SESS = data[i]
            note_username = ulist[c]
            note_password = plist[c]
            msg += checkin(YNOTE_SESS)
            msg += "\n"
            c += 1
        return msg


if __name__ == "__main__":
    if note_username and note_password:
        logger.info("----------有道云笔记开始尝试签到----------")
        logger.info(main_handler())
        logger.info("----------有道云笔记签到执行完毕----------")
