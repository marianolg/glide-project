FROM python:3.7

COPY . /app

WORKDIR /app

RUN pip install --no-cache -r requirements.txt

EXPOSE 5000

ARG startcmd="gunicorn --bind 0.0.0.0:5000 -w 1 wsgi:app"
ENV startcmd=$startcmd

CMD ${startcmd}
