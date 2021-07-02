FROM python:3.10.0b3

COPY . /app
WORKDIR /app

RUN python3 -m pip install -r requirements.txt

CMD python3 -m generate_data
