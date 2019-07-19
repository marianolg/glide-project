FROM python:3.7

COPY . /app

WORKDIR /app

RUN pip install --no-cache -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["gunicorn --bind 0.0.0.0:5000 -w 1 wsgi:app"]
