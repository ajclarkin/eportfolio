FROM python:3.12-alpine

RUN pip3 install flask

RUN pip3 install gunicorn

RUN pip3 install python-dateutil

WORKDIR /flask

ENTRYPOINT ["./gunicorn.sh"]
