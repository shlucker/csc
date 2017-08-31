FROM python:2.7-slim

WORKDIR /app

ADD requirements.txt /app
ADD run.py /app

ADD . /app/csc

RUN pip install -r requirements.txt

EXPOSE 5000

#CMD ["python", "initialize_database.py"]
CMD ["python", "run.py"]
