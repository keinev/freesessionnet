# syntax=docker/dockerfile:1
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN rm -rf /var/lib/apt/lists/*
RUN apt update && \
    apt install python3 python3-pip gunicorn default-jre -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN rm -rf /var/lib/apt/lists/*

# gunicorn for website
COPY ./webapp /app
CMD ["gunicorn", "-w", "9", "-b", "0.0.0.0:8000", "local_website:app", "--chdir", "/app"]
