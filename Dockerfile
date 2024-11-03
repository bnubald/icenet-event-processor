# To enable ssh & remote debugging on app service change the base image to the one below
FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice

ENV AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    PYTHON_ISOLATE_WORKER_DEPENDENCIES=1

RUN apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /
RUN apt-get update && apt-get install -y \
    gcc g++ libeccodes-dev libgeos-dev pkg-config libhdf5-103 libhdf5-dev vim-tiny && \
    pip install --upgrade pip setuptools wheel && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man && \
    apt-get clean && \
    pip --no-cache-dir install --prefer-binary -r requirements.txt

COPY icenet-0.2.9.dev0-py2.py3-none-any.whl /
RUN pip install --no-deps /icenet-0.2.9.dev0-py2.py3-none-any.whl
COPY . /home/site/wwwroot
