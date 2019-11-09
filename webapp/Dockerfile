FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

COPY ./app /app
COPY ./uwsgi_flask_nginx/uwsgi_timeout.conf /etc/nginx/conf.d/
COPY ./uwsgi_flask_nginx/nginx.conf /etc/nginx/
COPY ./uwsgi_flask_nginx/supervisord/rq_worker.ini /etc/supervisor.d/


RUN apk add --no-cache postgresql-dev gcc python3 python3-dev musl-dev && \
  python3 -m ensurepip && \
  rm -r /usr/lib/python*/ensurepip && \
  pip install --upgrade pip setuptools && \
  rm -r /root/.cache && \
  pip install -r requirements.txt &&\
  rm requirements.txt

WORKDIR /app
