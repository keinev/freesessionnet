# syntax=docker/dockerfile:1
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN rm -rf /var/lib/apt/lists/*
RUN apt update && \
    apt install python3 python3-pip gunicorn -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/bin/gunicorn", "--workers=2", "--log-file=-", "--worker-tmp-dir=/dev/shm", "--threads=4", "--worker-class=gthread",  "--bind", "unix:/tmp/website.sock", "-m", "007", "--user", "www-data", "--chdir", "/tmp/site", "-k", "uvicorn.workers.UvicornWorker", "search_server:app"]