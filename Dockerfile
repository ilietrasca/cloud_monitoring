FROM python:3-alpine

ADD ./src/app.py /
ADD ./src/var.py /

RUN pip install --upgrade pip \
        && pip install prometheus-client \
        && pip install beautifulsoup4 \
        && pip install requests

CMD [ "python", "./app.py" ]