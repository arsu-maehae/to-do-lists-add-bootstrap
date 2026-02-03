FROM python:3.12-slim

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

#install  ตาม requirements
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY src /src
WORKDIR /src
CMD python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8888