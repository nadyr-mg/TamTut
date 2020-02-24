FROM python:3.7.5

ENV APP_HOME=/src

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /src/
RUN pip install -r requirements.txt

COPY . $APP_HOME