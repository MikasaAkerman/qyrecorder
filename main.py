#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time

from pkg.acfun import AcFun


def start_recorder(room, path):
    while True:
        session = requests.session()
        recorder = AcFun(session, room, path)
        recorder.try_record()

        time.sleep(5 * 60)  # 5分钟执行一次


if __name__ == '__main__':
    start_recorder('378269', "videos")
