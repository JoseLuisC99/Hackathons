FROM python:latest
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./database /code/database
COPY ./server.py /code/server.py
COPY .env* /code/.env

EXPOSE 8000
CMD ["fastapi", "run", "server.py"]