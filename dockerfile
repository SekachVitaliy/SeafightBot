FROM python:3.9

RUN mkdir /src
WORKDIR /src
COPY requirements.txt /src
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /src