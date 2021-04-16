FROM python:3.8.5-alpine

LABEL maintainer="Lucas <dongliang_cq@qq.com>"

ADD . /app

WORKDIR /app

VOLUME /app/videos

RUN pip install -i http://pypi.douban.com/simple/ -r requirements.txt --trusted-host pypi.douban.com

ENTRYPOINT ["python", "main.py"]