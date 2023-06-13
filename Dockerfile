FROM python:3.12.0b1-buster

WORKDIR /root/KURUMIBOT

COPY . .

RUN pip install -r requirements.txt

CMD ["python3","-m","AkariRobot"]
