ARG BASE_IMAGE=mcr.microsoft.com/azureml/curated/pytorch-2.0-cuda11.7-cudnn8-ubuntu20.04

FROM ${BASE_IMAGE}

ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX" \
    TORCH_NVCC_FLAGS="-Xfatbin -compress-all" \
    CMAKE_PREFIX_PATH="$(dirname $(which conda))/../" \
    FORCE_CUDA="1"

# ARGS for non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Set timezone non-interactively
ENV DEBIAN_FRONTEND=noninteractive TZ=UTC

# Install the required packages
RUN apt-get update \
    && apt-get install -y ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libxrender-dev libcurl4 openssl unzip wget curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Create a non-root user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to non-root user
USER $USERNAME

# Create Python 3.10 conda env and install requirements
COPY ./requirements.txt .
RUN conda create -y -n prs-env python=3.10 pip \
    && conda clean -afy \
    && conda run -n prs-env pip install -r requirements.txt \
    && echo "conda activate prs-env" >> /home/$USERNAME/.bashrc

ENV CONDA_DEFAULT_ENV=prs-env
ENV PATH=/home/$USERNAME/.conda/envs/prs-env/bin:$PATH
