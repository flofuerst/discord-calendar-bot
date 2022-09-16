FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN chmod -R 777 /app

COPY . .

CMD ["python3", "main.py"]