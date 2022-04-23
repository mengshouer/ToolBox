import requests
import json
import os


def pusher(*args):
    testmsg = ""
    msg = args[0]
    othermsg = ""
    for i in range(1, len(args)):
        othermsg += args[i]
        othermsg += "\n"

    # region server酱推送
    SCKEY = os.environ.get("SCKEY")  # http://sc.ftqq.com/
    SCTKEY = os.environ.get("SCTKEY")  # http://sct.ftqq.com/
    if SCKEY:
        sendurl = f"https://sc.ftqq.com/{SCKEY}.send"
        data = {"text": msg, "desp": othermsg}
        r = requests.post(sendurl, data=data)
        testmsg += f"{r.text}\n"
    if SCTKEY:
        sendurl = f"https://sctapi.ftqq.com/{SCTKEY}.send"
        data = {"title": msg, "desp": othermsg}
        r = requests.post(sendurl, data=data)
        testmsg += f"{r.text}\n"
    # endregion

    # region pushplus推送
    pushplus_token = os.environ.get("pushplus_token")  # http://www.pushplus.plus/
    pushplus_topic = os.environ.get("pushplus_topic")  # pushplus一对多推送需要的"群组编码"，一对一推送不用管
    if pushplus_token:
        sendurl = "http://www.pushplus.plus/send"
        if not othermsg:
            othermsg = msg
        if pushplus_topic:
            params = {
                "token": pushplus_token,
                "title": msg,
                "content": othermsg,
                "template": "html",
                "topic": pushplus_topic,
            }
        else:
            params = {
                "token": pushplus_token,
                "title": msg,
                "content": othermsg,
                "template": "html",
            }
        r = requests.post(sendurl, params=params)
        testmsg += f"{r.text}\n"
        if r.json()["code"] != 200:
            print(r.json())
            print(f"pushplus推送失败！{r.json()['msg']}")
    # endregion

    # region 酷推推送
    Skey = os.environ.get("Skey")  # https://cp.xuthus.cc/
    Smode = os.environ.get(
        "Smode"
    )  # send, group, psend, pgroup, wx, tg, ww, ding(no send email)
    if Skey:
        if not Smode:
            Smode = "send"
        if othermsg:
            msg = msg + "\n" + othermsg
        sendurl = f"https://push.xuthus.cc/{Smode}/{Skey}"
        params = {"c": msg}
        r = requests.post(sendurl, params=params)
        testmsg += f"{r.text}\n"
    # endregion

    # region telegram bot推送
    tg_token = os.environ.get("tg_token")  # telegram bot的Token，telegram机器人通知推送必填项
    tg_chatid = os.environ.get("tg_chatid")  # 接收通知消息的telegram用户的id，telegram机器人通知推送必填项
    tg_api_host = os.environ.get(
        "tg_api_host"
    )  # Telegram api自建的反向代理地址(不懂忽略)，默认tg官方api=api.telegram.org
    if tg_token and tg_chatid:
        if tg_api_host:
            sendurl = f"https://{tg_api_host}/bot{tg_token}/sendMessage"
        else:
            sendurl = f"https://api.telegram.org/bot{tg_token}/sendMessage"
        params = {"chat_id": tg_chatid, "text": f"{msg}\n{othermsg}"}
        r = requests.post(sendurl, data=params)
        testmsg += f"{r.text}\n"
    # endregion

    # region SMTP邮箱推送
    smtp_host = os.environ.get("smtp_host")  # 邮件服务器地址    QQ邮箱例子："smtp.qq.com"
    smtp_port = os.environ.get("smtp_port")  # 邮件服务器端口    QQ邮箱例子：465
    smtp_user = os.environ.get("smtp_user")  # 邮件服务器用户名  QQ邮箱例子："xxxxx@qq.com"
    smtp_pass = os.environ.get(
        "smtp_pass"
    )  # 邮件服务器密码    QQ邮箱例子：进入QQ邮箱，设置->账户->POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务里面有个生成授权码
    smtp_sender = os.environ.get("smtp_sender")  # 邮件发送者    QQ邮箱例子："xxxxx@qq.com"
    smtp_receiver = os.environ.get(
        "smtp_receiver"
    )  # 邮件接收者  QQ邮箱例子："user1@qq.com" 多账号"用户1@qq.com\n用户2@qq.com"(就是直接换行)
    if (
        smtp_host
        and smtp_port
        and smtp_user
        and smtp_pass
        and smtp_sender
        and smtp_receiver
    ):
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header

        try:
            smsg = MIMEText(msg + "\n" + othermsg, "plain", "utf-8")
            smsg["From"] = Header(smtp_sender, "utf-8")
            smtp_receiver = smtp_receiver.split("\n")
            smsg["To"] = Header(";".join(smtp_receiver), "utf-8")
            smsg["Subject"] = Header(msg, "utf-8")
            smtpObj = smtplib.SMTP_SSL(smtp_host, smtp_port)
            smtpObj.login(smtp_user, smtp_pass)
            smtpObj.sendmail(smtp_sender, smtp_receiver, smsg.as_string())
            testmsg += "邮件发送成功\n"
            smtpObj.quit()
        except Exception as e:
            testmsg += f"邮件发送失败：{e}\n"
    # endregion

    # region 企业微信应用消息通知设置(详见文档 https://work.weixin.qq.com/api/doc/90000/90135/90236)
    # 环境变量名 QYWX_AM依次填入 corpid,corpsecret,touser(注:多个成员ID使用|隔开),agentid,消息类型(选填,不填默认文本消息类型)
    # 注意用,号隔开(英文输入法的逗号)，例如：wwcff56746d9adwers,B-791548lnzXBE6_BWfxdf3kSTMJr9vFEPKAbh6WERQ,mingcheng,1000001,2COXgjH2UIfERF2zxrtUOKgQ9XklUqMdGSWLBoW_lSDAdafat
    # 可选推送消息类型(推荐使用图文消息（mpnews）): - 文本卡片消息: 0 (数字零)  - 文本消息: 1 (数字一)  - 图文消息（mpnews）: 素材库图片id
    QYWX_AM = os.environ.get("QYWX_AM")
    if QYWX_AM:
        QYWX_AM_AY = QYWX_AM.split(",")
        if 4 < len(QYWX_AM_AY) > 5:
            testmsg += "QYWX_AM 设置错误!!\n取消推送"
        else:
            corpid = QYWX_AM_AY[0]
            corpsecret = QYWX_AM_AY[1]
            touser = QYWX_AM_AY[2]
            agentid = QYWX_AM_AY[3]
            try:
                media_id = QYWX_AM_AY[4]
            except IndexError:
                media_id = ""
            wx = WeCom(corpid, corpsecret, agentid)
            # 如果没有配置 media_id 默认就以 text 方式发送
            if not media_id:
                r = wx.send_text(msg + othermsg, touser)
            else:
                r = wx.send_mpnews(msg, othermsg, media_id, touser)
            if r == "ok":
                testmsg += "企业微信推送成功！"
            else:
                testmsg += "企业微信推送失败！错误信息如下：\n" + r
    # endregion

    return testmsg


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace("\n", "<br/>"),
                        "digest": message,
                    }
                ]
            },
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]
