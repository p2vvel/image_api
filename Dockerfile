FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apt update
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./image_api/ .