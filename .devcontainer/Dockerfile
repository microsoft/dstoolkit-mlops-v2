FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

RUN set -x

RUN apt-get update \
    && apt-get -y install curl \
    && apt-get -y install net-tools \
    && apt-get -y install procps \
    && apt-get -y install build-essential \
    && apt-get -y install docker.io

RUN pip install ipython ipykernel
RUN ipython kernel install --user --name dstoolkit

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN set +x

CMD bash
