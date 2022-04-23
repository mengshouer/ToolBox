# CheckinBox

<details>
  <summary>目前已开发功能(不保证一定可用，随缘修)</summary>

- [天翼云盘每日签到一次 ~~抽奖 2 次~~](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/Cloud189Checkin)

- [最终幻想 14 积分商城签到](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/FF14Checkin)

- [什么值得买网页每日签到](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/smzdmCheckin)

- [52pojie 每日签到 + 免费评分](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/Checkin52pj)

- [网易云音乐每日签到与刷歌单](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/NetEase_Music_daily)

- [有道云笔记签到](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/NoteyoudaoCheckin)

- [V2EX 签到](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/V2EX)

- [恩山论坛签到](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/Enshan)

- [PT 站点签到](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/ptWebsite)

- [百度贴吧签到](https://github.com/mengshouer/ToolBox/tree/master/CheckinBox/Baidu)

</details>

<details>
  <summary>青龙运行方式</summary>

`docker exec -it qinglong bash` 进入容器

`python3 -m pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/` 更换 pip 源为阿里云的源

`python3 -m pip install --upgrade pip` 更新 pip 才能直接安装成功

在青龙面板添加一个任务并运行一次，后续自动更新依赖

`task python3 -m pip install -r https://ghproxy.com/https://raw.githubusercontent.com/mengshouer/ToolBox/master/CheckinBox/requirements.txt`

如果上面安装依赖报错，跑一边`apk add --no-cache rust cargo libxml2 libxslt libxml2-dev libxslt-dev`再安装一次

`ql repo https://github.com/mengshouer/ToolBox.git "CheckinBox" "pusher"` 拉取仓库

之后在环境变量里面添加需要运行的脚本的环境，具体需要的环境变量看脚本目录的说明

定时使用的是青龙拉取脚本时默认的定时规则，自行修改。

推送使用的是青龙自带的推送脚本。

</details>

### [腾讯云函数 SCF](https://console.cloud.tencent.com/scf/index)的版本

### SCF 计费问题：免费额度变少了，小心超额付费，[账单详细](https://console.cloud.tencent.com/expense/bill/summary?businessCode=p_scf)

1. 下载[requirements.zip](https://github.com/mengshouer/ToolBox/releases)所需库，到[层](https://console.cloud.tencent.com/scf/layer)里面新建一个层，运行环境选 Python3.7

2. 到[函数服务](https://console.cloud.tencent.com/scf/list)里面新建一个函数，选择从头开始，函数类型为事件函数，运行环境选择 python3.7，其他选项自己看着改，比较重要的有"执行超时时间"按需修改

3. 函数代码里修改执行方法为 index.main_handler，修改 index.py 文件，把 SCF 版 py 文件内容覆盖掉里面的函数

4. 高级设置，添加多个环境变量 key 内输入：1.env1_sample 2.env2_sample 3.推送服务设置值(可选)

    value 内输入：1.value1_sample 2.value2_sample 3.推送服务设置值(可选)， 具体的环境变量和值到各脚本里面查看

5. 层配置，添加层，选择刚才新建的层。最后点完成

6. 进入函数 → 触发管理 → 新建触发器，按自己需求定时启动

7. 自己酌情修改函数的内存与执行超时时间以及其他参数

<details>
  <summary>多账号设置</summary>

青龙多账号时账号密码一行一个一一对应<br>
腾讯云函数 SCF 在每个账号和密码后面添加\n，账号密码也是一一对应<br>
没写单独账号推送<br>

</details>

<details>
  <summary>报错提醒提示</summary>

推送可以设置的参数( Key/name(名称) --> Value(值) )：<br>
Github Actions 添加在 Setting→Secrets→New secrets，腾讯云函数 SCF 设置在环境变量里<br>

1. Key: SCKEY --> Value: [Server 酱的推送 SCKEY 的值](http://sc.ftqq.com/)<br>
2. Key: SCTKEY --> Value: [Server 酱·Turbo 版的推送 SCTKEY 的值](http://sct.ftqq.com/)<br>
3. Key: Skey --> Value: [酷推调用代码 Skey](https://cp.xuthus.cc/)<br>
4. Key: Smode --> Value: 酷推的推送渠道，不设置默认 send.可选参数(send,group,psend,pgroup,wx,tg,ww,ding)<br>
5. Key: pushplus_token --> Value: [pushplus 推送 token](http://www.pushplus.plus/)<br>
6. Key: pushplus_topic --> Value: pushplus 一对多推送需要的"群组编码"，一对一推送不用管填了报错<br>
7. Key: tg_token --> Value: Telegram bot 的 Token，Telegram 机器人通知推送必填项<br>
8. Key: tg_chatid --> Value: 接收通知消息的 Telegram 用户的 id，Telegram 机器人通知推送必填项<br>
9. Key: tg_api_host --> Value: Telegram api 自建的反向代理地址(不懂忽略此项)，默认 tg 官方 api=api.telegram.org<br>
10. Key: smtp_host smtp_port smtp_user smtp_pass smtp_sender smtp_receiver 使用 SMTP 邮箱推送<br>
11. Value: 邮件的服务器，端口，用户，密码，发送者，接受者<br>
12. Key: QYWX_AM 企业微信应用消息通知，具体参数看 pusher.py<br>
    PS:腾讯云函数 SCF 的默认无推送，需要推送的话需要将[pusher.py](https://github.com/mengshouer/ToolBox/blob/master/CheckinBox/pusher.py)内的内容直接复制到所需函数的代码最上方！！！

#### 一切提醒都是报错提醒，没问题不提醒

</details>

<details>
  <summary>代理设置</summary>

V2EX，pt 站点，恩山论坛可能国内节点有时候会无法访问，所以需要代理

环境变量添加：

Key: proxy_url_http --> Value: http 的代理地址，例如:http://127.0.0.1:7890

Key: proxy_url_https --> Value: https 的代理地址，例如:https://xxxxx

http 的地址可以用于 https，要使用代理必须两个都填

</details>

<details>
  <summary>Cookie获取方法</summary>

浏览器打开需要签到的网站并登录，F12 打开检查

在 Console 中输入：document.cookie，如果这个 cookie 能签到的话就不用看下面的了，如果不行按下面的方法获取

在 Chrome 浏览器下方的开发工具中单击 Network 标签页(其他浏览器大同小异)

F5 刷新当前网站，随便选一个 Name 里面的网页，在右侧 Headers 内找到 Cookie: xxxxxx，复制 xxxx 的东西，一般很长一大串

Headers 如果没有 Cookie 就换另一个 Name 里面的网页，实在看不懂就自行 baidu 吧.jpg

Cookie 过期就必须手动更换，再重复一次获取流程，然后更新环境变量

</details>

<details>
  <summary>小声 bb</summary>

~~旧仓库 AC 都关这么久了还能被 ban，没想到~~

</details>
