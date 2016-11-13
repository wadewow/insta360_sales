FROM python:2.7.12-alpine

MAINTAINER Thonatos.Yang <thonatos.yang@gmail.com>
LABEL vendor=implements.io
LABEL io.implements.version=0.1.0

ENV S6_OVERLAY_VERSION=v1.17.2.0 \
    HOME=/root

# update repositories
RUN sed -i "s/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g" /etc/apk/repositories

# use aliyun mirrors
COPY root/root/.pip/ /root/.pip/

# install package
RUN apk add --update curl gcc g++ libgcc make \
    zlib-dev mariadb-dev \
    nginx \
    && curl -sSL https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-amd64.tar.gz | tar xfz - -C /

# install  mysqlclient
RUN pip install mysqlclient

# clean cache & package
RUN apk del gcc g++ make curl \
    && rm -rf /usr/include /usr/share/man /tmp/* /var/cache/apk/*     

# nginx
RUN mkdir -p /app && \
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

ADD root /

# run server
COPY src/ /app

WORKDIR /app/

RUN pip install -r requirements.txt

VOLUME /app/sales/static/store

EXPOSE 80 443 8000

ENTRYPOINT ["/init"]