FROM python:3.12-alpine

ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG SECRET_KEY
ARG DEBUG

ENV DB_USERNAME=${DB_USERNAME}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}
ENV DB_NAME=${DB_NAME}
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=${DEBUG}

WORKDIR /pacilflix

COPY requirements.txt /pacilflix/

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /pacilflix

EXPOSE 8000

RUN python manage.py migrate

CMD ["gunicorn", "e4_pacilflix.wsgi", "--bind", "0.0.0.0:8000"]