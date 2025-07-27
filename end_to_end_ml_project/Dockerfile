FROM python:3.11-slim-buster

WORKDIR /app

COPY . /app

RUN apt update && apt install awscli-y

RUN pip install -r /tmp/requirements.txt

CMD ["python3", "app.py"]