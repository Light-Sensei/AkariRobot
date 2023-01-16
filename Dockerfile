FROM python:3.10.2-buster

WORKDIR /root/KURUMIBOT

COPY . .

RUN pip install -r requirements.txt

CMD ["python3","-m","ShikimoriRobot"]
