FROM python:3.10.0rc1

WORKDIR /app
COPY . .

RUN python3 -m pip install -r requirements.txt

CMD ["python3", "-m", "generate_data"]
