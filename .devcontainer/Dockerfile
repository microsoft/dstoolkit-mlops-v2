FROM python:3.12-bullseye

RUN set -x

RUN apt-get update && apt-get -y install \
    curl \
    net-tools \
    procps \
    build-essential \
    docker.io \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --upgrade pip
RUN pip install ipython ipykernel
RUN ipython kernel install --user --name dstoolkit

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

RUN set +x

CMD bash
