FROM python:3.8.5-alpine

LABEL maintainer="Lucas <dongliang_cq@qq.com>"

ENV PYTHONUNBUFFERED 0

COPY requirements.txt requirements.txt
COPY pkg /app/pkg
COPY *.py /app/

RUN mkdir -p /app \
    && pip install -i http://pypi.douban.com/simple/ -r requirements.txt --trusted-host pypi.douban.com

WORKDIR /app

VOLUME /app/videos

ENTRYPOINT ["python", "-u", "main.py"]