FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

RUN pip3 install -e .

VOLUME ["/app/data"]

CMD ["python3", "-m", "chlenomer"]
