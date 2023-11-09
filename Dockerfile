FROM python:3.11-alpine

WORKDIR /app

ADD requirements.txt /app

RUN pip install -r requirements.txt

ADD clean-runners.py /app

CMD ["python", "clean-runners.py"]