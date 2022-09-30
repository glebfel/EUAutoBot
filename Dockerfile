FROM ubuntu:latest
MAINTAINER Gleb Felyust 'felyust@list.ru'

# set env variables
ENV GECKODRIVER_VERSION v0.31.0
ENV FIREFOX_VERSION 105.0.1

RUN apt-get update -qy
RUN apt-get install -qy python3.10 python3-pip python3.10-dev \
fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip wget \
    xvfb

# download geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -zxf geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz


# donwnload firefox
RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-${FIREFOX_VERSION}&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

# copy project files and all dependencies
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3","main.py"]
