FROM python:alpine

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt && \
    pip install gunicorn

COPY . /app

WORKDIR /app

CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]