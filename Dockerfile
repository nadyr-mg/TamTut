FROM python:3.7.5

RUN mkdir /src
WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /src/
RUN pip install -r requirements.txt

COPY . /src/