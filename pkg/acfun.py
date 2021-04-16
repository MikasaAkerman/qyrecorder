import datetime
import time
import json
import os
from bs4 import BeautifulSoup


class AcFun(object):
    room_url = "https://live.acfun.cn/live/{}"
    anonymous_login_url = "https://id.app.acfun.cn/rest/app/visitor/login"
    start_play_url = "https://api.kuaishouzt.com/rest/zt/live/web/startPlay"
    user_info = {}
    start_time = 0
    headers = {
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
    }

    def __init__(self, session, room, path, user='', password=''):
        self.session = session
        self.room = room
        self.path = path
        self.user = user
        self.password = password

        if not os.path.exists(path):
            os.mkdir(path)

    def live_page(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        headers.update(self.headers)

        resp = self.session.get(self.room_url.format(self.room), headers=headers)
        if resp.ok:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for script in soup.find_all("script"):
                if script.string.startswith("window.__INITIAL_STATE__="):
                    state = json.loads(script.string[len("window.__INITIAL_STATE__="):-len(
                        ";(function(){var s;(s=document.currentScript||document.scripts[document.scripts.length-1]).parentNode.removeChild(s);}());")])
                    if hasattr(state["headers"], "cookie"):
                        setattr(self.headers, "cookie", state["headers"]["cookie"])
                    return

    def login(self):
        if self.user == '':
            return self.anonymous_login()

    def anonymous_login(self):
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json, text/plain, */*",
        }
        headers.update(self.headers)
        data = {
            "sid": "acfun.api.visitor"
        }
        self.user_info = self.session.post(self.anonymous_login_url, data=data, headers=headers).json()

    def start_play(self):
        headers = self.headers
        headers.update({
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json, text/plain, */*",
            "origin": "https://live.acfun.cn",
            "referer": "https://live.acfun.cn/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        })
        response = self.session.post(self.start_play_url, data={
            "authorId": self.room,
            "pullStreamType": "FLV"
        }, params={
            "subBiz": "mainApp",
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "userId": self.user_info["userId"],
            "did": self.session.cookies.get("_did"),
            "acfun.api.visitor_st": self.user_info["acfun.api.visitor_st"]
        }, headers=headers)
        resp = response.json()

        if resp["result"] != 1:
            raise Exception(resp["error_msg"])

        res = json.loads(resp["data"]["videoPlayRes"])
        print("chose media type", res["liveAdaptiveManifest"][0]["adaptationSet"]["representation"][-1]["name"])
        return res["liveAdaptiveManifest"][0]["adaptationSet"]["representation"][-1]["url"]

    def record(self, url):
        print("start recording at", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.start_time = datetime.datetime.now()
        if os.path.isabs(self.path):
            file_path = os.path.join(os.curdir, self.path,
                                     time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + ".flv")
        else:
            file_path = os.path.join(self.path,
                                     time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + ".flv")

        response = self.session.get(url, stream=True)

        block_size = 1024 * 4  # 4 Kib
        with open(file_path, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
                print('\r recording length %ds.' % (datetime.datetime.now() - self.start_time).seconds, end="")
                if file.tell() > 15 * 1024 * 1024 * 1024:  # single file max size: 15G
                    print('\n rotate file.')
                    return
            print("\n")

    def try_record(self):
        try:
            self.live_page()
            self.login()
            url = self.start_play()
            self.record(url)
        except Exception as e:
            print("try to record AcFun room {} failed. because {}".format(self.room, e))
            return False
        print("record success.")
        return True
