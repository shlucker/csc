FROM python:2.7-slim

WORKDIR /app

ADD requirements.txt /app
ADD run.py /app
ADD initialize_database.py /app

ADD ./csc /app/csc

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["python", "initialize_database.py"]
CMD ["python", "run.py"]
