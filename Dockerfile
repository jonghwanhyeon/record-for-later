FROM python:3.6-slim

LABEL maintainer="hyeon0145@gmail.com"

RUN apt-get update && apt-get install -y \
    ffmpeg \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /rfl
COPY . /rfl

RUN pip --no-cache-dir install --requirement requirements.txt

ENTRYPOINT ["python", "run.py"]