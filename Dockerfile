FROM python:3
RUN apt-get update && apt-get -y install libmysqlclient-dev --no-install-recommends

RUN mkdir /src
WORKDIR /src
COPY requirements.txt /src/
RUN ["pip", "install", "-r", "requirements.txt"]
COPY . /src/

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
