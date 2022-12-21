FROM python:3.9-alpine

# RUN apt-get update && apt-get install -y software-properties-common
# RUN add-apt-repository ppa:gaod/ffmpeg5
RUN apk update
RUN apk upgrade
RUN apk add ffmpeg

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ENV PYTHONPATH /code/app

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]